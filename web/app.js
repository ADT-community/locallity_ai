/* Locality AI — voice-first chat.
 * Hearing:  phone's speech recognition, or CONFIG.sttUrl (our own model).
 * Thinking: CONFIG.apiUrl, or demo mode (repeats what it heard).
 * Speaking: phone's voices, or CONFIG.ttsUrl (our own model).
 */
(() => {
  "use strict";

  const CONFIG = Object.assign({ apiUrl: "", sttUrl: "", ttsUrl: "" }, window.LOCALITY_CONFIG || {});

  const LANGS = [
    { code: "sw-KE", name: "Kiswahili" },
    { code: "en-NG", name: "English" },
    { code: "zu-ZA", name: "isiZulu" },
    { code: "xh-ZA", name: "isiXhosa" },
    { code: "af-ZA", name: "Afrikaans" },
    { code: "am-ET", name: "አማርኛ (Amharic)" },
    { code: "yo-NG", name: "Yorùbá" },
    { code: "ha-NG", name: "Hausa" },
    { code: "ig-NG", name: "Igbo" },
    { code: "rw-RW", name: "Kinyarwanda" },
    { code: "so-SO", name: "Soomaali" },
    { code: "fr-SN", name: "Français" }
  ];

  const STATUS_TEXT = {
    idle: "Tap to talk",
    listening: "Listening…",
    thinking: "Thinking…",
    speaking: "Speaking…"
  };

  const API_TIMEOUT_MS = 20000;
  const API_ERROR_TEXT = "Sorry, I couldn't reach the server. Check your connection and try again.";
  const API_TIMEOUT_TEXT = "That took too long. Check your connection and try again.";

  const $ = (s) => document.querySelector(s);
  const el = {
    lang: $("#lang"), handsfree: $("#handsfree"), mute: $("#mute"),
    history: $("#history"), welcome: $("#welcome"),
    orb: $("#orb"), status: $("#status"), caption: $("#caption"), note: $("#note"),
    typebar: $("#typebar"), textInput: $("#textInput"),
    keyboard: $("#keyboard"), mic: $("#mic"), clear: $("#clear")
  };

  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  const canBrowserHear = !!SR;
  const canBrowserSpeak = "speechSynthesis" in window;

  const state = {
    status: "idle",
    lang: "en-NG",
    messages: [],
    handsFree: false,
    muted: false,
    rec: null,            // browser SpeechRecognition
    recorder: null,       // MediaRecorder for server STT
    audio: null,          // <audio> for server TTS
    voices: [],
    turn: 0,              // increments on every new turn or interruption
    stopRequested: false
  };

  /* ---------- storage (best effort) ---------- */
  const store = {
    get(k, d) { try { const v = localStorage.getItem("locality:" + k); return v === null ? d : JSON.parse(v); } catch { return d; } },
    set(k, v) { try { localStorage.setItem("locality:" + k, JSON.stringify(v)); } catch { /* ignore */ } }
  };

  /* ---------- UI helpers ---------- */
  function setStatus(status, caption) {
    state.status = status;
    el.orb.className = "orb " + status;
    el.status.textContent = STATUS_TEXT[status];
    if (caption !== undefined) el.caption.textContent = caption;
    const active = status === "listening" || status === "speaking";
    el.mic.classList.toggle("active", active);
    el.mic.setAttribute("aria-label", status === "listening" ? "Stop listening" : status === "speaking" ? "Stop speaking and talk" : "Tap to talk");
    el.mic.disabled = status === "thinking";
  }

  function showNote(text) {
    el.note.textContent = text || "";
    el.note.hidden = !text;
  }

  function langName(code) {
    const l = LANGS.find((x) => x.code === code);
    return l ? l.name.replace(/\s*\(.*\)/, "") : code;
  }

  function addMessage(role, text, opts = {}) {
    el.welcome.hidden = true;
    const div = document.createElement("div");
    div.className = "msg " + role;
    const p = document.createElement("div");
    p.textContent = text;
    div.append(p);
    if (role === "assistant") {
      const btn = document.createElement("button");
      btn.className = "replay";
      btn.type = "button";
      btn.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 9v6h4l5 5V4L7 9H3Zm13.5 3A4.5 4.5 0 0 0 14 8v8a4.5 4.5 0 0 0 2.5-4Z"/></svg>';
      btn.append("Play again");
      btn.addEventListener("click", () => {
        stopAll();
        const turn = ++state.turn;
        speak(text).then(() => { if (turn === state.turn) setStatus("idle", ""); });
      });
      div.append(btn);
      if (opts.demo) {
        const t = document.createElement("span");
        t.className = "tag";
        t.textContent = "Demo mode: repeating what I heard";
        div.append(t);
      }
    }
    el.history.append(div);
    el.history.scrollTop = el.history.scrollHeight;
    if (role !== "system" && !opts.transient) state.messages.push({ role, content: text });
  }

  /* ---------- hearing ---------- */
  function listen() {
    stopSpeaking();
    showNote("");
    state.stopRequested = false;
    if (CONFIG.sttUrl) return recordForServer();
    if (!canBrowserHear) {
      showNote("Voice input isn't available in this browser. Try Chrome on Android, or type instead.");
      openKeyboard(true);
      return;
    }
    browserListen();
  }

  function browserListen() {
    const rec = new SR();
    rec.lang = state.lang;
    rec.interimResults = true;
    rec.continuous = false;
    rec.maxAlternatives = 1;

    let finalText = "";
    let error = null;

    rec.onspeechstart = () => el.orb.classList.add("hearing");
    rec.onspeechend = () => el.orb.classList.remove("hearing");
    rec.onresult = (e) => {
      let interim = "";
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const r = e.results[i];
        if (r.isFinal) finalText += r[0].transcript;
        else interim += r[0].transcript;
      }
      el.caption.textContent = (finalText + " " + interim).trim();
    };
    rec.onerror = (e) => { error = e.error; };
    rec.onend = () => {
      state.rec = null;
      el.orb.classList.remove("hearing");
      const text = finalText.trim();
      if (text) return handleUserText(text);
      setStatus("idle", "");
      if (error === "not-allowed" || error === "service-not-allowed") {
        showNote("Microphone access is blocked. Allow it in your browser settings, then try again.");
      } else if (error === "language-not-supported") {
        showNote(`This phone can't hear ${langName(state.lang)} yet. Try another language, or type.`);
      } else if (error === "network") {
        showNote("Voice recognition needs an internet connection.");
      } else if (error === "no-speech" || !error) {
        if (!state.stopRequested) showNote("I didn't hear anything. Tap and try again.");
      } else if (error !== "aborted") {
        showNote("Something went wrong with listening. Please try again.");
      }
    };

    try {
      rec.start();
      state.rec = rec;
      setStatus("listening", "");
    } catch {
      setStatus("idle", "");
      showNote("Couldn't start the microphone. Please try again.");
    }
  }

  async function recordForServer() {
    let stream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch {
      showNote("Microphone access is blocked. Allow it in your browser settings, then try again.");
      return;
    }
    const chunks = [];
    const rec = new MediaRecorder(stream);
    state.recorder = rec;
    rec.ondataavailable = (e) => e.data.size && chunks.push(e.data);
    rec.onstop = async () => {
      stream.getTracks().forEach((t) => t.stop());
      state.recorder = null;
      clearTimeout(limit);
      if (!chunks.length) return setStatus("idle", "");
      setStatus("thinking", "");
      try {
        const form = new FormData();
        form.append("audio", new Blob(chunks, { type: rec.mimeType }), "speech");
        form.append("lang", state.lang);
        const res = await fetch(CONFIG.sttUrl, { method: "POST", body: form });
        if (!res.ok) throw new Error(res.status);
        const { text } = await res.json();
        if (text && text.trim()) handleUserText(text.trim());
        else { setStatus("idle", ""); showNote("I didn't catch that. Tap and try again."); }
      } catch {
        setStatus("idle", "");
        showNote("Couldn't reach the speech service. Please try again.");
      }
    };
    rec.start();
    setStatus("listening", "Tap the button when you're done");
    const limit = setTimeout(() => rec.state === "recording" && rec.stop(), 30000);
  }

  function stopListening() {
    state.stopRequested = true;
    if (state.rec) state.rec.stop();
    if (state.recorder && state.recorder.state === "recording") state.recorder.stop();
  }

  /* ---------- thinking ---------- */
  async function getReply() {
    if (!CONFIG.apiUrl) {
      const last = state.messages[state.messages.length - 1];
      return { text: last ? last.content : "", demo: true };
    }
    const controller = typeof AbortController !== "undefined" ? new AbortController() : null;
    let timer;
    const timeout = new Promise((resolve) => {
      timer = setTimeout(() => {
        if (controller) controller.abort();
        resolve({ text: API_TIMEOUT_TEXT, demo: false, error: true });
      }, API_TIMEOUT_MS);
    });
    const request = (async () => {
      try {
        const res = await fetch(CONFIG.apiUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ lang: state.lang, messages: state.messages }),
          signal: controller ? controller.signal : undefined
        });
        if (!res.ok) throw new Error("HTTP " + res.status);
        const data = await res.json();
        return { text: String(data.reply || "").trim() || "…", demo: false };
      } catch {
        return { text: API_ERROR_TEXT, demo: false, error: true };
      }
    })();
    try {
      return await Promise.race([request, timeout]);
    } finally {
      clearTimeout(timer);
    }
  }

  async function handleUserText(text, { typed = false } = {}) {
    const turn = ++state.turn;
    addMessage("user", text);
    setStatus("thinking", "");
    const reply = await getReply();
    if (turn !== state.turn) return; // conversation was cleared or interrupted
    addMessage("assistant", reply.text, { demo: reply.demo, transient: reply.error });
    if (reply.error) showNote(reply.text);
    await speak(reply.text);
    if (turn !== state.turn) return; // user interrupted the reply
    if (state.handsFree && !state.muted && !typed) listen();
    else setStatus("idle", "");
  }

  /* ---------- speaking ---------- */
  function loadVoices() {
    if (!canBrowserSpeak) return;
    state.voices = speechSynthesis.getVoices();
  }

  function pickVoice(code) {
    const v = state.voices;
    const base = code.split("-")[0].toLowerCase();
    const norm = (l) => l.replace("_", "-").toLowerCase();
    return v.find((x) => norm(x.lang) === code.toLowerCase())
        || v.find((x) => norm(x.lang).split("-")[0] === base)
        || null;
  }

  function chunkText(text) {
    const parts = text.match(/[^.!?።\n]+[.!?።]*\s*/g) || [text];
    const out = [];
    let buf = "";
    for (const p of parts) {
      if ((buf + p).length > 180 && buf) { out.push(buf.trim()); buf = ""; }
      buf += p;
    }
    if (buf.trim()) out.push(buf.trim());
    return out;
  }

  function speak(text) {
    if (state.muted || !text) return Promise.resolve();
    setStatus("speaking", text);
    if (CONFIG.ttsUrl) return speakWithServer(text);
    if (!canBrowserSpeak) return Promise.resolve();

    return new Promise((resolve) => {
      speechSynthesis.cancel();
      const voice = pickVoice(state.lang);
      if (!voice) showNote(`No ${langName(state.lang)} voice on this phone yet, so I'm using the default voice.`);
      const chunks = chunkText(text);
      let left = chunks.length;
      const done = () => { if (--left <= 0) resolve(); };
      for (const c of chunks) {
        const u = new SpeechSynthesisUtterance(c);
        u.lang = state.lang;
        if (voice) u.voice = voice;
        u.rate = 1;
        u.onend = done;
        u.onerror = done;
        speechSynthesis.speak(u);
      }
    });
  }

  async function speakWithServer(text) {
    try {
      const res = await fetch(CONFIG.ttsUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, lang: state.lang })
      });
      if (!res.ok) throw new Error(res.status);
      const url = URL.createObjectURL(await res.blob());
      return await new Promise((resolve) => {
        const a = new Audio(url);
        state.audio = a;
        a.onended = a.onerror = () => { URL.revokeObjectURL(url); state.audio = null; resolve(); };
        a.play().catch(() => resolve());
      });
    } catch {
      showNote("Couldn't reach the voice service.");
    }
  }

  function stopSpeaking() {
    if (canBrowserSpeak) speechSynthesis.cancel();
    if (state.audio) { state.audio.pause(); state.audio.onended && state.audio.onended(); }
  }

  function stopAll() {
    stopListening();
    stopSpeaking();
  }

  /* ---------- controls ---------- */
  el.mic.addEventListener("click", () => {
    if (state.status === "listening") return stopListening();
    if (state.status === "speaking") { state.turn++; stopSpeaking(); }
    listen();
  });

  function openKeyboard(open) {
    el.typebar.hidden = !open;
    el.keyboard.setAttribute("aria-pressed", String(open));
    if (open) el.textInput.focus();
  }
  el.keyboard.addEventListener("click", () => openKeyboard(el.typebar.hidden));

  el.typebar.addEventListener("submit", (e) => {
    e.preventDefault();
    const text = el.textInput.value.trim();
    if (!text || state.status === "thinking") return;
    el.textInput.value = "";
    stopAll();
    handleUserText(text, { typed: true }); // typed turns don't auto-listen afterwards
  });

  el.handsfree.addEventListener("click", () => {
    state.handsFree = !state.handsFree;
    el.handsfree.setAttribute("aria-pressed", String(state.handsFree));
    store.set("handsFree", state.handsFree);
    showNote(state.handsFree ? "Conversation mode on: I'll keep listening after each reply." : "");
  });

  el.mute.addEventListener("click", () => {
    state.muted = !state.muted;
    el.mute.setAttribute("aria-pressed", String(state.muted));
    store.set("muted", state.muted);
    if (state.muted && state.status === "speaking") { state.turn++; stopSpeaking(); setStatus("idle", ""); }
  });

  el.clear.addEventListener("click", () => {
    state.turn++;
    stopAll();
    state.messages = [];
    el.history.querySelectorAll(".msg").forEach((m) => m.remove());
    el.welcome.hidden = false;
    showNote("");
    setStatus("idle", "");
  });

  el.lang.addEventListener("change", () => {
    state.lang = el.lang.value;
    store.set("lang", state.lang);
    showNote("");
  });

  /* ---------- start ---------- */
  function init() {
    for (const l of LANGS) {
      const o = document.createElement("option");
      o.value = l.code;
      o.textContent = l.name;
      el.lang.append(o);
    }
    const nav = (navigator.language || "").toLowerCase();
    const guess = LANGS.find((l) => l.code.toLowerCase() === nav) || LANGS.find((l) => l.code.split("-")[0] === nav.split("-")[0]);
    state.lang = store.get("lang", guess ? guess.code : "en-NG");
    if (!LANGS.some((l) => l.code === state.lang)) state.lang = "en-NG";
    el.lang.value = state.lang;

    state.handsFree = store.get("handsFree", false);
    state.muted = store.get("muted", false);
    el.handsfree.setAttribute("aria-pressed", String(state.handsFree));
    el.mute.setAttribute("aria-pressed", String(state.muted));

    if (canBrowserSpeak) {
      loadVoices();
      speechSynthesis.addEventListener?.("voiceschanged", loadVoices);
    }
    if (!canBrowserHear && !CONFIG.sttUrl) {
      showNote("Voice input isn't available in this browser. Try Chrome on Android, or type instead.");
      openKeyboard(true);
    }
    setStatus("idle", "");
  }

  init();
})();
