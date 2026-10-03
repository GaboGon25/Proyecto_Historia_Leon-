#!/usr/bin/env bash
set -euo pipefail
repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_dir"
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install --requirement backend/requirements.txt
backend/.venv/bin/python backend/manage.py migrate --noinput
backend/.venv/bin/python backend/manage.py seed_history
cd frontend
npm ci --cache /tmp/leon-npm-cache --no-audit --no-fund
npm run build
