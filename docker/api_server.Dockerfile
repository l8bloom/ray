FROM ubuntu:24.04

RUN apt update \
    && apt install -y wget \
    nano \
    curl \
    ca-certificates \
    jq


# install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | UV_INSTALL_DIR=/usr/bin sh

WORKDIR /nowhere

# install cpu based vllm so imports work, no inference happens here
# https://docs.vllm.ai/en/latest/getting_started/installation/cpu/
RUN bash -c '\
  uv venv --python 3.12 --seed --managed-python \
  && source .venv/bin/activate \
  && export VLLM_VERSION=$(curl -s https://api.github.com/repos/vllm-project/vllm/releases/latest | jq -r .tag_name | sed 's/^v//') \
  && uv pip install https://github.com/vllm-project/vllm/releases/download/v${VLLM_VERSION}/vllm-${VLLM_VERSION}+cpu-cp38-abi3-manylinux_2_35_x86_64.whl --torch-backend cpu'

COPY . .

RUN bash -c '\
  source .venv/bin/activate \
  && uv pip install --no-cache-dir .'

ENV PATH=".venv/bin:$PATH"

ARG uvicorn_port="8000"
ENV UVICORN_PORT="${uvicorn_port}"

ENTRYPOINT ["/bin/sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port ${UVICORN_PORT} --log-config log_conf.yaml"]
