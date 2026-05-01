FROM ubuntu:24.04

RUN apt update \
    && apt install -y wget \
    nano \
    curl


# install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | UV_INSTALL_DIR=/usr/bin sh

WORKDIR /nowhere

# install vllm so imports work, no inference happens here
RUN bash -c '\
  uv venv --python 3.12 --seed --managed-python \
  && source .venv/bin/activate \
  && uv pip install vllm --extra-index-url https://wheels.vllm.ai/rocm/ --upgrade'

# install utilities and wayland libs
RUN apt update \
    && apt install -y wget \
    nano \
    curl \
	libopenmpi3 \
	libopenmpi-dev \
	openmpi-bin

COPY . .

RUN bash -c '\
  source .venv/bin/activate \
  && uv pip install --no-cache-dir .'

ENV PATH=".venv/bin:$PATH"

ARG uvicorn_port="8000"
ENV UVICORN_PORT="${uvicorn_port}"

ENTRYPOINT ["/bin/sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port ${UVICORN_PORT} --log-config log_conf.yaml"]
