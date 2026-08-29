#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AI_ROOT="${HOME}/AI"

echo "[1/5] Installing Python prerequisites..."
sudo apt update
sudo apt install -y python3 python3-pip python-is-python3

echo "[2/5] Creating runtime folders..."
mkdir -p "${AI_ROOT}/AIAgentCoder/IN" \
		 "${AI_ROOT}/AIAgentCoder/PROCESSING" \
		 "${AI_ROOT}/AIAgentCoder/SUCCESS" \
		 "${AI_ROOT}/AIAgentCoder/FAILURE" \
		 "${AI_ROOT}/AIAgentQA/IN" \
		 "${AI_ROOT}/AIAgentQA/PROCESSING" \
		 "${AI_ROOT}/AIAgentQA/SUCCESS" \
		 "${AI_ROOT}/AIAgentQA/FAILURE" \
		 "${AI_ROOT}/Tasks" \
		 "${AI_ROOT}/Data"

echo "[3/5] Installing Python dependencies..."
python -m pip install --upgrade pip
python -m pip install -r "${REPO_ROOT}/requirements.txt"

echo "[4/5] Running unit/integration tests..."
python -m pytest "${REPO_ROOT}/tests/unit" "${REPO_ROOT}/tests/integration" -q

echo "[5/5] Setup complete."
echo "Run coder agent: python -m src.aia_coder.agent"
echo "Run qa agent:    python -m src.aia_qa.agent"
