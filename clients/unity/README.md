# CivilizationClone Unity Client

A code-bootstrapped Unity client for the CivilizationClone `/api/v1` public contract.

## Target

- Unity 6.3 LTS (project currently records `6000.3.22f1`)
- No proprietary Civilization assets or rules
- No direct imports from the Python engine
- Async/non-blocking HTTP through `UnityWebRequest` coroutines

## Features

- health check and civilization discovery;
- 2-4 player hotseat game creation/enrollment;
- civilization selection;
- fog-safe axial map rendering;
- viewer switching with stale-response suppression;
- unit selection, movement, and combat;
- settlement founding and worked-tile management;
- research selection;
- production queue/cancel;
- declare war, peace offer/accept/reject;
- end turn and concede;
- legal-action and mandatory-decision display;
- authorized event polling and event log;
- optimistic `expected_state_version` on gameplay commands.

## Open and run

Open `clients/unity` in Unity Hub using Unity 6.3 LTS. The editor bootstrap creates `Assets/Scenes/Main.unity` and adds it to Build Settings on first import. Press Play, start the CivilizationClone API separately, and connect to `http://127.0.0.1:8000`.

The runtime client also bootstraps itself into any scene, so the UI is not coupled to a hand-authored scene or prefab.

## Local verification

```bash
UNITY_BIN=/path/to/Unity bash scripts/verify_unity_client.sh
```

The project follows the repository's local-only QA policy. Runtime acceptance should use the actual rendered client and pointer/keyboard input.
