#!/usr/bin/env bash
# scripts/playtest_godot.sh
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

godot_bin="${GODOT_BIN:-}"
if [[ -z "$godot_bin" ]]; then
  for candidate in godot godot4 godot4.7; do
    if command -v "$candidate" >/dev/null 2>&1; then
      godot_bin="$candidate"
      break
    fi
  done
fi
if [[ -z "$godot_bin" ]]; then
  printf 'Godot 4.7.x is required. Set GODOT_BIN=/path/to/godot if it is not on PATH.\n' >&2
  exit 1
fi

mkdir -p artifacts
if [[ -z "${CIVILIZATION_CLONE_DB:-}" ]]; then
  export CIVILIZATION_CLONE_DB="artifacts/godot-playtest-${$}.sqlite3"
  cleanup_db=1
else
  cleanup_db=0
fi
export CIVILIZATION_CLONE_AUTH_SECRET="${CIVILIZATION_CLONE_AUTH_SECRET:-local-godot-playtest-secret}"
export CIVILIZATION_CLONE_HOST="127.0.0.1"
export CIVILIZATION_CLONE_PORT="${CIVILIZATION_CLONE_PORT:-8000}"
export CIVILIZATION_CLONE_API_URL="http://127.0.0.1:${CIVILIZATION_CLONE_PORT}"

uv run civilization-clone-api >artifacts/godot-playtest-api.log 2>&1 &
api_pid=$!
cleanup() {
  kill "$api_pid" >/dev/null 2>&1 || true
  if [[ "$cleanup_db" -eq 1 ]]; then
    rm -f "$CIVILIZATION_CLONE_DB" "$CIVILIZATION_CLONE_DB-shm" "$CIVILIZATION_CLONE_DB-wal"
  fi
}
trap cleanup EXIT

python - <<'PY'
import os
import time
import urllib.request

url = os.environ["CIVILIZATION_CLONE_API_URL"] + "/api/v1/health"
for _ in range(100):
    try:
        with urllib.request.urlopen(url, timeout=0.25) as response:
            if response.status == 200:
                raise SystemExit(0)
    except OSError:
        time.sleep(0.05)
raise SystemExit("API did not become healthy")
PY

printf 'Godot playtest API: %s\n' "$CIVILIZATION_CLONE_API_URL"
printf 'Interact with the real client using normal mouse/keyboard input.\n'
"$godot_bin" --path clients/godot
