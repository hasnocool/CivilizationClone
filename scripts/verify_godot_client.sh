#!/usr/bin/env bash
# scripts/verify_godot_client.sh
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

printf '==> Godot version\n'
"$godot_bin" --version

printf '==> project import/parse\n'
"$godot_bin" --headless --path clients/godot --editor --quit

printf '==> scene smoke test\n'
"$godot_bin" --headless --path clients/godot --script res://tests/smoke_test.gd

printf '==> GODOT CLIENT LOCAL CHECK PASS\n'
