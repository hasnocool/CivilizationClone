#!/usr/bin/env bash
# scripts/ci.sh
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

printf '==> governance\n'
required_files=(
  "PLAN.md"
  "AGENTS.md"
  "docs/WORKFLOW.md"
  ".opencode/agents/local-qa.md"
  ".opencode/agents/implementer.md"
  ".opencode/agents/reviewer.md"
)

for path in "${required_files[@]}"; do
  if [[ ! -f "$path" ]]; then
    printf 'missing required governance file: %s\n' "$path" >&2
    exit 1
  fi
done

# The repository begins documentation-first. Once pyproject.toml exists, the
# same script automatically becomes the Python quality/test gate used locally
# and in GitHub Actions.
if [[ ! -f "pyproject.toml" ]]; then
  printf '==> no pyproject.toml yet; Python checks are not applicable\n'
  printf '==> CI PASS\n'
  exit 0
fi

if ! command -v uv >/dev/null 2>&1; then
  printf 'uv is required to run Python CI checks\n' >&2
  exit 1
fi

printf '==> dependency sync\n'
if [[ -f "uv.lock" ]]; then
  uv sync --locked --all-extras --dev
else
  uv sync --all-extras --dev
fi

printf '==> formatting\n'
uv run ruff format --check .

printf '==> lint\n'
uv run ruff check .

printf '==> type checking\n'
if uv run pyright --version >/dev/null 2>&1; then
  uv run pyright
elif uv run mypy --version >/dev/null 2>&1; then
  uv run mypy src tests
else
  printf 'no configured type checker found (expected pyright or mypy)\n' >&2
  exit 1
fi

printf '==> tests\n'
uv run pytest

printf '==> CI PASS\n'
