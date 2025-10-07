#!/usr/bin/env bash
set -euo pipefail
WS="/home/kavia/workspace/code-generation/finmate-streamlit-18626-18629/StreamlitApplication"
SUDO=sudo
[ "${WS}" = "/home/kavia/workspace/code-generation/finmate-streamlit-18626-18629/StreamlitApplication" ] || { echo "env-001: workspace mismatch" >&2; exit 1; }
mkdir -p "${WS}" && cd "${WS}"
TMP_VENV="/tmp/.venv_test_$$"; rm -rf "${TMP_VENV}"
if ! python3 -m venv "${TMP_VENV}" >/dev/null 2>&1; then
  if command -v apt-get >/dev/null 2>&1; then
    ${SUDO} apt-get update -qq || { echo "env-001: apt-get update failed" >&2; exit 2; }
    ${SUDO} apt-get install -y -qq python3-venv || { echo "env-001: installing python3-venv failed" >&2; exit 3; }
    rm -rf "${TMP_VENV}"
    if ! python3 -m venv "${TMP_VENV}" >/dev/null 2>&1; then
      echo "env-001: python3 -m venv failed after install" >&2; rm -rf "${TMP_VENV}" || true; exit 4
    fi
  else
    echo "env-001: python3-venv required but apt-get not available" >&2; exit 5
  fi
fi
rm -rf "${TMP_VENV}"
# create workspace venv idempotently
if [ ! -x "${WS}/.venv/bin/python" ]; then
  python3 -m venv "${WS}/.venv"
fi
VENV_PY="${WS}/.venv/bin/python"
if [ ! -x "${VENV_PY}" ]; then
  echo "env-001: venv python missing after creation" >&2; exit 6
fi
# ensure pip and core tooling
"${VENV_PY}" -m ensurepip --upgrade >/dev/null 2>&1 || true
"${VENV_PY}" -m pip install --upgrade pip setuptools wheel --quiet || { echo "env-001: pip upgrade failed" >&2; exit 7; }
# Persist STREAMLIT env vars if /etc/profile.d writable by sudo
STREAM_ENV_FILE=/etc/profile.d/streamlit_env.sh
if [ -d /etc/profile.d ] && ${SUDO} test -w /etc/profile.d >/dev/null 2>&1; then
  if ! ${SUDO} test -f "${STREAM_ENV_FILE}" >/dev/null 2>&1; then
    ${SUDO} tee "${STREAM_ENV_FILE}" >/dev/null <<EOF
# Streamlit environment persisted by env-001
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_SERVER_ENABLECORS=false
export STREAMLIT_DATA_DIR="${WS}/data"
EOF
    ${SUDO} chmod 644 "${STREAM_ENV_FILE}"
  else
    if ! ${SUDO} grep -q "STREAMLIT_SERVER_HEADLESS" "${STREAM_ENV_FILE}" >/dev/null 2>&1; then
      ${SUDO} tee -a "${STREAM_ENV_FILE}" >/dev/null <<'EOF'
# added by env-001
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_SERVER_ENABLECORS=false
EOF
    fi
    if ! ${SUDO} grep -q "STREAMLIT_DATA_DIR" "${STREAM_ENV_FILE}" >/dev/null 2>&1; then
      ${SUDO} tee -a "${STREAM_ENV_FILE}" >/dev/null <<EOF
export STREAMLIT_DATA_DIR="${WS}/data"
EOF
    fi
  fi
fi
# Export inline for this script's runtime only
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_SERVER_ENABLECORS=false
export STREAMLIT_DATA_DIR="${WS}/data"
# Optional: install tini only if operator requests via INSTALL_TINI=1; surface failures
if [ "${INSTALL_TINI:-0}" = "1" ]; then
  if command -v tini >/dev/null 2>&1; then
    :
  else
    if command -v apt-get >/dev/null 2>&1; then
      ${SUDO} apt-get update -qq || { echo "env-001: apt-get update failed (tini)" >&2; exit 8; }
      ${SUDO} apt-get install -y -qq tini || { echo "env-001: apt-get install tini failed" >&2; exit 9; }
      echo "env-001: tini installed but will not become PID 1 until container ENTRYPOINT is adjusted" >&2
    else
      echo "env-001: cannot install tini; apt-get missing" >&2
    fi
  fi
fi
# create data dir and ensure writable
mkdir -p "${WS}/data" && chmod a+rw "${WS}/data"
# verify venv python version accessible
"${VENV_PY}" -V >/dev/null
