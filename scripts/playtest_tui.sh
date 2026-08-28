#!/usr/bin/env bash
# scripts/playtest_tui.sh
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

mkdir -p artifacts
export CIVILIZATION_CLONE_DB="${CIVILIZATION_CLONE_DB:-artifacts/playtest.sqlite3}"
export CIVILIZATION_CLONE_AUTH_SECRET="${CIVILIZATION_CLONE_AUTH_SECRET:-local-playtest-secret}"
export CIVILIZATION_CLONE_HOST="127.0.0.1"
export CIVILIZATION_CLONE_PORT="${CIVILIZATION_CLONE_PORT:-8765}"

uv run civilization-clone-api >artifacts/playtest-api.log 2>&1 &
api_pid=$!
trap 'kill "$api_pid" >/dev/null 2>&1 || true' EXIT

python - <<'PY'
import time
import urllib.request

url = "http://127.0.0.1:8765/api/v1/health"
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
