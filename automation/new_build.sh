#!/usr/bin/env bash
# new_build.sh — New Build Governance Agent
#
# Interactive intake, classification, and scaffolding launcher.
# Wraps bootstrap_project.sh; does not replace it.
#
# Usage:
#   bash ~/code/Rules\ of\ Development\ and\ Deployment/automation/new_build.sh

set -euo pipefail

GOVERNANCE_HOME="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BOOTSTRAP="${GOVERNANCE_HOME}/automation/bootstrap_project.sh"
AGENTS_ROOT="${HOME}/code/agents"
APPS_ROOT="${HOME}/code/Applications"
NOW="$(date -Iseconds 2>/dev/null || date +%Y-%m-%dT%H:%M:%S%z)"
REGISTRY="${GOVERNANCE_HOME}/automation/project_registry.py"

if [[ "${1:-}" == "--version" || "${1:-}" == "-V" ]]; then
  python3 "${GOVERNANCE_HOME}/automation/version.py"
  exit 0
fi

if [[ "${1:-}" == "--check-updates" || "${1:-}" == "--update-check" ]]; then
  python3 "${GOVERNANCE_HOME}/automation/update_check.py"
  exit $?
fi

if [[ "${1:-}" == "--self-update" ]]; then
  python3 "${GOVERNANCE_HOME}/automation/self_update.py"
  exit $?
fi

# ── helpers ───────────────────────────────────────────────────────────────────

hr()  { printf '%.0s─' {1..60}; echo; }
msg() { echo "  $*"; }

ask() {
  local prompt="$1" default="${2:-}" answer
  if [[ -n "$default" ]]; then
    read -rp "  ${prompt} [${default}]: " answer || { echo; exit 1; }
    printf '%s' "${answer:-$default}"
  else
    read -rp "  ${prompt}: " answer || { echo; exit 1; }
    printf '%s' "$answer"
  fi
}

ask_choice() {
  local prompt="$1"; shift
  local choices=("$@")
  local answer valid
  while true; do
    read -rp "  ${prompt} ($(IFS=/; echo "${choices[*]}")): " answer || { echo; exit 1; }
    valid=""
    for c in "${choices[@]}"; do
      [[ "$answer" == "$c" ]] && valid=1 && break
    done
    [[ -n "$valid" ]] && break
    msg "Please enter one of: ${choices[*]}"
  done
  printf '%s' "$answer"
}

slugify() {
  printf '%s' "$1" \
    | tr '[:upper:]' '[:lower:]' \
    | tr ' _/' '-' \
    | tr -cd '[:alnum:]-' \
    | sed 's/--*/-/g; s/^-//; s/-$//'
}

# ── header ────────────────────────────────────────────────────────────────────

echo
hr
msg "New Build Governance Agent"
msg "Scope → Classify → Scaffold"
hr
echo

# ── intake ────────────────────────────────────────────────────────────────────

RAW_NAME=""
while [[ -z "$RAW_NAME" ]]; do
  RAW_NAME=$(ask "Project name")
  [[ -z "$RAW_NAME" ]] && msg "Name cannot be empty."
done

BUILD_TYPE=$(ask_choice "Build type" app agent tool other)

case "$BUILD_TYPE" in
  app)
    GOV_TYPE="application"
    TARGET_ROOT="$APPS_ROOT"
    ;;
  agent)
    GOV_TYPE="agent"
    TARGET_ROOT="$AGENTS_ROOT"
    ;;
  tool)
    GOV_TYPE="internal-tool"
    TARGET_ROOT="$APPS_ROOT"
    ;;
  other)
    echo
    msg "Supported types: website / service / internal-tool / automation / infrastructure / documentation"
    GOV_TYPE=$(ask "Governance project type")
    ROOT_CHOICE=$(ask_choice "Target root" agents applications)
    [[ "$ROOT_CHOICE" == "agents" ]] && TARGET_ROOT="$AGENTS_ROOT" || TARGET_ROOT="$APPS_ROOT"
    ;;
