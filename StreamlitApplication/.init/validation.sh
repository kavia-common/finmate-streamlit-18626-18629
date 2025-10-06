#!/usr/bin/env bash
set -euo pipefail
# validation: start streamlit from venv, wait readiness, probe HTTP, then cleanly stop
WS="/home/kavia/workspace/code-generation/finmate-streamlit-18626-18629/StreamlitApplication"
VENV="$WS/.venv"
STREAMLIT="$VENV/bin/streamlit"
APP_DIR="$WS/app"
PORT=8501
LOG="$WS/streamlit_validation.log"
# ensure log file exists and is writable
mkdir -p "$WS"
: >"$LOG" || true
# ensure streamlit binary exists
[ -x "$STREAMLIT" ] || { echo "streamlit CLI missing at $STREAMLIT" >&2; exit 2; }
# portable port-in-use check: return 0 if in use, 1 if free
port_in_use() {
  if command -v ss >/dev/null 2>&1; then
    ss -ltn 2>/dev/null | awk '{print $4}' | grep -Eq ":$PORT( |$)" && return 0 || return 1
  else
    python3 - <<PY
import socket
s=socket.socket()
try:
 s.settimeout(0.5)
 s.connect(('127.0.0.1',%d))
 print(1)
except Exception:
 print(0)
finally:
 s.close()
PY
    # python prints 1/0; interpret stdout
    return 0
  fi
}
if port_in_use; then echo "port $PORT appears in use" >&2; exit 3; fi
# change to app dir
cd "$APP_DIR"
# ensure env truth for non-interactive shells as well
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_SERVER_PORT=$PORT
# start streamlit in background, capture leader PID
"$STREAMLIT" run app.py --server.headless true --server.port $PORT >"$LOG" 2>&1 &
PID=$!
# cleanup: attempt graceful shutdown of leader only; increase log retention on failure
cleanup(){ rc=$?; if ps -p "$PID" >/dev/null 2>&1; then
    kill -TERM "$PID" >/dev/null 2>&1 || true
    sleep 1
    if ps -p "$PID" >/dev/null 2>&1; then kill -KILL "$PID" >/dev/null 2>&1 || true; fi
  fi
  if [ "$rc" -ne 0 ]; then
    echo "=== STREAMLIT VALIDATION LOG (tail 200) ==="
    tail -n 200 "$LOG" || true
  fi
  exit "$rc"
}
trap cleanup EXIT
# wait for readiness up to 60s
SECS=0
READY=0
while [ $SECS -lt 60 ]; do
  if curl -sS "http://127.0.0.1:$PORT/" >/dev/null 2>&1 || curl -sS "http://127.0.0.1:$PORT/?" >/dev/null 2>&1; then READY=1; break; fi
  sleep 1; SECS=$((SECS+1))
done
if [ $READY -ne 1 ]; then echo "Streamlit did not become ready in time" >&2; exit 4; fi
# basic HTTP status check
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:$PORT/" || true)
if [ -n "$HTTP_STATUS" ] && [ "$HTTP_STATUS" -ge 200 ] && [ "$HTTP_STATUS" -lt 400 ]; then
  echo "Streamlit responded with HTTP $HTTP_STATUS"
else
  echo "Unexpected or missing HTTP response: $HTTP_STATUS" >&2; exit 5
fi
# on success, show a short log excerpt for evidence
tail -n 200 "$LOG" || true
# cleanup trap will stop the server
