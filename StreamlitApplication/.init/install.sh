#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="/home/kavia/workspace/code-generation/finmate-streamlit-18626-18629/StreamlitApplication"
cd "$WORKSPACE"
# Ensure venv exists (create if missing)
PY3="$(command -v python3 || true)"
if [ -z "$PY3" ]; then echo "ERROR: python3 not found" >&2; exit 2; fi
[ -d ".venv" ] || { python3 -m venv .venv; }
VENV_PIP="$WORKSPACE/.venv/bin/pip"
VENV_PY="$WORKSPACE/.venv/bin/python"
LOG="/tmp/venv_install.log"
[ -x "$VENV_PIP" ] || { echo "ERROR: venv pip not found" >&2; exit 2; }
# Record global streamlit presence (informational)
if python3 -m pip show streamlit >/dev/null 2>&1; then
  echo "INFO: global streamlit present:" >&2
  python3 -m pip show streamlit | sed -n '1,3p' || true
fi
# Upgrade packaging tools in venv
"$VENV_PIP" install --upgrade -q pip setuptools wheel || true
# Ensure STREAMLIT_SERVER_HEADLESS visible to any subprocesses that might read it during install
export STREAMLIT_SERVER_HEADLESS=true
# Install requirements with retries; log output for diagnostics
RC=1
for attempt in 1 2 3; do
  "$VENV_PIP" install --no-cache-dir --prefer-binary -r requirements.txt >"$LOG" 2>&1 && RC=0 && break || RC=$?
  sleep $((attempt * 2))
done
if [ $RC -ne 0 ]; then
  echo "ERROR: pip install failed; see $LOG" >&2
  sed -n '1,300p' "$LOG" >&2 || true
  # Detect reportlab/native hints and suggest non-interactive apt-get installation
  if grep -iE "reportlab|freetype|libjpeg|jpeg|png|ft2build" "$LOG" >/dev/null 2>&1; then
    echo "NOTE: reportlab or its C extensions may require system libraries. To install non-interactively run:" >&2
    echo "  sudo DEBIAN_FRONTEND=noninteractive apt-get update -qq && sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq libfreetype-dev libjpeg-dev" >&2
  fi
  exit 3
fi
# Verify core imports using venv python
"$VENV_PY" - <<'PY'
import sys
for m in ('streamlit','pandas','pytest'):
    try:
        __import__(m)
    except Exception as e:
        print('IMPORT_FAIL',m,e)
        sys.exit(4)
print('IMPORTS_OK')
PY
