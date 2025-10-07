#!/usr/bin/env bash
set -euo pipefail

# Validation: start Streamlit headless, probe HTTP, and stop cleanly (uses setsid)
WORKSPACE="/home/kavia/workspace/code-generation/finmate-streamlit-18626-18629/StreamlitApplication"
VENV="$WORKSPACE/.venv"
export PATH="$VENV/bin:$PATH"
cd "$WORKSPACE"
LOG_FILE="$WORKSPACE/streamlit_validation.log"
EVIDENCE="$WORKSPACE/validation_evidence.txt"
PIDFILE="$WORKSPACE/streamlit.pid"
PGIDFILE="$WORKSPACE/streamlit.pgid"

# Ensure streamlit binary exists
if [ ! -x "$VENV/bin/streamlit" ]; then
  echo "Error: streamlit binary not found at $VENV/bin/streamlit" >&2
  exit 20
fi

# Start streamlit in its own session (process group) via setsid; redirect stdout/stderr to log
STREAMLIT_CMD=("$VENV/bin/streamlit" run app.py --server.port=8501 --server.address=0.0.0.0)
# Inline env vars to guarantee headless behavior for this run
STREAM_ENV=("STREAMLIT_SERVER_HEADLESS=true" "STREAMLIT_SERVER_ENABLECORS=false")

# Start under setsid so it gets its own PGID; capture PID
setsid env "${STREAM_ENV[0]}" "${STREAM_ENV[1]}" "${STREAMLIT_CMD[@]}" >"$LOG_FILE" 2>&1 &
ST_PID=$!
# small grace before probing ps
sleep 0.2

# determine PGID of the launched process
if ps -p "$ST_PID" >/dev/null 2>&1; then
  PGID=$(ps -o pgid= -p "$ST_PID" | tr -d ' ')
else
  echo "Streamlit process did not start (no PID)" >&2
  # capture log tail for debugging
  { echo "--- streamlit log tail ---"; tail -n 200 "$LOG_FILE" 2>/dev/null || true; } >&2
  exit 10
fi

# persist pid/pgid
echo "$ST_PID" > "$PIDFILE"
echo "$PGID" > "$PGIDFILE"

# Probe HTTP up to TIMEOUT seconds
TIMEOUT=90
SECS=0
STATUS=0
URL="http://127.0.0.1:8501/"
while [ $SECS -lt $TIMEOUT ]; do
  if command -v curl >/dev/null 2>&1; then
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" -L --max-redirs 5 "$URL" || echo 0)
  elif command -v wget >/dev/null 2>&1; then
    wget -q -O /tmp/streamlit_probe.$$ "$URL" && STATUS=200 || STATUS=0
    rm -f /tmp/streamlit_probe.$$ || true
  else
    STATUS=0
  fi
  if [ "$STATUS" = "200" ] || [ "$STATUS" = "302" ] || [ "$STATUS" = "301" ]; then
    break
  fi
  sleep 1; SECS=$((SECS+1))
done

# Save evidence
printf 'streamlit_pid=%s
streamlit_pgid=%s
http_status=%s
startup_seconds=%s
log_file=%s
' "$ST_PID" "$PGID" "$STATUS" "$SECS" "$LOG_FILE" > "$EVIDENCE"

if [ "$STATUS" = "200" ] || [ "$STATUS" = "302" ] || [ "$STATUS" = "301" ]; then
  echo "Validation succeeded; server responded with $STATUS" >> "$EVIDENCE"
  # clean up: kill the exact process group
  if [ -n "$PGID" ]; then
    # send TERM to the process group (negative pgid) then KILL if necessary
    kill -TERM -"$PGID" 2>/dev/null || true
    sleep 1
    kill -KILL -"$PGID" 2>/dev/null || true
  fi
  rm -f "$PIDFILE" || true
  rm -f "$PGIDFILE" || true
  exit 0
else
  echo "Validation failed; server returned $STATUS" >> "$EVIDENCE"
  echo "--- log tail ---" >> "$EVIDENCE"
  tail -n 200 "$LOG_FILE" >> "$EVIDENCE" || true
  # attempt best-effort cleanup
  if [ -n "$PGID" ]; then
    kill -TERM -"$PGID" 2>/dev/null || true
  fi
  cat "$EVIDENCE" >&2
  exit 11
fi
