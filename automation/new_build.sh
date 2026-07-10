#!/usr/bin/env bash
# new_build.sh — New Build Governance Agent (POSIX launcher)
#
# Thin wrapper: collects and validates intake answers, then delegates the
# actual project creation to automation/new_build_headless.py, exactly like
# automation/new_build.ps1 does on Windows. All slug, reserved-name, and
# governance rules live in automation/project_naming.py and the headless
# entry point — this script owns none of them.

set -euo pipefail

GOVERNANCE_HOME="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AUTOMATION="${GOVERNANCE_HOME}/automation"
HEADLESS="${AUTOMATION}/new_build_headless.py"

usage() {
  cat <<'EOF'
Usage: bash automation/new_build.sh [options]

Interactive intake for a governed project. Prompts for anything not supplied
as an option, then delegates creation to automation/new_build_headless.py.

Options:
  --project-name NAME       Project name (prompted if omitted)
  --build-type TYPE         app | agent | tool | other
  --governance-type TYPE    website | service | internal-tool | automation |
                            infrastructure | documentation | application | agent
                            (only asked when build type is "other")
  --stack STACK             Expected stack (default: "not specified")
  --primary-builder NAME    claude | codex | local | hybrid
  --governance-level N      0 | 1 | 2 | 3 | 4
  --scope-problem TEXT      Scope brief: problem statement
  --scope-user TEXT         Scope brief: primary user or consumer
  --scope-mvp TEXT          Scope brief: MVP description
  --version, -V             Print the agent version and exit
  --check-updates           Check for agent updates and exit
  --self-update             Fast-forward this checkout and exit
  --help, -h                Show this help and exit
EOF
}

# ── python discovery ──────────────────────────────────────────────────────────

PYTHON=()
find_python() {
  local candidate
  for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1 \
      && "$candidate" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 8) else 1)' >/dev/null 2>&1; then
      PYTHON=("$candidate")
      return 0
    fi
  done
  if command -v py >/dev/null 2>&1 \
    && py -3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 8) else 1)' >/dev/null 2>&1; then
    PYTHON=(py -3)
    return 0
  fi
  echo "Error: unable to find Python 3.8 or newer on PATH." >&2
  return 1
}

# ── argument parsing ──────────────────────────────────────────────────────────

PROJECT_NAME=""
BUILD_TYPE=""
GOVERNANCE_TYPE=""
STACK=""
PRIMARY_BUILDER=""
GOVERNANCE_LEVEL=""
SCOPE_PROBLEM=""
SCOPE_USER=""
SCOPE_MVP=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --version|-V)
      find_python
      exec "${PYTHON[@]}" "${AUTOMATION}/version.py"
      ;;
    --check-updates|--update-check)
      find_python
      exec "${PYTHON[@]}" "${AUTOMATION}/update_check.py"
      ;;
    --self-update)
      find_python
      exec "${PYTHON[@]}" "${AUTOMATION}/self_update.py"
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    --project-name)     PROJECT_NAME="${2:?--project-name requires a value}"; shift 2 ;;
    --build-type)       BUILD_TYPE="${2:?--build-type requires a value}"; shift 2 ;;
    --governance-type)  GOVERNANCE_TYPE="${2:?--governance-type requires a value}"; shift 2 ;;
    --stack)            STACK="${2:?--stack requires a value}"; shift 2 ;;
    --primary-builder)  PRIMARY_BUILDER="${2:?--primary-builder requires a value}"; shift 2 ;;
    --governance-level) GOVERNANCE_LEVEL="${2:?--governance-level requires a value}"; shift 2 ;;
    --scope-problem)    SCOPE_PROBLEM="${2:?--scope-problem requires a value}"; shift 2 ;;
    --scope-user)       SCOPE_USER="${2:?--scope-user requires a value}"; shift 2 ;;
    --scope-mvp)        SCOPE_MVP="${2:?--scope-mvp requires a value}"; shift 2 ;;
    *)
      echo "Error: unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

find_python

# ── prompt helpers ────────────────────────────────────────────────────────────

read_required() {
  local prompt="$1" value="${2:-}"
  while [[ -z "${value// }" ]]; do
    read -rp "  ${prompt}: " value || { echo; exit 1; }
  done
  printf '%s' "$value"
}

read_choice() {
  local prompt="$1" value="$2"; shift 2
  local choices=("$@") shown choice valid
  shown="$(IFS=/; echo "${choices[*]}")"
  while true; do
    valid=""
    for choice in "${choices[@]}"; do
      [[ "$value" == "$choice" ]] && valid=1 && break
    done
    [[ -n "$valid" ]] && break
    read -rp "  ${prompt} (${shown}): " value || { echo; exit 1; }
  done
  printf '%s' "$value"
}

# ── intake (mirrors new_build.ps1) ────────────────────────────────────────────

echo
echo "New Build Governance Agent"
echo "Scope -> Classify -> Scaffold"
echo

PROJECT_NAME="$(read_required "Project name" "$PROJECT_NAME")"
BUILD_TYPE="$(read_choice "Build type" "$BUILD_TYPE" app agent tool other)"

