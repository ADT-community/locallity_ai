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
- [ ] Simple chat app (web or mobile) on top of the API
- [ ] Knowledge base for trusted answers (start with farming and health)
- [ ] Translation layer: local language ↔ English
- [ ] Evaluation set: 100 real farmer questions with good answers, per language
- [ ] Speech-to-text prototype for one language

## Contribute

See the [website](https://adt-community.github.io) for how bounties and goals work, then pick an open issue in this repo.
