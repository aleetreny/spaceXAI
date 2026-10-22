# Same Room

Hackathon entry for the Grok Bot Community Engineering London Hackathon, 22 Oct 2026, Expedite, 7 Lyric Square, London. Event: https://luma.com/eveur09a

The product pairs two communities who are in the room and publishes a page the leads can send before they leave.

## Hard rules

- Do not invent member quotes, attendance numbers, or community bios. Public lines live in `data.js` with a source. If a source is missing, say so.
- Questions on the page are questions. They become "what members said" only when someone pastes text into the desk.
- Luma says code freeze is 21:50. Other listings say 21:15. Do not delete that warning.
- Tracks are announced in the room. The built path is the collab engine plus idea-to-live-page. Extend it; do not replace the roster with fake communities.
- Sponsor tooling is not integrated. Supabase schema is in `supabase/schema.sql`. The planned Cognee integration builds a sourced comment graph for Grok to query; see `docs/architecture.md`. Zero is not integrated. Do not claim those calls exist until they do.

## Parallel contributors

- Before editing, read `docs/team-plan.md` and `coordination/roles.json`. Declare your role (web, data, agent, or coordination), branch, and checkout path in the chat.
- One active implementation chat per role. Each chat uses its own branch AND checkout/worktree. Never change branch in another chat's checkout or edit another checkout's files.
- Edit only your role's paths in `coordination/roles.json`. Request changes outside that scope through the owning contributor; do not fix them in your branch.
- The data contributor owns runtime setup, dependency manifests, lockfiles, migrations, API wiring and deployment. The agent contributor proposes dependencies and delivers code under `agent/`; data integrates it.
- Coordination owns shared contracts, these instructions and scope checks. Propose contract changes before implementing incompatible APIs. Use the current contract for independent work.
- Never reset, discard, commit, stash or force-push another contributor's work. Each PR targets `main` and declares its role, dependency PRs and validation.
- Run `python3 scripts/check_scope.py --base origin/main --branch YOUR_BRANCH` before opening a PR. Branch prefixes and owned paths are defined in the roles file. This checks committed, staged, unstaged and untracked files locally.
- Use separate local databases or isolated test records and separate Cognee datasets per contributor. Only data applies migrations to the shared demo database; only agent indexes the shared demo graph. No destructive tests on shared resources.

## Run

```bash
python3 -m http.server 4321
```

Open http://127.0.0.1:4321
