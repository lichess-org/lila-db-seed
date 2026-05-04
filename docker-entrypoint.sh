#!/bin/bash -e

SEED_PASSWORD="password"
if [ -f /run/secrets/user_seed_password ]; then
    SEED_PASSWORD=$(cat /run/secrets/user_seed_password)
fi

echo "Seeding Lichess database..."
python spamdb/spamdb.py \
    --uri=mongodb://mongodb/lichess \
    --drop-db \
    --password="$SEED_PASSWORD" \
    --su-password="$SEED_PASSWORD" \
    --streamers \
    --coaches \
    --tokens

echo "Creating indexes..."
mongosh \
    --host mongodb \
    lichess indexes.js

echo "✅ Lichess database seeded and indexes created."
