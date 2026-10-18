# chat-service — Claude Code context

The real-time messaging service (WebSockets). Part of the chat system in GitHub org `jzviagin-chat-app`; the
**system design lives in chat-infra** and is kept in `.context/chat-infra/` by the SessionStart hook
(`.claude/hooks/load-design.sh`).

## System design (shared, loaded from chat-infra)
@.context/chat-infra/docs/ARCHITECTURE.md
@.context/chat-infra/docs/PLAN.md

## Current state of this repo
- `app.py` is a **placeholder**: a WebSocket echo server (`/ws`) plus `/healthz`, used to prove the
  ingress, load balancing and deploy pipeline. Deployed as `k8s/chat.yaml` in chat-infra (2 pods on workers,
  env `POD_NAME`, `NODE_NAME`, `INSTANCE`, `INSTANCE_ID`, `REDIS_URL=redis://redis:6379/0`).
- The real service is **phase 9** in PLAN.md: messaging design in PLAN.md section 4, data model in section 5.1
  and `docs/CASSANDRA.md` (chat-infra), contracts in ARCHITECTURE.md section 5.
- When it is rebuilt, use the same stack and layout as `auth-service` (Python 3.14, uv, async FastAPI,
  `src/` layout, `api/` → `services/` → `db/`, ruff + mypy strict + pytest in CI, JSON logs). Look at
  https://github.com/jzviagin-chat-app/auth-service for the conventions.

## Working with the owner
- The owner is learning Python (coming from Node.js): explain the why, with Node equivalents and trade-offs.
  **Don't guess** facts or UI; say when unsure. One step at a time; do only what was asked; explain a step
  before building it.
- `main` is protected (PRs only, admins included): work on a branch, open a PR; the owner merges.
- Commands for the owner: root-anchored (`cd "$(git rev-parse --show-toplevel)"`) and say which machine.

## Rules for this repo
- Async everywhere; never block the event loop (thousands of sockets share it).
- Only rebuildable state in Redis. Never log message contents, tokens or phone numbers.
- Retry the first Cassandra/Redis connection: new pods are blocked by the NetworkPolicy for a few seconds.
- Deploys: merging to `main` builds the image and opens a "Deploy chat-service" PR in chat-infra.

## Keeping the design current
If a change affects another service, a contract (WebSocket messages, Redis keys/channels, token use), the chat
tables, the infra or a decision in PLAN.md, update `.context/chat-infra/docs/ARCHITECTURE.md` / `PLAN.md` on a
branch there (with a change-log row) and tell the owner how to push it. Run `/sync-design` before finishing a task.
