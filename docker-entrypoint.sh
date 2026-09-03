#!/bin/bash -e

/app/seed.sh

if [ -n "$SEED_CRON" ]; then
    echo "Re-seeding on schedule: $SEED_CRON"
    echo "$SEED_CRON /app/seed.sh" > /app/crontab
    exec supercronic -passthrough-logs /app/crontab
fi
