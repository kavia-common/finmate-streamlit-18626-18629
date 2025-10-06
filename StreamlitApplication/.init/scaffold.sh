#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="/home/kavia/workspace/code-generation/finmate-streamlit-18626-18629/StreamlitApplication"
mkdir -p "$WORKSPACE"
sudo chown -R "$(id -u):$(id -g)" "$WORKSPACE" || true
chmod -R u+rwX,g+rwX,o-rwx "$WORKSPACE" || true
cd "$WORKSPACE"
PLACEHOLDER_MSG="PLACEHOLDER_BY_SETUP_SCRIPT_v1"
if [ ! -f "$WORKSPACE/app.py" ] && [ ! -f "$WORKSPACE/main.py" ]; then
  cat > "$WORKSPACE/app.py" <<'PY'
# Placeholder Streamlit app - safe until dependencies are installed
# NOTICE_MARKER: PLACEHOLDER_BY_SETUP_SCRIPT_v1

def get_message():
    return 'Placeholder app created by setup script. Install dependencies and replace this file.'

if __name__ == '__main__':
    print(get_message())
PY
  printf "Created placeholder app.py with NOTICE_MARKER: %s\n" "$PLACEHOLDER_MSG" > NOTICE_PLACEHOLDER.txt
fi
REQ="$WORKSPACE/requirements.txt"
if [ ! -f "$REQ" ]; then
  touch "$REQ"
fi
awk 'BEGIN{ } {g=$0; sub(/^[ \t]+/,"",g); sub(/[ \t]+$/,"",g); if(g=="" || g~"^#") next; if(!seen[g]++){print g}}' "$REQ" > "$REQ.normalized" || true
if ! grep -Eqi '^\s*streamlit(\b|[=<>])' "$REQ.normalized"; then
  printf "streamlit\n" >> "$REQ.normalized"
fi
mv "$REQ.normalized" "$REQ"
if grep -Eri "reportlab|weasyprint" . -n --exclude-dir=.venv >/dev/null 2>&1; then
  printf "Detected references to reportlab/weasyprint. If PDF generation is required, add reportlab or weasyprint to requirements.txt with versions.\n" > NOTICE_pdf_libs.txt
fi
