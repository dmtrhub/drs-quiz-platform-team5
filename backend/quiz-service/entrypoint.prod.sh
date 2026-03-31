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

if is_seed_enabled; then
  echo "[BOOT] RUN_SEEDS_ON_BOOT enabled. Seeding quizzes, pending quizzes, and attempts..."
  python scripts/seed_quizzes.py
  python scripts/seed_pending_quizzes_realistic.py
  python scripts/seed_attempts_realistic.py
else
  echo "[BOOT] RUN_SEEDS_ON_BOOT disabled. Skipping quiz seed scripts."
fi

exec gunicorn --workers 2 --bind 0.0.0.0:5001 run:app