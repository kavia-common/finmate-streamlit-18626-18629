#!/usr/bin/env bash
set -euo pipefail

# dependencies step: install python deps into venv and verify streamlit version
WS="/home/kavia/workspace/code-generation/finmate-streamlit-18626-18629/StreamlitApplication"
cd "$WS"
VENV="$WS/.venv"
PYBIN="$VENV/bin/python"
UPGRADE_LOG="$WS/pip_upgrade.log"
INSTALL_LOG="$WS/pip_install.log"
INST_VERSIONS_OUT="$WS/installed_versions.txt"

if [ ! -x "$PYBIN" ]; then
  echo "ERROR: venv python missing at $PYBIN" >&2
  exit 2
fi

# upgrade pip, setuptools, wheel inside venv (non-interactive, no cache)
# capture concise logs, fail with tail of log on error
"$PYBIN" -m pip install --upgrade --no-cache-dir --disable-pip-version-check pip setuptools wheel > "$UPGRADE_LOG" 2>&1 || (
  echo "ERROR: pip upgrade failed, last 200 lines:" >&2; tail -n 200 "$UPGRADE_LOG" >&2; exit 6
)

# install from requirements.txt non-interactively
if [ -f "$WS/requirements.txt" ]; then
  "$PYBIN" -m pip install --no-cache-dir --disable-pip-version-check -r "$WS/requirements.txt" > "$INSTALL_LOG" 2>&1 || (
    echo "ERROR: pip install failed, last 200 lines:" >&2; tail -n 200 "$INSTALL_LOG" >&2; exit 7
  )
else
  echo "ERROR: requirements.txt missing at $WS" >&2
  exit 8
fi

# verify installed streamlit matches STREAMLIT_VERSION when provided
if [ -n "${STREAMLIT_VERSION-}" ]; then
  INSTVER=$("$PYBIN" -m pip show streamlit 2>/dev/null | awk -F': ' '/^Version:/{print $2}') || true
  if [ -z "${INSTVER}" ]; then
    echo "ERROR: streamlit not installed after pip install" >&2
    exit 9
  fi
  if [ "${INSTVER}" != "${STREAMLIT_VERSION}" ]; then
    echo "ERROR: installed streamlit==${INSTVER} does not match expected STREAMLIT_VERSION=${STREAMLIT_VERSION}" >&2
    exit 10
  fi
fi

# concise installed versions for diagnostics
"$PYBIN" - <<'PY' > "$INST_VERSIONS_OUT"
import importlib
pkgs = ('streamlit','pandas','reportlab','fpdf')
for pkg in pkgs:
    try:
        m = importlib.import_module(pkg)
        v = getattr(m, '__version__', None)
        if v:
            print(f"{pkg}=={v}")
        else:
            print(f"{pkg} installed (version unknown)")
    except Exception:
        print(f"{pkg} not installed")
PY

exit 0
