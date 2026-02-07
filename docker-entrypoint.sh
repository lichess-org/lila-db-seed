#!/bin/bash

python spamdb/spamdb.py \
    --uri=mongodb://mongodb/lichess \
    --drop-db \
    --password=password \
    --su-password=password \
    --streamers \
    --coaches \
    --tokens

mongosh \
    --host mongodb \
    lichess indexes.js
