# Use the respective Makefile to pass the appropriate BASE_IMG and build the image correctly
ARG BASE_IMG=<base>
FROM $BASE_IMG

USER root

# args - software versions
 # renovate: datasource=github-tags depName=cdr/code-server versioning=semver
ARG CODESERVER_VERSION=v4.13.0
ARG CODESERVER_PYTHON_VERSION=2022.2.1924087327
SHELL ["/bin/bash", "-c"]
# install - code-server
RUN curl -sL "https://github.com/cdr/code-server/releases/download/${CODESERVER_VERSION}/code-server_${CODESERVER_VERSION/v/}_amd64.deb" -o /tmp/code-server.deb \
 && dpkg -i /tmp/code-server.deb \
 && rm -f /tmp/code-server.deb

# install - codeserver extensions (python)
RUN curl -# -L -o /tmp/ms-python-release.vsix "https://github.com/microsoft/vscode-python/releases/download/${CODESERVER_PYTHON_VERSION}/ms-python-release.vsix" \
 && code-server --install-extension /tmp/ms-python-release.vsix \
 && code-server --list-extensions --show-versions


# Adding a layer for setup git lfs
RUN curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash && apt-get install git-lfs && git lfs install

USER $NB_UID

ENV PORT=8888
EXPOSE 8888

ENTRYPOINT ["/usr/bin/code-server", "/worker", "--bind-addr", "0.0.0.0:8888", "--disable-telemetry"]