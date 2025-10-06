#!/usr/bin/env bash
set -euo pipefail
WS="/home/kavia/workspace/code-generation/finmate-streamlit-18626-18629/StreamlitApplication"
APP_DIR="$WS/app"
DATA_DIR="$APP_DIR/data"
mkdir -p "$DATA_DIR"
# Minimal import-safe app.py with lazy imports
cat > "$APP_DIR/app.py" <<'PY'
from io import BytesIO

def create_ui():
    try:
        import streamlit as st
    except Exception as e:
        raise ImportError('streamlit not available: ' + str(e))
    try:
        from reportlab.pdfgen import canvas
    except Exception as e:
        raise ImportError('reportlab not available: ' + str(e))
    st.title('Minimal Streamlit App')
    if st.button('Show sample data'):
        st.write({'hello': 'world'})
    if st.button('Generate PDF'):
        buffer = BytesIO()
        c = canvas.Canvas(buffer)
        c.drawString(100, 750, 'Sample PDF from ReportLab')
        c.showPage(); c.save(); buffer.seek(0)
        st.download_button('Download PDF', buffer, file_name='sample.pdf', mime='application/pdf')

if __name__ == '__main__':
    create_ui()
PY
# Conservative pinned requirements to avoid unbounded upgrades; rely on requirements-lock.txt for exact versions
cat > "$APP_DIR/requirements.txt" <<'REQ'
streamlit>=1.30.0,<2.0
reportlab>=4.0.0,<5.0
pytest>=7.0.0,<8.0
REQ
# sample data
cat > "$DATA_DIR/sample.json" <<'JS'
{"sample": true}
JS
# ensure ownership/permissions
sudo chown -R "$(id -u):$(id -g)" "$APP_DIR" || true
sudo chmod -R u+rwX "$APP_DIR" || true
