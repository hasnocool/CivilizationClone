# Unreal Client Agent Instructions

Follow repository-root `AGENTS.md`, `PLAN.md`, and `docs/API_CONTRACT.md`.

- Keep this project a presentation/transport adapter only.
- Use `/api/v1`; never call Python/domain internals.
- All HTTP work must stay asynchronous through Unreal's HTTP subsystem.
- Never log or render admin/player credentials.
- Increment viewer generation on hotseat viewer switches and ignore stale callbacks.
- Prefer code-only Slate for this POC to avoid binary asset churn.
- Run `scripts/verify_unreal_client.sh` and complete a human-style PIE/Standalone playtest before reporting PASS.
