"use strict";

const assert = require("node:assert/strict");
const test = require("node:test");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const APP_PATH = path.join(__dirname, "..", "app.js");
const SOURCE = fs.readFileSync(APP_PATH, "utf8");
const NODE_IDS = [
  "#lang", "#handsfree", "#mute", "#history", "#welcome",
  "#orb", "#status", "#caption", "#note", "#typebar",
  "#textInput", "#keyboard", "#mic", "#clear"
];

function makeElement(tag = "div") {
  const listeners = {};
  const classes = new Set();
  return {
    tagName: tag.toUpperCase(),
    children: [],
    className: "",
    textContent: "",
    innerHTML: "",
    value: "",
    hidden: false,
    disabled: false,
    scrollTop: 0,
    scrollHeight: 0,
    type: "",
    attrs: {},
    classList: {
      add: (...names) => names.forEach((name) => classes.add(name)),
      remove: (...names) => names.forEach((name) => classes.delete(name)),
      toggle: (name, force) => {
        const on = force === undefined ? !classes.has(name) : !!force;
        if (on) classes.add(name); else classes.delete(name);
        return on;
      },
      contains: (name) => classes.has(name)
    },
    setAttribute(key, value) { this.attrs[key] = String(value); },
    getAttribute(key) { return this.attrs[key]; },
    append(...nodes) { this.children.push(...nodes); },
    querySelectorAll(selector) {
      const name = selector.replace(/^\./, "");
      return this.children.filter((child) => child.className.split(/\s+/).includes(name));
    },
    addEventListener(type, handler) {
      if (!listeners[type]) listeners[type] = [];
      listeners[type].push(handler);
    },
    fire(type, event = {}) {
      for (const handler of listeners[type] || []) handler(event);
    },
    focus() {}
  };
}

function makeTimers() {
  let nextId = 1;
  const pending = new Map();
  return {
    set(fn, delay) {
      const id = nextId++;
      pending.set(id, { fn, delay });
      return id;
    },
    clear(id) { pending.delete(id); },
    advance(ms) {
      for (const [id, timer] of [...pending]) {
        if (timer.delay <= ms) {
          pending.delete(id);
          timer.fn();
        }
      }
    },
    get size() { return pending.size; }
  };
}

function boot(config, fetchImpl) {
  const timers = makeTimers();
  const nodes = {};
  for (const id of NODE_IDS) nodes[id] = makeElement();
  const storage = new Map();
  const calls = { fetch: [], aborted: [] };
  const sandbox = {
    document: {
      querySelector: (selector) => nodes[selector] || null,
      createElement: (tag) => makeElement(tag)
    },
    localStorage: {
      getItem: (key) => (storage.has(key) ? storage.get(key) : null),
      setItem: (key, value) => storage.set(key, String(value))
    },
    navigator: { language: "en-NG" },
    console,
    setTimeout: timers.set,
    clearTimeout: timers.clear,
    fetch: (url, options) => {
      calls.fetch.push({ url, options });
      return fetchImpl(url, options);
    },
    AbortController: class {
      constructor() {
        this.signal = { aborted: false };
        this.abort = () => {
          this.signal.aborted = true;
          calls.aborted.push(this.signal);
        };
      }
    }
  };
  sandbox.window = sandbox;
  sandbox.LOCALITY_CONFIG = config;
  vm.createContext(sandbox);
  vm.runInContext(SOURCE, sandbox, { filename: "app.js" });
  return { nodes, calls, timers };
}

function submit(app, text) {
  app.nodes["#textInput"].value = text;
  app.nodes["#typebar"].fire("submit", { preventDefault() {} });
}

function assistantReplies(app) {
  return app.nodes["#history"].children.filter((node) => node.className.includes("assistant"));
}

function replyText(node) {
  return node.children[0].textContent;
}

const flush = () => new Promise((resolve) => setImmediate(resolve));
const settle = async () => { await flush(); await flush(); await flush(); };

test("demo mode is unchanged when apiUrl is empty", async () => {
  const app = boot({ apiUrl: "", sttUrl: "", ttsUrl: "" }, () => {
    throw new Error("fetch must not be called in demo mode");
  });
  submit(app, "hello");
  await settle();

  assert.equal(app.calls.fetch.length, 0);
  const messages = app.nodes["#history"].children;
  assert.equal(messages.length, 2);
  assert.ok(messages[1].className.includes("assistant"));
  assert.equal(replyText(messages[1]), "hello");
  assert.ok(messages[1].children.some((child) => child.textContent.includes("Demo mode")));
  assert.equal(app.nodes["#status"].textContent, "Tap to talk");
});

test("real reply is shown and the thinking state is visible while waiting", async () => {
  const app = boot({ apiUrl: "https://api.example/chat", sttUrl: "", ttsUrl: "" },
    async () => ({ ok: true, json: async () => ({ reply: "Habari, karibu!" }) }));

  submit(app, "hello");
  assert.equal(app.nodes["#status"].textContent, "Thinking…");
  assert.equal(app.nodes["#mic"].disabled, true);
  await settle();

  assert.equal(app.calls.fetch.length, 1);
  const { url, options } = app.calls.fetch[0];
  assert.equal(url, "https://api.example/chat");
  assert.equal(options.method, "POST");
  assert.equal(options.headers["Content-Type"], "application/json");
  assert.deepEqual(JSON.parse(options.body), {
    lang: "en-NG",
    messages: [{ role: "user", content: "hello" }]
  });
  assert.ok(options.signal);
  assert.equal(replyText(assistantReplies(app)[0]), "Habari, karibu!");
  assert.equal(app.nodes["#status"].textContent, "Tap to talk");
});

test("network failure shows a friendly retry message", async () => {
  const app = boot({ apiUrl: "https://api.example/chat" }, async () => {
    throw new Error("offline");
  });
  submit(app, "hello");
  await settle();

  const text = replyText(assistantReplies(app)[0]);
  assert.match(text, /try again/i);
  assert.equal(app.nodes["#note"].textContent, text);
  assert.equal(app.nodes["#status"].textContent, "Tap to talk");
});

test("HTTP error response shows a friendly retry message", async () => {
  const app = boot({ apiUrl: "https://api.example/chat" }, async () => ({
    ok: false,
    status: 503,
    json: async () => ({})
  }));
  submit(app, "hello");
  await settle();

  assert.match(replyText(assistantReplies(app)[0]), /try again/i);
});

test("request times out after 20 s and is aborted", async () => {
  const app = boot({ apiUrl: "https://api.example/chat" }, () => new Promise(() => {}));
  submit(app, "hello");
  await flush();

  assert.equal(app.calls.aborted.length, 0);
  app.timers.advance(20000);
  await settle();

  assert.equal(app.calls.aborted.length, 1);
  const text = replyText(assistantReplies(app)[0]);
  assert.match(text, /too long/i);
  assert.match(text, /try again/i);
  assert.equal(app.nodes["#note"].textContent, text);
});

test("an error reply is not replayed to the API on the next turn", async () => {
  let attempts = 0;
  const bodies = [];
  const app = boot({ apiUrl: "https://api.example/chat" }, async (url, options) => {
    bodies.push(JSON.parse(options.body));
    attempts += 1;
    if (attempts === 1) throw new Error("offline");
    return { ok: true, json: async () => ({ reply: "working again" }) };
  });

  submit(app, "first");
  await settle();
  submit(app, "second");
  await settle();

  assert.equal(bodies.length, 2);
  assert.deepEqual(bodies[1].messages, [
    { role: "user", content: "first" },
    { role: "user", content: "second" }
  ]);
  assert.equal(replyText(assistantReplies(app)[1]), "working again");
});
