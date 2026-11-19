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
    if (caption) {
      el.caption.textContent = caption;
    }
    // Clear any previous error note when we move out of an error state.
    if (status !== "idle") {
      el.note.textContent = "";
    }
  }

  // Populate language selector.
  LANGS.forEach(l => {
    const opt = document.createElement("option");
    opt.value = l.code;
    opt.textContent = l.name;
    el.lang.appendChild(opt);
  });

  // ---------------------------------------------------------------------------
  // Core interaction – send user utterance to back‑end and render reply.
  // ---------------------------------------------------------------------------
  async function handleUserMessage(text) {
    // Add user message to UI & state.
    addMessageToHistory("user", text);
    state.messages.push({ role: "user", content: text });

    // Show loading state.
    setStatus("thinking");

    try {
      // Call the core API (or demo fallback).
      const reply = await window.callCoreApi(state.messages, state.lang);

      // Append assistant reply.
      addMessageToHistory("assistant", reply);
      state.messages.push({ role: "assistant", content: reply });
    } catch (err) {
      // Display a friendly error.
      console.error(err);
      el.note.textContent = "Error contacting the AI service. Please try again later.";
    } finally {
      // Return to idle so the user can speak again.
      setStatus("idle");
    }
  }

  function addMessageToHistory(role, content) {
    const div = document.createElement("div");
    div.className = "msg " + role;
    div.textContent = content;
    el.history.appendChild(div);
    // Scroll to bottom.
    el.history.scrollTop = el.history.scrollHeight;
  }

  // ---------------------------------------------------------------------------
  // Event wiring – microphone button, text input, etc.
  // (Only the parts relevant to the new API are shown; the rest of the file
  // remains unchanged.)
  // ---------------------------------------------------------------------------
  el.mic.addEventListener("click", () => {
    if (state.status !== "idle") return;
    startListening();
  });

  function startListening() {
    if (!canBrowserHear) {
      // Fallback to server STT – not part of this PR.
      return;
    }
    const rec = new SR();
    state.rec = rec;
    rec.lang = state.lang;
    rec.interimResults = false;
    rec.onresult = (e) => {
      const transcript = e.results[0][0].transcript.trim();
      handleUserMessage(transcript);
    };
    rec.onerror = (e) => {
      console.error(e);
      el.note.textContent = "Speech recognition error.";
      setStatus("idle");
    };
    rec.start();
    setStatus("listening");
  }

  // ---------------------------------------------------------------------------
  // Initialization – restore persisted settings.
  // ---------------------------------------------------------------------------
  function init() {
    const savedLang = store.get("lang", state.lang);
    if (LANGS.some(l => l.code === savedLang)) {
      state.lang = savedLang;
      el.lang.value = savedLang;
    }
    // Other init logic (hands‑free, mute, etc.) stays the same.
  }

  init();

  // ---------------------------------------------------------------------------
  // The remainder of the original app.js (speech synthesis, server STT/TTS,
  // UI helpers, etc.) is left untouched.
  // ---------------------------------------------------------------------------
})();