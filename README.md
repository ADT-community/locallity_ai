# locallity_ai — Local-language AI

An assistant that speaks African languages, by voice and text, for farmers and everyday use.

Part of the [ADT community](https://adt-community.github.io). Contributors are paid through bounties and goals.

## The problem

Most AI tools work poorly or not at all in African languages, and many people use basic phones or have expensive data. That shuts millions out of useful information.

## What we're building

- **For farmers:** weather, crop prices, pest and planting advice
- **For everyday use:** health info, help with forms, translation, general questions
- **Channels:** WhatsApp, SMS, USSD and voice calls, so it works on low-cost phones

**Start small:** 1–2 languages (for example Swahili plus one West African language) and one use case (farm advice), then expand.

## How it earns

- API access for banks, telcos, agri-businesses and NGOs
- Partnerships (e.g. input suppliers, co-ops)
- Licensing the language models and tools

## Suggested stack

- **Channels:** WhatsApp Cloud API; SMS/USSD/voice via a provider like Africa's Talking
- **Models:** open models fine-tuned on public African-language datasets; small enough to run cheaply (and offline on laptops, in the spirit of the ADT Laptop LLM Challenge)
- **Speech:** open speech-to-text and text-to-speech models for the chosen languages
- **Backend:** Python (FastAPI)

## Goals

| Goal | Done when |
|---|---|
| **G1: Text bot** | WhatsApp bot answers farm questions in one African language |
| **G2: Voice** | Users can ask by voice note and get a spoken reply |
| **G3: Pilot** | 100 farmers using it weekly through a partner |
| **G4: First revenue** | First paying API customer or partner |

## Starter tasks (bounty candidates)

- [ ] Survey open datasets and models for the first 2 languages (research bounty)
- [ ] WhatsApp bot skeleton: receive a message, reply
- [ ] Retrieval of farm advice from a curated knowledge base
- [ ] Translation layer: local language ↔ English
- [ ] Evaluation set: 100 real farmer questions with good answers, per language
- [ ] Speech-to-text prototype for one language

## Contribute

See the [website](https://adt-community.github.io) for how bounties and goals work, then pick an open issue in this repo.
