# Same Room

Hackathon entry for the Grok Bot Community Engineering London Hackathon, 22 Oct 2026, Expedite, 7 Lyric Square, London. Event: https://luma.com/eveur09a

The product pairs two communities who are in the room and publishes a page the leads can send before they leave.

## Hard rules

- Do not invent member quotes, attendance numbers, or community bios. Public lines live in `data.js` with a source. If a source is missing, say so.
- Questions on the page are questions. They become "what members said" only when someone pastes text into the desk.
- Luma says code freeze is 21:50. Other listings say 21:15. Do not delete that warning.
- Tracks are announced in the room. The built path is the collab engine plus idea-to-live-page. Extend it; do not replace the roster with fake communities.
- Sponsor tooling is not integrated. Supabase schema is in `supabase/schema.sql`. Cognee would replace the "Memory used" citations. Zero would store the next action. Do not claim those calls exist until they do.
- The Grok key is `XAI_API_KEY`, read only by `netlify/functions/grok.ts` via `Netlify.env.get`. Keep it in a gitignored `.env` or in the Netlify environment. Never commit it, and never put it in `data.js`, HTML, or client JavaScript. The desk does not call `/api/grok`.

## Run

```bash
python3 -m http.server 4321
```

Open http://127.0.0.1:4321
