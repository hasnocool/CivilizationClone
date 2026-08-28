#!/usr/bin/env bash
# scripts/release.sh
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

printf '==> local release verification\n'
bash scripts/ci.sh

printf '==> package build\n'
mkdir -p artifacts/release
rm -f artifacts/release/*.whl artifacts/release/*.tar.gz
uv build --out-dir artifacts/release

printf '==> release artifacts\n'
find artifacts/release -maxdepth 1 -type f -print | sort
printf '==> RELEASE CANDIDATE PASS\n'
