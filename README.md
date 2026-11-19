# locallity_ai — Local-language AI

An assistant that speaks African languages, by voice and text, for farmers and everyday use.

Part of the [ADT community](https://adt-community.github.io). Contributors are paid through bounties and goals.

## The problem

Most AI tools work poorly or not at all in African languages, and many people use basic phones or have expensive data. That shuts millions out of useful information.

## What we're building

A general AI assistant and language platform for Africa, not a single bot.

- **Core:** AI that understands and speaks African languages, by text and voice
- **Uses:** farming advice, health info, help with forms, translation, learning, business and everyday questions
- **Everywhere people are:** its own app and web, an API for other products, and channels like WhatsApp, SMS, USSD and voice calls for low-cost phones. Each channel is one feature on top of the same core.

**Start focused:** begin with 1–2 languages to get quality right, then add languages, uses and channels.

## Voice-first web app (`web/`)

A mobile website built to **hear and speak back**. Typing is secondary.

- Big mic button: tap to talk, tap to stop. Tap while it's speaking to interrupt.
- Live caption shows what it hears as you speak, and the orb shows listening, thinking and speaking.
- **Conversation mode** (header): keeps listening after each reply, hands-free.
- Language picker, mute, replay any answer, and a keyboard button for typing.

**Try it locally:** serve the `web/` folder (for example `npx serve web`) and open it in Chrome on Android. Microphone access needs `https` or `localhost`.

### How it plugs in

Out of the box it uses the phone's own speech recognition and voices, and runs in **demo mode**, repeating back what it heard to test hearing and speaking in each language. Set these in `web/config.js` to connect our own models (no secret keys in that file, it's public):

| Setting | Request | Response |
|---|---|---|
| `apiUrl` (the brain) | `POST { lang, messages: [{ role, content }] }` | `{ reply }` |
| `sttUrl` (hearing) | `POST` form with `audio` + `lang` | `{ text }` |
| `ttsUrl` (speaking) | `POST { text, lang }` | audio file |

Phones support some African languages better than others for built-in speech. Our own `sttUrl` and `ttsUrl` models are how we cover the rest.

## Core API (`api/`)

The core API provides the "brain" for the web app and other channels. It accepts text and a language code, and returns an answer in the same language.

### Setup

1. Install dependencies:
   ```bash
   cd api
   pip install -r requirements.txt
   ```

2. Configure environment variables:
   ```bash
   export LLM_API_URL="https://api.openai.com/v1/chat/completions"
   export LLM_API_KEY="your-api-key"
   ```

3. Run the server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

### Usage

Send a POST request to `/v1/chat` with a JSON body:

```json
{
  "lang": "sw-KE",
  "messages": [
    {"role": "user", "content": "Habari yako?"}
  ]
}
```

Response:

```json
{
  "reply": "Niko vizuri, asante. Wewe?"
}
```

### Supported Languages

- Kiswahili (sw-KE)
- English (en-NG)
- isiZulu (zu-ZA)
- isiXhosa (xh-ZA)
- Afrikaans (af-ZA)
- Amharic (am-ET)
- Yorùbá (yo-NG)
- Hausa (ha-NG)
- Igbo (ig-NG)
- Kinyarwanda (rw-RW)
- Soomaali (so-SO)
- Français (fr-SN)

### Testing

Run the test suite:

```bash
cd api
pytest
```

## How it earns

- API access for banks, telcos, agri-businesses and NGOs
- Partnerships (e.g. input suppliers, co-ops)
- Licensing the language models and tools
