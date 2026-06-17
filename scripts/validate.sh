#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

bash "${repo_root}/automation/governance_check.sh" "${repo_root}"
bash "${repo_root}/automation/check_required_files.sh" "${repo_root}"
python3 "${repo_root}/automation/schema_validation.py" --project "${repo_root}"

mapfile -t python_files < <(find "${repo_root}/automation" -maxdepth 1 -name '*.py' -print | sort)
if (( ${#python_files[@]} > 0 )); then
  python3 -m py_compile "${python_files[@]}"
fi

mapfile -t shell_files < <(find "${repo_root}/automation" "${repo_root}/scripts" "${repo_root}/templates/project/scripts" -name '*.sh' -print | sort)
for file in "${shell_files[@]}"; do
  bash -n "${file}"
done

mapfile -t powershell_files < <(find "${repo_root}/automation" "${repo_root}/scripts" -maxdepth 1 -name '*.ps1' -print | sort)
if (( ${#powershell_files[@]} > 0 )); then
  echo "SKIP: PowerShell syntax is validated by scripts/validate.ps1 in the Windows CI job."
fi

if python3 -c "import coverage" 2>/dev/null; then
  python3 -m coverage run --source="${repo_root}/automation" \
    -m unittest discover -s "${repo_root}/tests" -p 'test_*.py'
  python3 -m coverage report --fail-under=60
  python3 -m coverage json -q -o /tmp/_cov_nbga.json
  python3 - <<'PYEOF'
import json, sys
data = json.load(open('/tmp/_cov_nbga.json'))
targets = {'promotion_execute.py': 40, 'promotion_checks.py': 40}
failures = []
for key, fd in data['files'].items():
    base = key.rsplit('/', 1)[-1]
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
  rm -f /tmp/_cov_nbga.json
else
  echo "SKIP: coverage package not installed — running tests without coverage reporting"
  python3 -m unittest discover -s "${repo_root}/tests" -p 'test_*.py'
fi
