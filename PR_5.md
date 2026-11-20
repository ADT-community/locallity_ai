## Why

The issue asks the web app to talk to the core API when `apiUrl` is configured, instead of always echoing in demo mode. The existing client already had the basic POST call, but it had no deadline: on a slow 3G connection the UI could stay in *Thinking…* forever. It also treated failure text as part of the conversation history.

## What

- `web/app.js`: `getReply()` now races the API request against a **20 s** deadline, aborts the in-flight request with `AbortController`, and returns a friendly retry message for network/HTTP errors and a separate friendly timeout message.
- Empty `apiUrl` still returns the last transcript as a demo reply with the same "Demo mode" tag — demo mode is unchanged.
- Keeps the *Thinking…* state (and disabled mic) while the request is in flight.
- Error/timeout messages are shown in the note area and are marked transient so they are **not** sent back to the API as assistant turns on the next message.
- `README.md`: documents the timeout behaviour and the test command.
- `web/tests/api.test.js`: 6 dependency-free Node tests covering demo mode, real replies, thinking state, network/HTTP errors, the 20 s timeout + abort, and the transient-error regression.

## How to verify

```
node --check web/app.js
node --test web/tests/api.test.js
```

Test output (6/6 passing):

```
✔ demo mode is unchanged when apiUrl is empty
✔ real reply is shown and the thinking state is visible while waiting
✔ network failure shows a friendly retry message
✔ HTTP error response shows a friendly retry message
✔ request times out after 20 s and is aborted
✔ an error reply is not replayed to the API on the next turn
ℹ tests 6
ℹ pass 6
ℹ fail 0
```

Manual check on throttled 3G: set `window.LOCALITY_CONFIG.apiUrl` in `web/config.js`, serve `web/` and use Chrome DevTools → Network → Slow 3G. The orb shows *Thinking…*, the real reply is rendered, and after 20 s a stalled request is aborted with the retry message.

Closes #5
