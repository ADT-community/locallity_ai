// web/api.js
// Helper to communicate with the core AI back‑end.
// Exposes a single async function `callCoreApi(messages, lang)` that returns the assistant's reply.

(() => {
  "use strict";

  // Pull configuration from the global object – same source as app.js.
  const CONFIG = Object.assign({ apiUrl: "" }, window.LOCALITY_CONFIG || {});

  /**
   * Calls the core API.
   * @param {Array<{role:string,content:string}>} messages - Conversation history.
   * @param {string} lang - BCP‑47 language code.
   * @returns {Promise<string>} The assistant's reply.
   */
  async function callCoreApi(messages, lang) {
    if (!CONFIG.apiUrl) {
      // Demo mode – simply echo the last user message.
      const last = messages[messages.length - 1];
      return last && last.role === "user" ? last.content : "";
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 s timeout for slow connections

    try {
      const response = await fetch(CONFIG.apiUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lang, messages }),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const txt = await response.text();
        throw new Error(`API error ${response.status}: ${txt}`);
      }

      const data = await response.json();
      if (!data || typeof data.reply !== "string") {
        throw new Error("Malformed API response: missing `reply` field");
      }
      return data.reply;
    } catch (err) {
      // Re‑throw so callers can display a user‑friendly message.
      throw err;
    }
  }

  // Expose globally for app.js to import without a bundler.
  window.callCoreApi = callCoreApi;
})();
