#!/bin/sh
set -eu
cd "$(dirname "$0")"
python -m pytest -q
python scripts_e2e_mock.py
python scripts_e2e_local.py
