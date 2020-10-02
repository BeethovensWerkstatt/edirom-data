###################################
# multi stage Dockerfile
# 1. build xar archives
# 3. build exist container
###################################

# 1. step

FROM openjdk:8-jdk-stretch as builder
LABEL maintainer="Daniel Röwenstrunk <roewenstrunk@uni-paderborn.de>"

RUN apt-get update && \
    apt-get install -y git ant curl unzip ruby

RUN mkdir -p /sencha && \
    mkdir -p /edition && \
    mkdir -p /edirom-online && \
    mkdir -p /xars && \
    curl -o /sencha/cmd.sh.zip http://cdn.sencha.com/cmd/6.6.0.13/no-jre/SenchaCmd-6.6.0.13-linux-amd64.sh.zip && \
    unzip -p /sencha/cmd.sh.zip > /sencha/cmd-install.sh && \
    chmod +x /sencha/cmd-install.sh && \
    /sencha/cmd-install.sh -Dall=true -q -dir /opt/Sencha/Cmd && \
    git clone https://github.com/BeethovensWerkstatt/Edirom-Online.git /edirom-online

ENV PATH /opt/Sencha/Cmd/:$PATH

WORKDIR /edirom-online

RUN sh build.sh && \
    mv build-xar/*.xar /xars/

WORKDIR /edition

COPY . .

RUN ant edition && \
    mv dist/*.xar /xars/


# 2. step

FROM stadlerpeter/existdb:latest
LABEL maintainer="Daniel Röwenstrunk <roewenstrunk@uni-paderborn.de>"

ENV EXIST_CONTEXT_PATH /
ENV EXIST_DEFAULT_APP_PATH xmldb:exist:///db/apps/EdiromOnline

COPY --from=builder /xars/*.xar /opt/exist/autodeploy/
