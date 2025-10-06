#!/usr/bin/env bash
set -euo pipefail
# Dependencies installation step (pip upgrade, install requirements, lock, metadata, validation)
WS="/home/kavia/workspace/code-generation/finmate-streamlit-18626-18629/StreamlitApplication"
VENV="$WS/.venv"
PIP="$VENV/bin/pip"
PY="$VENV/bin/python"
REQ="$WS/app/requirements.txt"
META="$WS/.install-metadata.txt"
LOCK="$WS/requirements-lock.txt"
# Validate workspace and venv
[ -d "$WS" ] || { echo "workspace missing: $WS" >&2; exit 1; }
[ -f "$REQ" ] || { echo "requirements file missing: $REQ" >&2; exit 1; }
[ -x "$PIP" ] || { echo "venv pip missing: $PIP" >&2; exit 2; }
# Upgrade pip/setuptools/wheel and expose failure
if ! "$PIP" install --disable-pip-version-check --no-input --upgrade pip setuptools wheel; then
  echo "pip upgrade failed" >&2
  "$PIP" --version || true
  exit 3
fi
# Install dependencies non-interactively, fail on error (no caching to keep deterministic)
if ! "$PIP" install --disable-pip-version-check --no-input --no-cache-dir -r "$REQ"; then
  echo "pip install of requirements failed" >&2
  # try a more verbose retry to aid debugging but still fail overall
  "$PIP" install -r "$REQ" || true
  exit 4
fi
# Produce a lockfile with exact installed versions
"$PIP" freeze > "$LOCK"
# Record metadata for debugging: pip, python, streamlit version and pip freeze head
{
  echo "pip: $($PIP --version 2>/dev/null || echo unknown)";
  echo "python: $($PY --version 2>&1 || echo unknown)";
  echo -n "streamlit: "; $PY -c "import importlib,sys
try:
  m=importlib.import_module('streamlit'); print(getattr(m,'__version__','unknown'))
except Exception:
  print('not-installed')
" || true;
  echo "--requirements-lock-head--";
  head -n 50 "$LOCK" 2>/dev/null || true;
} > "$META" 2>&1 || true
# Verify executables exist
[ -x "$VENV/bin/streamlit" ] || { echo "streamlit executable missing in venv" >&2; exit 5; }
[ -x "$VENV/bin/pytest" ] || { echo "pytest executable missing in venv" >&2; exit 6; }
# Verify imports succeed (streamlit, reportlab)
# Run a short python check; any ImportError will cause exit
"$PY" - <<'PYCODE'
import importlib
required = ['streamlit','reportlab']
for m in required:
    try:
        importlib.import_module(m)
    except Exception as e:
        print(f"import check failed: {m}: {e}")
        raise
print('imports ok')
PYCODE
# Success
exit 0
