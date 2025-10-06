#!/usr/bin/env bash
set -euo pipefail
# Step: testing - create lightweight pytest tests and run them with junit output
WS="/home/kavia/workspace/code-generation/finmate-streamlit-18626-18629/StreamlitApplication"
VENV="$WS/.venv"
PYTEST_BIN="$VENV/bin/pytest"
TEST_DIR="$WS/tests"
mkdir -p "$TEST_DIR"
# Fail fast if pytest binary missing
if [ ! -x "$PYTEST_BIN" ]; then
  echo "ERROR: pytest binary not found at $PYTEST_BIN" >&2
  exit 2
fi
# test 1: syntax check (compile-only, no imports executed)
cat > "$TEST_DIR/test_app_syntax.py" <<'PY'
import py_compile
from pathlib import Path
p = Path(__file__).resolve().parents[1] / 'app' / 'app.py'
assert p.exists(), f"app.py not found at {p}"
py_compile.compile(str(p), doraise=True)
PY
# test 2: AST inspection to assert create_ui exists without importing streamlit
cat > "$TEST_DIR/test_app_api.py" <<'PY'
import ast
from pathlib import Path
p = Path(__file__).resolve().parents[1] / 'app' / 'app.py'
src = p.read_text()
mod = ast.parse(src)
fnames = [n.name for n in mod.body if isinstance(n, ast.FunctionDef)]
assert 'create_ui' in fnames, 'create_ui function not found in app.py'
PY
# Run pytest and produce junit xml for CI evidence
# -q for concise output, exit non-zero if tests fail
"$PYTEST_BIN" -q "$TEST_DIR" --junitxml="$WS/tests/junit-results.xml"
