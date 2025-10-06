import json, subprocess, sys

def test_imports():
    import streamlit as st
    import pandas as pd
    assert hasattr(st,'write')
    assert hasattr(pd,'DataFrame')

def test_streamlit_cli_exit_code():
    # Ensure invoking streamlit via venv python -m streamlit exits 0
    p = subprocess.run([sys.executable,'-m','streamlit','--version'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    assert p.returncode == 0

def test_json_roundtrip(tmp_path):
    p = tmp_path / 'data.json'
    data = {'ok': True}
    p.write_text(json.dumps(data))
    assert json.loads(p.read_text())['ok'] is True
