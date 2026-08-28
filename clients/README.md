# CivilizationClone Clients

Every graphical client in this directory is an adapter over the same authoritative `/api/v1` boundary. Clients render authorized projections, submit validated commands, and must not import or reproduce simulation rules.

| Client | Engine | Status | Local verification |
| --- | --- | --- | --- |
| Godot | Godot 4.x | Existing playable client | `bash scripts/verify_godot_client.sh` |
| Unity | Unity 6.3 LTS | Playable code-bootstrapped client | `bash scripts/verify_unity_client.sh` |
| Unreal | Unreal Engine 5.8.x | Playable C++/Slate client | `bash scripts/verify_unreal_client.sh` |

## Shared functional surface

The Unity and Unreal clients implement the current POC lifecycle and gameplay contract:

- connect/health and civilization discovery;
- create a deterministic game;
- enroll 2-4 hotseat players and retain their opaque credentials only in memory;
- start the game through the admin credential, then discard that credential;
- switch player-authorized viewers without allowing stale requests from the prior viewer to update the screen;
- inspect fog-safe state, legal actions, mandatory decisions, and authorized events;
- move/attack/found settlements;
- work tiles and manage production;
- choose research;
- declare war and offer/accept/reject peace;
- end turns and concede.

Runtime networking must be non-blocking in every client. Final acceptance remains local and human-style: launch the real engine client and exercise the rendered controls rather than substituting direct API calls for client QA.
