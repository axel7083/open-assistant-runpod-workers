# Use the respective Makefile to pass the appropriate BASE_IMG and build the image correctly
ARG BASE_IMG=<base>
FROM $BASE_IMG

USER root

# args - software versions
 # renovate: datasource=github-tags depName=cdr/code-server versioning=semver
ARG CODESERVER_VERSION=v4.13.0
SHELL ["/bin/bash", "-c"]
# install - code-server
RUN curl -sL "https://github.com/cdr/code-server/releases/download/${CODESERVER_VERSION}/code-server_${CODESERVER_VERSION/v/}_amd64.deb" -o /tmp/code-server.deb \
 && dpkg -i /tmp/code-server.deb \
 && rm -f /tmp/code-server.deb

USER $NB_UID

ENV PORT=8888
EXPOSE 8888

ENTRYPOINT ["/usr/bin/code-server", "/worker", "--bind-addr", "0.0.0.0:8888", "--disable-telemetry"]