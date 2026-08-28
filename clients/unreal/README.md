# CivilizationClone Unreal Engine Client

Code-only Unreal Engine client for CivilizationClone's `/api/v1` public API.

## Target

- Unreal Engine 5.8.2
- C++ + Slate UI
- `FHttpModule` async HTTP; no synchronous network waits
- Public player projections only; no engine/domain imports

## Features

- API health and civilization discovery;
- 2-4 player hotseat game creation and enrollment;
- civilization choice per player;
- fog-safe axial map display and tile selection;
- unit movement/combat and settlement founding;
- worked tiles, production queue/cancel, research;
- war and bilateral peace actions;
- end turn/concede;
- viewer switching with generation-based stale-response rejection;
- authorized event polling and legal-action display;
- optimistic `expected_state_version` command submissions.

## Run

Open `CivilizationClient.uproject` in Unreal Engine 5.8.2, build the C++ project, then Play In Editor or run Standalone Game. Start the CivilizationClone API separately and connect to `http://127.0.0.1:8000`.

The UI is created from the custom `UGameInstance`; no proprietary content or authored UMG assets are required.

## Local verification

```bash
UNREAL_ENGINE_ROOT=/path/to/UnrealEngine bash scripts/verify_unreal_client.sh
```

A final QA pass must launch the actual client and exercise pointer/keyboard interactions, per repository governance.
