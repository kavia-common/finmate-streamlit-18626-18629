# FinMate Streamlit Application

This project is configured to run in environments where a Python virtualenv may not be pre-created. It avoids `source venv/bin/activate` and instead uses the environment's Python to start Streamlit.

How to run locally:
1. Ensure Python 3.9+ is installed.
2. Install dependencies:
   pip install -r requirements.txt
3. Start the app:
   bash run.sh
   # The app will bind to 0.0.0.0:3000 by default.
   # Optionally override the port:
   PORT=8501 bash run.sh

Entrypoint details:
- The main Streamlit file is app/app.py.
- The app binds to 0.0.0.0 and port 3000 by default to work with preview systems.
- A Procfile is provided for platforms that auto-detect process types.
