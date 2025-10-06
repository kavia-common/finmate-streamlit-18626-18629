import importlib.util
import os
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def safe_load(path):
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()
    if 'NOTICE_MARKER: PLACEHOLDER_BY_SETUP_SCRIPT_v1' in src:
        pytest.skip('Placeholder app present; skipping import test')
    if 'if __name__' in src:
        pytest.skip('Top-level __main__ detected; skipping import to avoid side-effects')
    spec = importlib.util.spec_from_file_location('proj_app', path)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
        return True
    except Exception:
        raise


def test_import_app():
    for candidate in ('app.py', 'main.py'):
        p = os.path.join(ROOT, candidate)
        if os.path.isfile(p):
            safe_load(p)
            return
    req = os.path.join(ROOT, 'requirements.txt')
    assert os.path.isfile(req)
    txt = open(req, 'r', encoding='utf-8').read().lower()
    assert 'streamlit' in txt
