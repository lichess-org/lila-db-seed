#!/bin/bash -e

echo "Seeding Lichess database..."
python spamdb/spamdb.py \
    --uri=mongodb://mongodb/lichess \
    --drop-db \
    --password=password \
    --su-password=password \
    --streamers \
    --coaches \
    --tokens

echo "Creating indexes..."
mongosh \
    --host mongodb \
    lichess indexes.js

echo "✅ Lichess database seeded and indexes created."
