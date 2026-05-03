deploy:
    # Ray operator
	helm repo add kuberay https://ray-project.github.io/kuberay-helm/
	helm repo update
	helm install kuberay-operator kuberay/kuberay-operator --version 1.6.0
    # AMD gpu device plugin
	kubectl apply -f https://raw.githubusercontent.com/ROCm/k8s-device-plugin/master/k8s-ds-amdgpu-dp.yaml
    # rancher local-path CSI solution
	kubectl apply -f https://raw.githubusercontent.com/rancher/local-path-provisioner/v0.0.34/deploy/local-path-storage.yaml
    # ray project manifests
	kubectl apply -f k8s/ -R

undeploy:
	kubectl delete -f k8s/ -R --ignore-not-found
	kubectl delete -f https://raw.githubusercontent.com/ROCm/k8s-device-plugin/master/k8s-ds-amdgpu-dp.yaml --ignore-not-found
	kubectl delete -f https://raw.githubusercontent.com/rancher/local-path-provisioner/v0.0.34/deploy/local-path-storage.yaml --ignore-not-found
	helm uninstall kuberay-operator || true
