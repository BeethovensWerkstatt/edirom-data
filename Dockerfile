#########################
# Edirom Online mit den Daten von Beethovens Werkstatt
#
# Mehrstufiges Dockerfile nach dem Vorbild der Bargheer-Edition
# (https://github.com/Edirom/Bargheer-Edition):
# 1. Daten-XAR bauen und die XAR-Pakete von Edirom Online herunterladen
# 2. eXist-db mit allen Paketen im autodeploy-Ordner
#########################

# Die erste Stufe erzeugt nur XAR-Dateien (architekturunabhängig) und läuft
# deshalb immer auf der Plattform des bauenden Rechners.
FROM --platform=$BUILDPLATFORM eclipse-temurin:26-jre AS builder

ARG BACKEND_VERSION=1.5.0
ARG FRONTEND_VERSION=1.5.0
ARG ROASTER_VERSION=1.11.0
# Relativer Pfad: Frontend und Backend laufen in derselben eXist-db, so
# funktioniert dasselbe Image lokal und unter jeder Domain.
ARG BACKEND_URL=/apps/Edirom-Online-Backend/
ARG BACKEND_PATH=/apps/Edirom-Online-Backend
# Version des Daten-XAR, z. B. 0.3.0 (aus dem Git-Tag). Leer: Version aus
# build.xml mit Datum und Uhrzeit.
ARG VERSION=

RUN apt-get update \
    && apt-get install -y --no-install-recommends ant curl unzip zip \
    && rm -rf /var/lib/apt/lists/*

# Daten-XAR bauen
WORKDIR /opt/data-build
COPY . .
RUN if [ -n "${VERSION}" ]; then \
        ant edition -Dproject.version="${VERSION}" -DTSTAMP= ; \
    else \
        ant edition ; \
    fi

# XAR-Pakete von Edirom Online und Roaster herunterladen
WORKDIR /opt/packages
RUN curl -fsSL -O "https://github.com/Edirom/Edirom-Online-Backend/releases/download/v${BACKEND_VERSION}/Edirom-Online-Backend-${BACKEND_VERSION}.xar" \
    && curl -fsSL -O "https://github.com/Edirom/Edirom-Online-Frontend/releases/download/v${FRONTEND_VERSION}/Edirom-Online-Frontend-${FRONTEND_VERSION}.xar" \
    && curl -fsSL -O "https://exist-db.org/exist/apps/public-repo/public/roaster-${ROASTER_VERSION}.xar"

# Adresse des Backends in die config.json des Frontends eintragen
RUN unzip -o "Edirom-Online-Frontend-${FRONTEND_VERSION}.xar" "config.json" \
    && sed -i "s|\"backendURL\": \".*\"|\"backendURL\": \"${BACKEND_URL}\"|g" config.json \
    && sed -i "s|\"backendPath\": \".*\"|\"backendPath\": \"${BACKEND_PATH}\"|g" config.json \
    && cat config.json \
    && zip -q -f "Edirom-Online-Frontend-${FRONTEND_VERSION}.xar" "config.json" \
    && rm config.json


#########################
# eXist-db mit allen Paketen
#########################
FROM stadlerpeter/existdb:6

LABEL org.opencontainers.image.source="https://github.com/BeethovensWerkstatt/edirom-data"
LABEL org.opencontainers.image.description="Edirom Online mit den Daten von Beethovens Werkstatt"

# Edirom Online direkt unter / ausliefern
ENV EXIST_CONTEXT_PATH="/"
ENV EXIST_DEFAULT_APP_PATH="xmldb:exist:///db/apps/Edirom-Online-Frontend"

COPY --from=builder /opt/data-build/dist/*.xar ${EXIST_HOME}/autodeploy/
COPY --from=builder /opt/packages/*.xar ${EXIST_HOME}/autodeploy/
