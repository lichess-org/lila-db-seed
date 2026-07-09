FROM alpine/git AS lila-indexes
RUN git clone --depth 1 --filter=blob:none --sparse https://github.com/lichess-org/lila.git /tmp/lila && \
    git -C /tmp/lila sparse-checkout set --no-cone bin/mongodb/indexes.js

FROM python:3.13-alpine

RUN apk add --no-cache \
    bash \
    build-base \
    npm \
    openjdk21

WORKDIR /app
COPY . /app
COPY --from=lila-indexes /tmp/lila/bin/mongodb/indexes.js /app/indexes.js

RUN npm install --global mongosh

RUN pip install --no-cache-dir -r spamdb/requirements.txt

CMD ["./docker-entrypoint.sh"]
