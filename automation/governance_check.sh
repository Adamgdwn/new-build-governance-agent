#!/usr/bin/env bash

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 /path/to/project"
  exit 1
fi

project_path="$1"
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ ! -d "${project_path}" ]]; then
  echo "Project path does not exist: ${project_path}"
  exit 1
fi

"${PYTHON:-python3}" "${repo_root}/automation/compliance_report.py" "${project_path}"
