#!/usr/bin/env bash
# scripts/playtest_tui.sh
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

mkdir -p artifacts
if [[ -z "${CIVILIZATION_CLONE_DB:-}" ]]; then
  export CIVILIZATION_CLONE_DB="artifacts/playtest-${$}.sqlite3"
  cleanup_db=1
else
  cleanup_db=0
fi
export CIVILIZATION_CLONE_AUTH_SECRET="${CIVILIZATION_CLONE_AUTH_SECRET:-local-playtest-secret}"
export CIVILIZATION_CLONE_HOST="127.0.0.1"
export CIVILIZATION_CLONE_PORT="${CIVILIZATION_CLONE_PORT:-8765}"

uv run civilization-clone-api >artifacts/playtest-api.log 2>&1 &
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

port = os.environ["CIVILIZATION_CLONE_PORT"]
url = f"http://127.0.0.1:{port}/api/v1/health"
for _ in range(100):
    try:
        with urllib.request.urlopen(url, timeout=0.25) as response:
            if response.status == 200:
                raise SystemExit(0)
    except OSError:
        time.sleep(0.05)
raise SystemExit("API did not become healthy")
PY

uv run civilization-clone-tui --url "http://127.0.0.1:${CIVILIZATION_CLONE_PORT}"
