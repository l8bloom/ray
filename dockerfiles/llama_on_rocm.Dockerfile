FROM rocm_base:7.2.1

RUN apt update \
    && apt install -y wget \
    nvtop \
    nano \
    xz-utils \
    git \
    cmake \
    build-essential \
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

# Build llama.cpp
RUN bash -c '\
    mkdir -p /srv && cd /srv \
    && git clone "https://github.com/ggml-org/llama.cpp.git" && cd llama.cpp \
    && mkdir -p builds/vulkan \
	&& export HIP_VISIBLE_DEVICES="0" \
	&& HIPCXX="$(hipconfig -l)/clang" HIP_PATH="$(hipconfig -R)" \
	cmake -G Ninja -S . -B builds/hip -DGGML_HIP=ON -DGPU_TARGETS=gfx1100 -DCMAKE_BUILD_TYPE=Release -DGGML_HIP_ROCWMMA_FATTN=ON \
	&& time cmake --build builds/hip --config Release
