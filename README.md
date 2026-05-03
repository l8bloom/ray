# Distributed Offline Batch Inference Platform

![ray](https://github.com/l8bloom/ray/blob/main/assets/images/diagram.png)

This project creates [ray-based](https://docs.ray.io/en/latest/ray-overview/getting-started.html) inference platform for offline batching.

## Overview
This platform is a high-throughput, offline batch inference system designed to deploy the **[Qwen2.5-0.5B](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct)** model at scale. Built on **KubeRay** and optimized for **AMD Radeon GPUs (7900 XTX)**, it demonstrates an approach to distributed LLM workloads.

### Key Architectural Features
*   **Engine:** Powered by **vLLM** with PagedAttention for maximum throughput.
*   **Orchestration:** Managed via **KubeRay** (RayCluster CRD) for resilient worker scaling.
*   **Hardware:** Purpose-built for **ROCm** environments.
*   **Persistence:** PostgreSQL backend to track job status, token counts, and performance metrics (TPS).


## Prerequisites
*   **OS:** Ubuntu 22.04+ (k8s nodes) with ROCm 7.2.1 drivers installed.
*   **GPU:** AMD Radeon Series (tested on 7900xtx).
*   **K8s Cluster:** v1.35+ with `kubectl`, `helm` configured([Cilium](https://cilium.io/) used for CNI).

## Setup & Deployment

The deployment is streamlined via a `Makefile` to handle the operator, hardware plugins, and local storage provisioning.

### 1. Installation

#### Kubernetes
Prepare a functional Kubernetes cluster with CNI and at least 1 node for GPGPU programming. There are plenty of [resources](https://kubernetes.io/docs/setup/) on how to do that.  
Download the [model](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct) to your GPU nodes. The model has to be installed at `/models/models--Qwen--Qwen2.5-0.5B-Instruct` on all nodes doing GPU inference.

#### Build images

Three images in total are required:
- Linux-based AMD HIP/ROCm stack
- Ray head/worker images
- Api server

`docker/build.sh` explains and automates how to build them.  
Note that the cluster's CRI will pull images from a local registry `l8bloom-frontier`, please replace it with the registry you are using. 


#### Deploy resources


```bash
# clone the project to one of the control-plane nodes
git clone https://github.com/l8bloom/ray && cd ray

# Deploys Operator, AMD Device Plugin, Storage Class, and Ray Cluster
make deploy   # installs:
              # - KubeRay operator (Helm)
              # - RayCluster
              # - AMD device plugin
              # - local-path storage
              # - application manifests
              # - services
```

Deployment may take 1-2mins depending on the Internet connection speed.  
Running `kubectl get pods` should look something like this:

![k8sPods](https://github.com/l8bloom/ray/blob/main/assets/images/k8s_pods.png)

To have Ray's UI dashboard accessible, run:  

`kubectl port-forward --address 0.0.0.0 service/raycluster-kuberay-head-svc 8265:8265 > /dev/null &`

Now the UI can be rendered in a broswer(e.g. `http://192.168.1.100:8265/#/cluster`)

![rayUI](https://github.com/l8bloom/ray/blob/main/assets/images/ray_dashboard.png)

### 2. Infrastructure Components Explanation
*   **KubeRay Operator:** Orchestrates the lifecycle of the Ray head and worker nodes.
*   **RayCluster:** Services for distributing computation tasks across the cluster.
*   **AMD Device Plugin:** Exposes AMD GPUs to the Kubernetes scheduler.
*   **Local Path Provisioner:** Provides CSI solution for the cluster. The database data is kept on a node even if the whole cluster is removed.
*   **Python uvicorn driver:** Acts as the entry point for submitting asynchronous batch jobs.


## Usage

### API Specification
The platform accepts JSON batches. It automatically maps requests to the **ChatML** format and persists metrics to the database.

`api-server` is a `NodePort` service which exposes the API for offline batching on the `31313` port, accessible from any node in your k8s cluster.

**Submit a Batch Job:**
```bash
curl -X 'POST' \
  'http://<any-node-host-ip>:31313/v1/batches' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: abc' \
  -H 'Content-Type: application/json' \
  -d '{
  "model": "Qwen/Qwen2.5-0.5B-Instruct",
  "input": [
    {"prompt": "Explain quantum entanglement."},
    {"prompt": "Write a story about a 7900 XTX GPU."}
  ],
  "max_tokens": 50
}'
```

### Monitoring Performance
You can monitor real-time performance via the database. Each batch records:
*   `total_in_tokens`: Sum of prompt tokens.
*   `total_out_tokens`: Sum of generated tokens.
*   `tokens_per_second`: Inference speed.

### Benchmarks 

Some noted benchmarks(7900 XTX):

- Model: Qwen2.5-0.5B
- Batch Size: 1000
- Input tokens: 3081
- Output tokens: 17644
- Avg Output Speed: ~2361 tokens/sec


## Cleanup
To remove all resources, including the KubeRay operator and device plugins:
```bash
make undeploy
```
