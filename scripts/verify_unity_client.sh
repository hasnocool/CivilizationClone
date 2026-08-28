#!/usr/bin/env bash
# scripts/verify_unity_client.sh
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"
unity_bin="${UNITY_BIN:-}"
if [[ -z "$unity_bin" ]]; then
  for candidate in Unity unity-editor unityhub; do
    if command -v "$candidate" >/dev/null 2>&1; then unity_bin="$candidate"; break; fi
  done
fi
if [[ -z "$unity_bin" ]]; then
  printf 'Unity 6.3 LTS is required. Set UNITY_BIN=/path/to/Unity.\n' >&2
  exit 1
fi
printf '==> Unity client import/compile\n'
"$unity_bin" -batchmode -nographics -quit -projectPath "$repo_root/clients/unity" -executeMethod CivilizationClone.UnityClient.Editor.ClientVerifier.Run -logFile -
printf '==> UNITY CLIENT LOCAL CHECK PASS\n'
