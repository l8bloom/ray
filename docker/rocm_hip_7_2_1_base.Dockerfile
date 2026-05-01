FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# https://rocm.docs.amd.com/projects/install-on-linux/en/latest/install/quick-start.html
RUN \
    apt update && \
    apt install -y wget && \
    wget https://repo.radeon.com/amdgpu-install/7.2.1/ubuntu/noble/amdgpu-install_7.2.1.70201-1_all.deb && \
    apt install -y ./amdgpu-install_7.2.1.70201-1_all.deb && \
    apt update && \
    apt install -y amdgpu-dkms && \
	apt install -y python3-setuptools python3-wheel && \
    apt install -y rocm
