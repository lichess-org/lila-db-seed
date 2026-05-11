#!/bin/bash -e

SEED_PASSWORD="password"
if [ -f /run/secrets/user_seed_password ]; then
    SEED_PASSWORD=$(cat /run/secrets/user_seed_password)
fi

TOKENS_FLAG=""
if [ "$SEED_PASSWORD" = "password" ]; then
    TOKENS_FLAG="--tokens"
else
    TOKENS_FLAG="--tokens=$SEED_PASSWORD"
fi

echo "Seeding Lichess database..."
echo "Using password: $SEED_PASSWORD"
echo "Tokens flag: ${TOKENS_FLAG:-none}"
python spamdb/spamdb.py \
    --uri=mongodb://mongodb/lichess \
    --drop-db \
    --password="$SEED_PASSWORD" \
    --su-password="$SEED_PASSWORD" \
    --streamers \
    --coaches \
    $TOKENS_FLAG

echo "Creating indexes..."
mongosh \
    --host mongodb \
    lichess indexes.js

echo "✅ Lichess database seeded and indexes created."
