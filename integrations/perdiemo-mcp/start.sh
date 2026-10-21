#!/bin/sh
# Explicit mode selection; NEVER falls back from a failed live request to mock.
set -eu
cd "$(dirname "$0")"
case "${1:-}" in
  mock)
    export PERDIEMO_API_MODE=mock
    unset PERDIEMO_API_URL PERDIEMO_ALLOW_PRODUCTION
    echo "STARTING OFFLINE MOCK: synthetic totals are NOT statutory calculations." >&2
    ;;
  live)
    export PERDIEMO_API_MODE=live
    export PERDIEMO_API_URL=https://perdiemo-backend-production.onrender.com
    export PERDIEMO_ALLOW_PRODUCTION=true
    echo "STARTING LIVE: requests will reach PerDiemo PRODUCTION API. SYNTHETIC TEST DATA ONLY." >&2
    ;;
  staging)
    if [ -z "${2:-}" ]; then
      echo "Usage: ./start.sh staging https://your-approved-staging.example" >&2
      exit 2
    fi
    export PERDIEMO_API_MODE=live
    export PERDIEMO_API_URL="$2"
    unset PERDIEMO_ALLOW_PRODUCTION
    echo "STARTING STAGING: $PERDIEMO_API_URL" >&2
    ;;
  *)
    echo "Usage: ./start.sh mock | live | staging <backend-url>" >&2
    exit 2
    ;;
esac
exec python server.py
