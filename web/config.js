// Locality AI — front-end configuration.
// Leave a URL empty to use the default. Never put secret keys in this file:
// it is public. Keys belong on the server behind these endpoints.
window.LOCALITY_CONFIG = {
  // Chat brain. POST { lang, messages: [{ role, content }] } -> { reply }
  // Empty = demo mode: the app repeats back what it heard, to test hearing and speaking.
  apiUrl: "",

  // Speech-to-text. POST multipart form { audio (webm/ogg), lang } -> { text }
  // Empty = use the phone's built-in speech recognition.
  sttUrl: "",

  // Text-to-speech. POST { text, lang } -> audio file (mp3/wav/ogg)
  // Empty = use the phone's built-in voices.
  ttsUrl: ""
};
