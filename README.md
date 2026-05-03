# Distributed Offline Batch Inference Platform (AMD/ROCm)

![gosd](https://github.com/l8bloom/ray/blob/main/assets/images/diagram.png)

This project creates [ray-based](https://docs.ray.io/en/latest/ray-overview/getting-started.html) inference platform for offline batching.

## Overview
This platform is a high-throughput, offline batch inference system designed to deploy the **[Qwen2.5-0.5B](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct)** model at scale. Built on **KubeRay** and optimized for **AMD Radeon GPUs (7900 XTX)**, it demonstrates an approach to distributed LLM workloads.

### Key Architectural Features
*   **Engine:** Powered by **vLLM** with PagedAttention for maximum throughput.
*   **Orchestration:** Managed via **KubeRay** (RayCluster CRD) for resilient worker scaling.
*   **Hardware:** Purpose-built for **ROCm** environments.
*   **Persistence:** PostgreSQL backend using to track job status, token counts, and performance metrics (TPS).

---

## Prerequisites
*   **OS:** Ubuntu 22.04+ (k8s nodes) with ROCm 7.2.1 drivers installed.
*   **GPU:** AMD Radeon Series (tested on 7900xtx).
*   **K8s Cluster:** v1.35+ with `kubectl`, `helm` configured([Cilium](https://cilium.io/) used for CNI).

---

## Setup & Deployment

The deployment is streamlined via a `Makefile` to handle the operator, hardware plugins, and local storage provisioning.

### 1. Installation
Prepare a functional Kubernetes cluster with CNI and at least 1 node for GPGPU programming. There are plenty of [resources](https://kubernetes.io/docs/setup/) on how to do that.  
Download the [model](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct) to your GPU nodes
```bash
# Deploys Operator, AMD Device Plugin, Storage Class, and Ray Cluster
make deploy   # installs:
              # - KubeRay operator (Helm)
              # - AMD device plugin
              # - local-path storage
              # - application manifests
              # - services
```

### 2. Infrastructure Components
*   **KubeRay Operator:** Orchestrates the lifecycle of the Ray head and worker nodes.
*   **AMD Device Plugin:** Exposes Radeon GPUs to the Kubernetes scheduler.
*   **Local Path Provisioner:** Provides CSI solution for PVC and storage resources.
*   **Python uvicorn Driver:** Acts as the entry point for submitting asynchronous batch jobs.

---

## Usage

### API Specification
The platform accepts JSON batches. It automatically maps requests to the **ChatML** format and persists metrics to the database.

**Submit a Batch Job:**
```bash
curl -X POST http://<api-url>/inference/batch \
-H "Content-Type: application/json" \
-d '{
  "model": "Qwen/Qwen2.5-0.5B-Instruct",
  "input": [
    {"prompt": "Explain quantum entanglement."},
    {"prompt": "Write a story about a 7900 XTX GPU."}
  ],
  "max_tokens": 150
}'
```

### Monitoring Performance
You can monitor real-time performance via the database. Each batch records:
*   `total_in_tokens`: Sum of prompt tokens.
*   `total_out_tokens`: Sum of generated tokens.
*   `tokens_per_second`: Inference speed`.

---

## Development & Insights

### AMD Performance Note
On a single **7900 XTX**, this stack achieves **~1,900+ tokens/second** for the Qwen 0.5B model by saturating the GPU compute units through vLLM's continuous batching.

---

## Cleanup
To remove all resources, including the KubeRay operator and device plugins:
```bash
make undeploy
```
