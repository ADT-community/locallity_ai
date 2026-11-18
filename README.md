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

## How it earns

- API access for banks, telcos, agri-businesses and NGOs
- Partnerships (e.g. input suppliers, co-ops)
- Licensing the language models and tools

## Suggested stack

- **Core API:** one service that every app and channel talks to
- **Apps:** its own mobile and web app
- **Channels:** WhatsApp, SMS, USSD and voice via providers like Africa's Talking, added one by one
- **Models:** open models fine-tuned on public African-language datasets; small enough to run cheaply (and offline on laptops, in the spirit of the ADT Laptop LLM Challenge)
- **Speech:** open speech-to-text and text-to-speech models for the chosen languages
- **Backend:** Python (FastAPI)

## Goals

| Goal | Done when |
|---|---|
| **G1: Core assistant** | Answers everyday and farm questions well in one African language, through the API and a simple app |
| **G2: Voice** | Users can ask by voice note and get a spoken reply |
| **G3: Pilot** | 1,000 people using it weekly, including farmers through a partner |
| **G4: First revenue** | First paying API customer or partner |

## Starter tasks (bounty candidates)

- [ ] Survey open datasets and models for the first 2 languages (research bounty)
- [ ] Core API: take a question in a local language, return an answer
- [x] Voice-first chat web app (`web/`)
- [ ] Connect the web app to the core API (`apiUrl`)
- [ ] Test built-in speech recognition and voices per language on common Android phones, and record which work (research bounty)
- [ ] Knowledge base for trusted answers (start with farming and health)
- [ ] Translation layer: local language ↔ English
- [ ] Evaluation set: 100 real farmer questions with good answers, per language
- [ ] Speech-to-text prototype for one language

## Contribute

See the [website](https://adt-community.github.io) for how bounties and goals work, then pick an open issue in this repo.
