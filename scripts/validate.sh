#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

PYTHON="${PYTHON:-}"
if [[ -z "${PYTHON}" ]]; then
  for candidate in python3 python; do
    if "${candidate}" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' >/dev/null 2>&1; then
      PYTHON="${candidate}"
      break
    fi
  done
fi
if [[ -z "${PYTHON}" ]]; then
  echo "FAIL: unable to find Python 3.11+ (tried python3, python)." >&2
  exit 1
fi
export PYTHON

bash "${repo_root}/automation/governance_check.sh" "${repo_root}"
bash "${repo_root}/automation/check_required_files.sh" "${repo_root}"
"${PYTHON}" "${repo_root}/automation/schema_validation.py" --project "${repo_root}"

mapfile -t python_files < <(find "${repo_root}/automation" -maxdepth 1 -name '*.py' -print | sort)
if (( ${#python_files[@]} > 0 )); then
  "${PYTHON}" -m py_compile "${python_files[@]}"
fi

if ! "${PYTHON}" -m ruff --version >/dev/null 2>&1; then
  echo "FAIL: ruff is required by the validation gate. Install dev tools: ${PYTHON} -m pip install ruff mypy" >&2
  exit 1
fi
(cd "${repo_root}" && "${PYTHON}" -m ruff check automation tests scripts)
(cd "${repo_root}" && "${PYTHON}" -m ruff format --check automation tests)
echo "PASS: ruff lint + format"

if ! "${PYTHON}" -m mypy --version >/dev/null 2>&1; then
  echo "FAIL: mypy is required by the validation gate. Install dev tools: ${PYTHON} -m pip install ruff mypy" >&2
  exit 1
fi
(cd "${repo_root}" && "${PYTHON}" -m mypy automation)
echo "PASS: mypy"

mapfile -t shell_files < <(find "${repo_root}/automation" "${repo_root}/scripts" "${repo_root}/templates/project/scripts" -name '*.sh' -print | sort)
for file in "${shell_files[@]}"; do
  bash -n "${file}"
done
if command -v shellcheck >/dev/null 2>&1; then
  shellcheck "${shell_files[@]}"
  echo "PASS: shellcheck"
else
  echo "SKIP: shellcheck not installed locally (enforced in CI)."
fi

echo "Running secret-hygiene scan (tests/test_secret_hygiene.py)"
"${PYTHON}" -m unittest discover -s "${repo_root}/tests" -p 'test_secret_hygiene*.py'

mapfile -t powershell_files < <(find "${repo_root}/automation" "${repo_root}/scripts" -maxdepth 1 -name '*.ps1' -print | sort)
if (( ${#powershell_files[@]} > 0 )); then
  echo "SKIP: PowerShell syntax is validated by scripts/validate.ps1 in the Windows CI job."
fi

if "${PYTHON}" -c "import coverage" 2>/dev/null; then
  (
    cd "${repo_root}"
    "${PYTHON}" -m coverage run --source=automation \
      -m unittest discover -s tests -p 'test_*.py'
    # Floor comes from [tool.coverage.report] fail_under in pyproject.toml.
    "${PYTHON}" -m coverage report
    "${PYTHON}" -m coverage json -q -o _cov_nbga.json
    "${PYTHON}" - <<'PYEOF'
import json, sys
data = json.load(open('_cov_nbga.json'))
# Honest measured baselines as of 2026-07-10 (the old 40% targets never ran:
# coverage was not installed in CI). Ratchet upward as tests land (backlog B-13).
targets = {'promotion_execute.py': 25, 'promotion_checks.py': 15}
failures = []
for key, fd in data['files'].items():
    base = key.replace('\\', '/').rsplit('/', 1)[-1]
    if base in targets:
        pct = fd['summary']['percent_covered']
        threshold = targets[base]
        if pct < threshold:
            failures.append(f"  {base}: {pct:.1f}% < {threshold}% required")
if failures:
    print("COVERAGE FAIL — per-file thresholds not met:")
    print('\n'.join(failures))
    sys.exit(1)
PYEOF
    rm -f _cov_nbga.json
  )
else
  echo "SKIP: coverage package not installed — running tests without coverage reporting"
  "${PYTHON}" -m unittest discover -s "${repo_root}/tests" -p 'test_*.py'
fi
