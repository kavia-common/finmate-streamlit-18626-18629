# Minimal Streamlit App
Run (from workspace root using the workspace venv):
  ./.venv/bin/python -m streamlit run app.py --server.headless true --server.port $PORT
Note: The setup writes STREAMLIT_SERVER_HEADLESS to /etc/profile.d (system-wide) for convenience; in ephemeral containers this is acceptable, but remove /etc/profile.d/streamlit_env.sh if undesirable. The wrapper /usr/local/bin/streamlit-run-wrapper ensures non-login processes can run streamlit in headless mode using the workspace venv.
