#!/usr/bin/env bash
set -euo pipefail
WS="/home/kavia/workspace/code-generation/finmate-streamlit-18626-18629/StreamlitApplication"
cd "$WS"
# look for common entry filenames only
candidates=("app.py" "main.py" "streamlit_app.py")
found=""
for f in "${candidates[@]}"; do [ -f "$WS/$f" ] && found="$f" && break || true; done
# create placeholder only if none found and workspace writable
if [ -z "$found" ]; then
  if touch "$WS/.scaffold_write_test" >/dev/null 2>&1; then
    rm -f "$WS/.scaffold_write_test"
    cat > "$WS/app.py" <<'PY'
import streamlit as st
st.title('Placeholder App')
st.write('Replace with project app .py files mounted into the container')
PY
    found="app.py"
  else
    echo "WARN: no entrypoint found and workspace not writable; skipping placeholder creation" >&2
  fi
fi
REQ="$WS/requirements.txt"
if [ -f "$REQ" ]; then
  if ! grep -E '^[[:space:]]*streamlit==[0-9]+\.[0-9]+(\.[0-9]+)?' "$REQ" >/dev/null 2>&1; then
    if [ "${STREAMLIT_AUTO_PIN-}" = "yes" ] && [ -n "${STREAMLIT_VERSION-}" ]; then
      # append pinned streamlit
      printf "\nstreamlit==%s\n" "$STREAMLIT_VERSION" >> "$REQ"
    else
      echo "ERROR: $REQ exists but does not contain pinned streamlit==X.Y.Z. Set STREAMLIT_AUTO_PIN=yes and STREAMLIT_VERSION to auto-insert or update $REQ manually." >&2
      exit 6
    fi
  fi
else
  if [ -z "${STREAMLIT_VERSION-}" ]; then
    echo "ERROR: no requirements.txt and STREAMLIT_VERSION not provided. Set STREAMLIT_VERSION to create requirements.txt." >&2
    exit 7
  fi
  printf "streamlit==%s\n# add pandas, reportlab or fpdf if required by the app\n" "$STREAMLIT_VERSION" > "$REQ"
fi
exit 0
