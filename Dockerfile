# syntax=docker/dockerfile:1
FROM python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b
ENV PYTHONDONTWRITEBYTECODE=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /tmp/install
COPY requirements/runtime.lock ./runtime.lock
COPY release/dist/*.whl ./
# Optional mount for the managed workspace's HTTPS inspection CA; unused on GitHub.
RUN --mount=type=secret,id=proxy_ca \
    if [ -f /run/secrets/proxy_ca ]; then export PIP_CERT=/run/secrets/proxy_ca; fi; \
    python -m pip install --no-cache-dir --require-hashes -r runtime.lock && \
    python -m pip install --no-cache-dir --no-deps ./*.whl && \
    python -m pip check && \
    rm -rf /tmp/install
USER 65532:65532
WORKDIR /tmp
ENTRYPOINT ["gpu-budget"]

