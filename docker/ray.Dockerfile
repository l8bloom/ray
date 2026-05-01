FROM rocm_base:7.2.1

# install utilities and wayland libs
RUN apt update \
    && apt install -y wget \
    nvtop \
    nano \
    curl \
    xz-utils \
    git \
    cmake \
    ninja-build \
    build-essential \
	libopenmpi3 \
	libopenmpi-dev \
	openmpi-bin \
	libcurl4-openssl-dev \
    libwayland-client0 \
    libwayland-server0 \
    libx11-6 \
    libxrandr2 \
    libxcb1 \
    libxcb-icccm4 \
    libxcb-randr0 \
    libxcb-util1 \
    libxcb-keysyms1 \
    libxcb-image0 \
    libxcb-xkb1 \
    libxkbcommon0 \
    libxkbcommon-x11-0

# uv
RUN curl -LsSf https://astral.sh/uv/install.sh | UV_INSTALL_DIR=/usr/bin sh

# https://docs.vllm.ai/en/latest/getting_started/installation/gpu/index.html
# vllm is heavy, isolate it
RUN bash -c '\
  uv venv --python 3.12 --seed --managed-python \
  && source .venv/bin/activate \
  && uv pip install vllm --extra-index-url https://wheels.vllm.ai/rocm/ --upgrade'

RUN bash -c '\
  source .venv/bin/activate \
  && uv pip install "ray[all]==2.55.1" --upgrade'

ENV PATH=".venv/bin:$PATH"
