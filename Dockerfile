FROM python:3.13-alpine

RUN apk add --no-cache \
    bash \
    build-base \
    npm \
    openjdk21

WORKDIR /app
COPY . /app

RUN npm install --global mongosh && \
    wget https://raw.githubusercontent.com/lichess-org/lila/refs/heads/master/bin/mongodb/indexes.js

RUN pip install --no-cache-dir -r spamdb/requirements.txt

CMD ["./docker-entrypoint.sh"]