if [[ "$BUILD_TYPE" == "other" && -z "$GOVERNANCE_TYPE" ]]; then
  echo
  echo "Supported governance types: website, service, internal-tool, automation, infrastructure, documentation"
  GOVERNANCE_TYPE="$(read_required "Governance project type" "$GOVERNANCE_TYPE")"
fi

if [[ -z "$STACK" ]]; then
  read -rp "  Expected stack [not specified]: " STACK || { echo; exit 1; }
  STACK="${STACK:-not specified}"
fi

PRIMARY_BUILDER="$(read_choice "Primary builder" "$PRIMARY_BUILDER" claude codex local hybrid)"

if [[ -z "$GOVERNANCE_LEVEL" ]]; then
  echo
  echo "Governance level scale:"
  echo "  0 = full autonomy"
  echo "  1 = light guardrails"
  echo "  2 = standard supervised"
  echo "  3 = strict review"
  echo "  4 = critical controls"
fi
GOVERNANCE_LEVEL="$(read_choice "Governance level" "$GOVERNANCE_LEVEL" 0 1 2 3 4)"

if [[ -z "$SCOPE_PROBLEM" && -z "$SCOPE_USER" && -z "$SCOPE_MVP" ]]; then
  CAPTURE_SCOPE="$(read_choice "Capture scope brief now?" "" yes no)"
  if [[ "$CAPTURE_SCOPE" == "yes" ]]; then
    SCOPE_PROBLEM="$(read_required "What problem does this solve" "$SCOPE_PROBLEM")"
    SCOPE_USER="$(read_required "Who is the primary user or consumer" "$SCOPE_USER")"
    SCOPE_MVP="$(read_required "What does the MVP look like" "$SCOPE_MVP")"
  fi
fi

# ── slug validation via the canonical naming module ───────────────────────────

SLUG="$("${PYTHON[@]}" "${AUTOMATION}/project_naming.py" slug "$PROJECT_NAME")" || exit 1

# ── plan preview (mirrors new_build.ps1; headless owns the real routing) ──────

if [[ -n "${NEW_BUILD_CODE_ROOT:-}" ]]; then
  CODE_ROOT="${NEW_BUILD_CODE_ROOT}"
else
  parent="$(cd "${GOVERNANCE_HOME}/.." && pwd)"
  parent_name="$(basename "$parent")"
  if [[ "$parent_name" == "code" || "$parent_name" == "01. Code Projects" ]]; then
    CODE_ROOT="$parent"
  else
    CODE_ROOT="${HOME}/code"
  fi
fi
if [[ "$BUILD_TYPE" == "agent" || "$GOVERNANCE_TYPE" == "agent" ]]; then
  TARGET_DIR="${CODE_ROOT}/agents/${SLUG}"
else
  TARGET_DIR="${CODE_ROOT}/Applications/${SLUG}"
fi

echo
echo "Plan"
echo "  Name:       ${PROJECT_NAME}"
echo "  Slug:       ${SLUG}"
echo "  Type:       ${BUILD_TYPE}"
echo "  Governance: ${GOVERNANCE_LEVEL}"
echo "  Builder:    ${PRIMARY_BUILDER}"
echo "  Stack:      ${STACK}"
echo "  Location:   ${TARGET_DIR}"
if [[ -d "$TARGET_DIR" ]]; then
  echo "  Warning: location already exists. Existing files will not be overwritten."
fi
CONFIRM="$(read_choice "Create this project?" "" yes no)"
if [[ "$CONFIRM" != "yes" ]]; then
  echo "Aborted."
  exit 0
fi

# ── delegate to the headless entry point ──────────────────────────────────────

PARAMS_JSON="$(
  NB_PROJECT_NAME="$PROJECT_NAME" \
  NB_BUILD_TYPE="$BUILD_TYPE" \
  NB_GOVERNANCE_TYPE="$GOVERNANCE_TYPE" \
  NB_GOVERNANCE_LEVEL="$GOVERNANCE_LEVEL" \
  NB_PRIMARY_BUILDER="$PRIMARY_BUILDER" \
  NB_STACK="$STACK" \
  NB_SCOPE_PROBLEM="$SCOPE_PROBLEM" \
  NB_SCOPE_USER="$SCOPE_USER" \
  NB_SCOPE_MVP="$SCOPE_MVP" \
  "${PYTHON[@]}" - <<'PYEOF'
import json
import os

params = {
    "project_name": os.environ.get("NB_PROJECT_NAME", ""),
    "build_type": os.environ.get("NB_BUILD_TYPE", ""),
    "governance_level": os.environ.get("NB_GOVERNANCE_LEVEL", ""),
    "primary_builder": os.environ.get("NB_PRIMARY_BUILDER", ""),
    "stack": os.environ.get("NB_STACK", ""),
    "scope_problem": os.environ.get("NB_SCOPE_PROBLEM", ""),
    "scope_user": os.environ.get("NB_SCOPE_USER", ""),
    "scope_mvp": os.environ.get("NB_SCOPE_MVP", ""),
}
governance_type = os.environ.get("NB_GOVERNANCE_TYPE", "")
if governance_type:
    params["governance_type"] = governance_type
print(json.dumps(params))
PYEOF
)"

printf '%s\n' "$PARAMS_JSON" | "${PYTHON[@]}" "$HEADLESS"
