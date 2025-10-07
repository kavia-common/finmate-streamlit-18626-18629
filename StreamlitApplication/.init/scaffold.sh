#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="/home/kavia/workspace/code-generation/finmate-streamlit-18626-18629/StreamlitApplication"
mkdir -p "$WORKSPACE" && cd "$WORKSPACE"
cat > "$WORKSPACE/app.py" <<'PY'
import json
from pathlib import Path

def run_app():
    # local imports to keep module import safe for tests
    import streamlit as st
    import pandas as pd
    from fpdf import FPDF

    st.title('Streamlit Sample App')
    st.write('This app is import-safe; UI is created when run_app() is called.')
    df = pd.DataFrame({'a':[1,2,3],'b':[4,5,6]})
    st.dataframe(df)
    if st.button('Generate PDF'):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('helvetica', size=12)
        pdf.cell(0,10,'Sample PDF from Streamlit app', ln=True)
        out = Path('/tmp/sample_streamlit.pdf')
        pdf.output(str(out))
        st.write('PDF written to', str(out))

if __name__ == '__main__':
    run_app()
PY
cat > "$WORKSPACE/safe_import.py" <<'PY'
"""Helper to validate project imports without executing Streamlit UI"""
import json
from pathlib import Path
DATA_DIR = Path(__file__).parent / 'data'
DATA_DIR.mkdir(exist_ok=True)
DATA_FILE = DATA_DIR / 'data.json'
if not DATA_FILE.exists():
    DATA_FILE.write_text(json.dumps({'rows': []}))
PY
cat > "$WORKSPACE/requirements.txt" <<'RT'
# Minimal runtime requirements (pin versions here if reproducibility required)
streamlit
pandas
fpdf2
pytest
RT
chmod -R u+rw "$WORKSPACE"
