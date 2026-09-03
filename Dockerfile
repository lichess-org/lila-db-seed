FROM alpine/git AS lila-indexes

RUN git clone --depth 1 --filter=blob:none --sparse https://github.com/lichess-org/lila.git /tmp/lila && \
    git -C /tmp/lila sparse-checkout set --no-cone bin/mongodb/indexes.js

FROM alpine AS supercronic

RUN apk add --no-cache curl

# https://github.com/aptible/supercronic/releases
ENV SUPERCRONIC_VERSION=v0.2.49
RUN set -eu; \
    case "$(apk --print-arch)" in \
        x86_64) SUPERCRONIC=supercronic-linux-amd64; SUPERCRONIC_SHA1SUM=e63c11a9726b775a6a11801e81af4f3fb926aa68 ;; \
        aarch64) SUPERCRONIC=supercronic-linux-arm64; SUPERCRONIC_SHA1SUM=0b6c5bb743e0b0dafed1132198c81807927ac413 ;; \
        *) echo "Unsupported architecture: $(apk --print-arch)" >&2; exit 1 ;; \
    esac; \
    curl -fsSLO "https://github.com/aptible/supercronic/releases/download/${SUPERCRONIC_VERSION}/${SUPERCRONIC}"; \
    echo "${SUPERCRONIC_SHA1SUM}  ${SUPERCRONIC}" | sha1sum -c -; \
    chmod +x "$SUPERCRONIC"; \
    mv "$SUPERCRONIC" /usr/local/bin/supercronic

FROM python:3.13-alpine

RUN apk add --no-cache \
    bash \
    build-base \
    npm \
    openjdk21

WORKDIR /app
COPY . /app
COPY --from=lila-indexes /tmp/lila/bin/mongodb/indexes.js /app/indexes.js
COPY --from=supercronic /usr/local/bin/supercronic /usr/local/bin/supercronic

RUN npm install --global mongosh@2.9.2

RUN pip install --no-cache-dir -r spamdb/requirements.txt

CMD ["./docker-entrypoint.sh"]
