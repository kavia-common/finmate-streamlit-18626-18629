#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="/home/kavia/workspace/code-generation/finmate-streamlit-18626-18629/StreamlitApplication"
cd "$WORKSPACE"
TEST_DIR="$WORKSPACE/tests"
mkdir -p "$TEST_DIR"
cat > "$TEST_DIR/test_basic.py" <<'PY'
import json, subprocess, sys

def test_imports():
    import streamlit as st
    import pandas as pd
    assert hasattr(st, 'write')
    assert hasattr(pd, 'DataFrame')

def test_streamlit_cli_exit_code():
    # Ensure invoking streamlit via venv python -m streamlit exits 0
    p = subprocess.run([sys.executable, '-m', 'streamlit', '--version'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    assert p.returncode == 0


def test_json_roundtrip(tmp_path):
    p = tmp_path / 'data.json'
    data = {'ok': True}
    p.write_text(json.dumps(data))
    assert json.loads(p.read_text())['ok'] is True
PY

# Run pytest via workspace venv pytest
if [ -x "$WORKSPACE/.venv/bin/pytest" ]; then
  exec "$WORKSPACE/.venv/bin/pytest" -q "$TEST_DIR"
else
  echo "ERROR: venv pytest not found at $WORKSPACE/.venv/bin/pytest. Ensure .venv exists and pytest is installed." >&2
  exit 2
fi