esac

STACK=$(ask "Expected stack" "not specified")

PRIMARY_MODEL=$(ask_choice "Primary builder" claude codex local hybrid)

msg "Governance level scale:"
msg "  0 = full autonomy"
msg "  1 = light guardrails"
msg "  2 = standard supervised"
msg "  3 = strict review"
msg "  4 = critical controls"
GOVERNANCE_LEVEL=$(ask_choice "Governance level" 0 1 2 3 4)
case "$GOVERNANCE_LEVEL" in
  0|1) RISK_TIER="low" ;;
  2) RISK_TIER="medium" ;;
  3) RISK_TIER="high" ;;
  4) RISK_TIER="critical" ;;
esac

SCOPE_NOW=$(ask_choice "Capture scope brief now?" yes no)

PROBLEM="" USER_DESC="" MVP=""
if [[ "$SCOPE_NOW" == "yes" ]]; then
  echo
  msg "Scope brief — brief answers are fine:"
  PROBLEM=$(ask  "What problem does this solve")
  USER_DESC=$(ask "Who is the primary user or consumer")
  MVP=$(ask      "What does the MVP look like")
fi

# ── derive ────────────────────────────────────────────────────────────────────

SLUG=$(slugify "$RAW_NAME")
if [[ -z "$SLUG" || ${#SLUG} -lt 2 ]]; then
  msg "Error: project name '${RAW_NAME}' produced an invalid slug '${SLUG}'."
  msg "Use ASCII letters, digits, spaces, or hyphens (minimum 2 characters)."
  exit 1
fi
RESERVED_SLUGS=("con" "prn" "aux" "nul" "com1" "com2" "com3" "com4" "com5" "com6" "com7" "com8" "com9" "lpt1" "lpt2" "lpt3" "lpt4" "lpt5" "lpt6" "lpt7" "lpt8" "lpt9")
for r in "${RESERVED_SLUGS[@]}"; do
  if [[ "${SLUG,,}" == "$r" ]]; then
    msg "Error: slug '${SLUG}' is a reserved OS name. Choose a different project name."
    exit 1
  fi
done
TARGET_DIR="${TARGET_ROOT}/${SLUG}"

# ── confirm ───────────────────────────────────────────────────────────────────

echo
hr
msg "Plan"
hr
msg "Name:        ${RAW_NAME}"
msg "Slug:        ${SLUG}"
msg "Type:        ${GOV_TYPE}"
msg "Governance:  ${GOVERNANCE_LEVEL}"
msg "Risk tier:   ${RISK_TIER}"
msg "Model:       ${PRIMARY_MODEL}"
msg "Stack:       ${STACK}"
msg "Location:    ${TARGET_DIR}"
echo

if [[ -d "$TARGET_DIR" ]]; then
  msg "WARNING: ${TARGET_DIR} already exists. Existing files will not be overwritten."
  echo
fi

CONFIRM=$(ask_choice "Create this project?" yes no)
[[ "$CONFIRM" != "yes" ]] && { msg "Aborted."; exit 0; }

# ── scaffold ──────────────────────────────────────────────────────────────────

echo
msg "Scaffolding..."
echo

bash "$BOOTSTRAP" "$TARGET_DIR" "$GOV_TYPE" "$GOVERNANCE_LEVEL"

# Extra directories not created by bootstrap_project.sh
mkdir -p \
  "${TARGET_DIR}/docs/adr" \
  "${TARGET_DIR}/docs/specs" \
  "${TARGET_DIR}/docs/runbooks" \
  "${TARGET_DIR}/archive"

echo "Created: docs/adr  docs/specs  docs/runbooks  archive"

# ── fill project-control.yaml ─────────────────────────────────────────────────

PC="${TARGET_DIR}/project-control.yaml"
if [[ -f "$PC" ]]; then
  sed -i "s/name: Project Owner/name: Adam Goodwin/" "$PC"
  sed -i "s/name: Technical Lead/name: ${PRIMARY_MODEL} session/" "$PC"
fi

# ── INITIAL_SCOPE.md ──────────────────────────────────────────────────────────

SCOPE_FILE="${TARGET_DIR}/INITIAL_SCOPE.md"

cat > "$SCOPE_FILE" <<EOF
# Initial Scope — ${RAW_NAME}

Generated: ${NOW}

## Classification

| Field          | Value             |
|----------------|-------------------|
| Project name   | ${RAW_NAME}       |
| Slug / dir     | ${SLUG}           |
| Type           | ${GOV_TYPE}       |
| Governance     | ${GOVERNANCE_LEVEL}               |
| Risk tier      | ${RISK_TIER}      |
| Stack          | ${STACK}          |
| Primary model  | ${PRIMARY_MODEL}  |
| Location       | ${TARGET_DIR}     |

## Build approach

Primary builder: **${PRIMARY_MODEL}**

EOF

if [[ -n "$PROBLEM" ]]; then
  cat >> "$SCOPE_FILE" <<EOF
## Scope brief

**Problem:** ${PROBLEM}

**Primary user / consumer:** ${USER_DESC}

**MVP:** ${MVP}

EOF
else
  cat >> "$SCOPE_FILE" <<'EOF'
## Scope brief

Not captured at intake. Fill in before the first coding session.

- **Problem:**
- **Primary user / consumer:**
- **MVP:**

EOF
fi

cat >> "$SCOPE_FILE" <<'EOF'
## First session checklist

- [ ] Read `START_HERE.md`
- [ ] Review `docs/current-build-pathway.md`
- [ ] Review `docs/standards/README.md`
- [ ] Review `docs/standards/engineering-governance-by-use-case.md`
- [ ] Review `docs/policy/durable-development-engineering-policy.md`
- [ ] Review `docs/standards/ship-ready-engineering-standard.md`
- [ ] Fill in commands in `AI_BOOTSTRAP.md`
- [ ] Confirm governance level and risk tier in `project-control.yaml`
- [ ] Add first ADR if architecture decisions were made at intake
- [ ] Run governance preflight: `bash scripts/governance-preflight.sh`
EOF

echo "Created: INITIAL_SCOPE.md"

if [[ -f "$REGISTRY" ]]; then
  python3 "$REGISTRY" register \
    --project-name "$RAW_NAME" \
    --slug "$SLUG" \
    --path "$TARGET_DIR" \
    --project-type "$GOV_TYPE" \
    --risk-tier "$RISK_TIER" \
    --governance-level "$GOVERNANCE_LEVEL" \
    --builder "$PRIMARY_MODEL" \
    --stack "$STACK" \
    --problem "$PROBLEM" \
    --user-desc "$USER_DESC" \
    --mvp "$MVP"
  echo "Registered: ${SLUG}"
fi

# ── summary ───────────────────────────────────────────────────────────────────

echo
hr
msg "Done — ${RAW_NAME}"
hr
msg "Path: ${TARGET_DIR}"
echo
msg "Files created:"
for f in README.md START_HERE.md CLAUDE.md AGENTS.md AI_BOOTSTRAP.md INITIAL_SCOPE.md project-control.yaml; do
  [[ -f "${TARGET_DIR}/${f}" ]] && msg "  ${f}"
done
echo
msg "Next:"
msg "  1. Read START_HERE.md"
msg "  2. Review docs/current-build-pathway.md"
msg "  3. Review docs/standards/README.md"
msg "  4. Review docs/standards/engineering-governance-by-use-case.md"
msg "  5. Review docs/policy/durable-development-engineering-policy.md"
msg "  6. Review docs/standards/ship-ready-engineering-standard.md"
msg "  7. Fill in commands in AI_BOOTSTRAP.md"
msg "  8. Review project-control.yaml"
msg "  9. Open: ${TARGET_DIR}"
echo
