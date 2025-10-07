#!/usr/bin/env bash
set -euo pipefail
# Install Python dependencies into project venv and validate
WORKSPACE="/home/kavia/workspace/code-generation/finmate-streamlit-18626-18629/StreamlitApplication"
VENV="$WORKSPACE/.venv"
if [ ! -x "$VENV/bin/python" ]; then
  echo "Virtualenv not found at $VENV" >&2; exit 2
fi
export PATH="$VENV/bin:$PATH"
REQ="$WORKSPACE/requirements.txt"
PIP_LOG="$WORKSPACE/pip_install.log"
# Install from requirements file for reproducibility; capture output
$VENV/bin/pip install --upgrade --disable-pip-version-check -r "$REQ" >"$PIP_LOG" 2>&1 || (echo "pip install failed; see $PIP_LOG" >&2; sed -n '1,200p' "$PIP_LOG" >&2; exit 3)
# Validate by importing and exercising minimal functionality
LOG="$WORKSPACE/deps_validation.log"
$VENV/bin/python - <<'PY' >"$LOG" 2>&1
import sys
try:
    import streamlit
    import pandas as pd
    # choose fpdf as lightweight PDF lib check
    from fpdf import FPDF
    # exercise minimal fpdf functionality
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('helvetica', size=10)
    pdf.cell(0,5,'ok', ln=True)
    del pdf
    # check pytest is runnable
    import subprocess
    rv = subprocess.run([sys.executable, '-m', 'pytest', '--version'], capture_output=True, text=True)
    if rv.returncode != 0:
        print('pytest check failed', rv.stdout, rv.stderr)
        sys.exit(4)
except Exception as e:
    print('import/functional check failed:', e)
    sys.exit(5)
print('all_ok')
PY
# Ensure validation marker present
grep -q all_ok "$LOG" || (echo "Dependency validation failed; see $LOG" >&2 && sed -n '1,200p' "$LOG" >&2 && exit 6)
# Success
exit 0
