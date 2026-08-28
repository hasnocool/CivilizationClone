#!/usr/bin/env bash
# scripts/verify_unreal_client.sh
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"
engine_root="${UNREAL_ENGINE_ROOT:-}"
if [[ -z "$engine_root" ]]; then
  printf 'Unreal Engine 5.8.x source/installation root is required. Set UNREAL_ENGINE_ROOT=/path/to/UnrealEngine.\n' >&2
  exit 1
fi
uproject="$repo_root/clients/unreal/CivilizationClient.uproject"
case "$(uname -s)" in
  Linux*) build="$engine_root/Engine/Build/BatchFiles/Linux/Build.sh"; platform=Linux ;;
  Darwin*) build="$engine_root/Engine/Build/BatchFiles/Mac/Build.sh"; platform=Mac ;;
  *) printf 'On Windows run Engine/Build/BatchFiles/Build.bat CivilizationClientEditor Win64 Development "%s" -WaitMutex\n' "$uproject" >&2; exit 1 ;;
esac
if [[ ! -x "$build" ]]; then printf 'Unreal build script not found: %s\n' "$build" >&2; exit 1; fi
printf '==> Unreal C++ client build\n'
"$build" CivilizationClientEditor "$platform" Development "$uproject" -WaitMutex -NoHotReload
printf '==> UNREAL CLIENT LOCAL CHECK PASS\n'
