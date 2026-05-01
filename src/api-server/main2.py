# learning script which acts as non k8s node ray local

import time

import ray
from vllm import LLM, SamplingParams

RAY_CLUSTER_ADDR = "ray://192.168.1.100:30422"
RAY_NAMESPACE = "vllm-space"
ACTOR_NAME = "qwen_service"

# for some reason ray images use default python installation
# even though PATH was extended with venv python
runtime_env = {
    "env_vars": {
        "PATH": "/.venv/bin:${PATH}",
    }
}


def run_stress_test():
    print(f"Connecting to {RAY_CLUSTER_ADDR}...")
    ray.init(address=RAY_CLUSTER_ADDR, namespace=RAY_NAMESPACE, runtime_env=runtime_env)

    # keep actor warm/detached
    LLMActor = ray.remote(LLM)
    llm_handle = LLMActor.options(
        name=ACTOR_NAME,
        lifetime="detached",
        get_if_exists=True,
        num_gpus=1,
        num_cpus=4,
    ).remote(
        "/model/snapshots/7ae557604adf67be50417f59c2c2f167def9a775",
    )

    prompts = [f"Explain the concept of Raylets in {i} words." for i in range(10, 110)]
    sampling_params = SamplingParams(temperature=0.7, max_tokens=1000)

    start_time = time.time()
    results = ray.get(llm_handle.generate.remote(prompts, sampling_params))
    end_time = time.time()

    # results
    total_tokens = sum(len(output.outputs[0].token_ids) for output in results)
    duration = end_time - start_time

    print("\n--- PERFORMANCE SUMMARY ---")
    print(f"Total Time: {duration:.2f} seconds")
    print(f"Total Tokens: {total_tokens}")
    print(f"Tokens Per Second (TPS): {total_tokens / duration:.2f}")
    print(f"Avg Latency per prompt: {(duration / len(prompts)) * 1000:.2f}ms")


if __name__ == "__main__":
    run_stress_test()
