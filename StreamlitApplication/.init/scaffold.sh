#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="/home/kavia/workspace/code-generation/finmate-streamlit-18626-18629/StreamlitApplication"
mkdir -p "$WORKSPACE"
cd "$WORKSPACE"
# Minimal app.py (atomic JSON write, guarded reportlab import)
cat > "$WORKSPACE/app.py" <<'PY'
import streamlit as st
import json, os, tempfile
WORKDIR = os.path.dirname(__file__)
DATA_FILE = os.path.join(WORKDIR, 'data.json')
try:
    from reportlab.pdfgen import canvas
except Exception as e:
    canvas = None
    _IMPORT_ERR = str(e)
else:
    _IMPORT_ERR = None
try:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE,'r',encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {'visits':0}
except Exception:
    data = {'visits':0}
data['visits'] = data.get('visits',0)+1
fd,tmpname = tempfile.mkstemp(dir=WORKDIR)
with os.fdopen(fd,'w',encoding='utf-8') as tmp:
    json.dump(data,tmp)
    tmp.flush(); os.fsync(tmp.fileno())
os.replace(tmpname,DATA_FILE)
st.title('Minimal Streamlit App (Headless)')
st.write('Visit count:', data['visits'])
if os.environ.get('STREAMLIT_SERVER_HEADLESS','false').lower() in ('1','true'):
    if canvas is None:
        st.write('PDF library missing:', _IMPORT_ERR or 'reportlab not installed. Install with: pip install reportlab')
    else:
        pdf_path = os.path.join(WORKDIR,'sample.pdf')
        c = canvas.Canvas(pdf_path); c.drawString(100,750,f"Visit count: {data['visits']}"); c.save(); st.write('PDF saved to', pdf_path)
else:
    if st.button('Generate PDF'):
        if canvas is None:
            st.error('reportlab not available; run: pip install reportlab')
        else:
            pdf_path = os.path.join(WORKDIR,'sample.pdf')
            c = canvas.Canvas(pdf_path); c.drawString(100,750,f"Visit count: {data['visits']}"); c.save(); st.write('PDF saved to', pdf_path)
PY
# pinned requirements (venv install)
cat > "$WORKSPACE/requirements.txt" <<'REQ'
streamlit>=1.30,<2.0
pandas>=2.0,<3.0
reportlab>=4.0,<5.0
pytest>=7.0,<8.0
REQ
# .gitignore and README with note about /etc/profile.d
cat > "$WORKSPACE/.gitignore" <<'GI'
.venv/
__pycache__/
data.json
sample.pdf
GI
cat > "$WORKSPACE/README.md" <<'RM'
# Minimal Streamlit App
Run (from workspace root using the workspace venv):
  ./.venv/bin/python -m streamlit run app.py --server.headless true --server.port $PORT
Note: The setup writes STREAMLIT_SERVER_HEADLESS to /etc/profile.d (system-wide) for convenience; in ephemeral containers this is acceptable, but remove /etc/profile.d/streamlit_env.sh if undesirable. The wrapper /usr/local/bin/streamlit-run-wrapper ensures non-login processes can run streamlit in headless mode using the workspace venv.
RM
