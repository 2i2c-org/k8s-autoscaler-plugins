FROM python:3.14-bookworm

RUN apt-get update && apt-get install -y tini git curl vim && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV VCS_VERSIONING_PRETEND_VERSION="0.0.0"

RUN mkdir /opt/k8s_autoscaler_plugins
COPY pyproject.toml /opt/k8s_autoscaler_plugins
COPY LICENSE.md /opt/k8s_autoscaler_plugins
COPY README.md /opt/k8s_autoscaler_plugins
COPY src/k8s_autoscaler_plugins /opt/k8s_autoscaler_plugins/src/k8s_autoscaler_plugins

WORKDIR /opt/k8s_autoscaler_plugins
RUN python3 -m pip install ".[gcp]"
# for debugging
RUN python3 -m pip install kubernetes

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["kopf", "run", "-A", "src/k8s_autoscaler_plugins/operator.py", "--verbose"]
