#!/bin/sh
set -e

is_seed_enabled() {
  case "${RUN_SEEDS_ON_BOOT:-false}" in
    1|true|TRUE|yes|YES|on|ON)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

# Always ensure admin exists in production.
python -m scripts.seed_admin

if is_seed_enabled; then
  echo "[BOOT] RUN_SEEDS_ON_BOOT enabled. Seeding realistic users..."
  python -m scripts.seed_users_realistic
else
  echo "[BOOT] RUN_SEEDS_ON_BOOT disabled. Skipping realistic user seed."
fi

exec gunicorn --worker-class eventlet --workers 1 --bind 0.0.0.0:5000 run:app