# Unity Client Agent Instructions

Read the repository-root `AGENTS.md`, `PLAN.md`, and `docs/API_CONTRACT.md` first.

- Keep all authoritative rules in the headless engine; this directory is presentation/transport only.
- Use the public `/api/v1` contract exclusively.
- Never expose admin/player tokens in logs or UI after they are issued.
- Network operations must remain asynchronous. Do not introduce synchronous HTTP, busy waits, or blocking waits on Tasks.
- Preserve hotseat privacy: increment the viewer generation on viewer changes and ignore callbacks from older generations.
- Prefer code-generated UI and deterministic layout over binary scene/prefab churn unless a later design phase explicitly adopts authored assets.
- Verify with `scripts/verify_unity_client.sh` and perform human-style Play Mode testing before declaring PASS.
