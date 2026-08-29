#!/bin/bash -e

USER_SEED_PASSWORD="password"
if [ -n "$USER_SEED_PASSWORD" ]; then
    USER_SEED_PASSWORD="$USER_SEED_PASSWORD"
fi

PRIVILEGED_SEED_PASSWORD="password"
if [ -n "$PRIVILEGED_SEED_PASSWORD" ]; then
    PRIVILEGED_SEED_PASSWORD="$PRIVILEGED_SEED_PASSWORD"
fi

echo "Seeding Lichess database..."
echo "Using regular password:    $USER_SEED_PASSWORD"
echo "Using privileged password: $PRIVILEGED_SEED_PASSWORD"

python spamdb/spamdb.py \
    --uri=mongodb://mongodb/lichess \
    --drop-db \
    --password="$USER_SEED_PASSWORD" \
    --su-password="$PRIVILEGED_SEED_PASSWORD" \
    --streamers \
    --coaches \
    --tokens

echo "Creating indexes..."
mongosh \
    --host mongodb \
    lichess indexes.js

echo "✅ Lichess database seeded and indexes created."
