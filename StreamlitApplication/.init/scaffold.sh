#!/usr/bin/env bash
set -euo pipefail
WS="/home/kavia/workspace/code-generation/finmate-streamlit-18626-18629/StreamlitApplication"
FORCE=${FORCE:-0}
[ "${WS}" = "/home/kavia/workspace/code-generation/finmate-streamlit-18626-18629/StreamlitApplication" ] || { echo "scaffold-002: workspace mismatch" >&2; exit 1; }
mkdir -p "${WS}" && cd "${WS}"
# create app.py unless exists or FORCE=1
if [ ! -f "${WS}/app.py" ] || [ "${FORCE}" -eq 1 ]; then
  cat > "${WS}/app.py" <<'PY'
import os
import json
from pathlib import Path

def main():
    try:
        import streamlit as st
    except Exception:
        raise RuntimeError('streamlit not available. activate the project venv and install dependencies')
    DATA_DIR = Path(os.environ.get('STREAMLIT_DATA_DIR','./data'))
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    state_file = DATA_DIR / 'state.json'
    if not state_file.exists():
        state_file.write_text(json.dumps({'visits': 0}))
    with state_file.open() as f:
        state = json.load(f)
    state['visits'] = state.get('visits',0) + 1
    with state_file.open('w') as f:
        json.dump(state, f)
    st.title('Streamlit Application (headless-ready)')
    st.write('Visits:', state['visits'])

if __name__ == '__main__':
    main()
PY
fi
# requirements: allow optional pin via STREAMLIT_PIN env var
PIN=${STREAMLIT_PIN:-}
if [ ! -f "${WS}/requirements.txt" ] || [ "${FORCE}" -eq 1 ]; then
  if [ -n "${PIN}" ]; then
    printf '%s\n' "streamlit==${PIN}" "pytest" > "${WS}/requirements.txt"
  else
    printf '%s\n' "streamlit" "pytest" > "${WS}/requirements.txt"
  fi
fi
# writable data dir
mkdir -p "${WS}/data" && chmod a+rw "${WS}/data"
# tests
mkdir -p "${WS}/tests"
if [ ! -f "${WS}/tests/test_app.py" ] || [ "${FORCE}" -eq 1 ]; then
  cat > "${WS}/tests/test_app.py" <<'PT'
def test_placeholder():
    assert 1 == 1
PT
fi
