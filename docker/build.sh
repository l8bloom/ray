#! /usr/bin/env bash

# call this from directory representing required context
# e.g. (pwd=...ray/src/api-server) build.sh server ../../docker/server.Dockerfile
# e.g. (pwd=...ray/src/api-server) build.sh ray ../../docker/ray.Dockerfile

set -euo pipefail

local_registry="frontier:5000"

parse_args() {
	mode="${1:-}"
	dockerfile="${2:-}"

	if [[ -z "$mode" || -z "$dockerfile" ]]; then
		echo "Usage: $0 <ray|server> <dockerfile>"
		exit 1
	fi

	build_and_push "$mode" "$dockerfile"
}

build_and_push() {
	local mode="$1"
	local dockerfile="$2"
	local image_tag=""

	case "$mode" in
		ray)
			image_tag="ray:0.0.3"
			;;
		server)
			image_tag="api_server:0.0.10"
			;;
		*)
			echo "Unknown mode: $mode"
			exit 1
			;;
	esac

	if [[ ! -f "$dockerfile" ]]; then
		echo "Dockerfile not found: $dockerfile"
		exit 1
	fi

	docker build -t "$image_tag" -f "$dockerfile" .
	docker tag "$image_tag" "${local_registry}/${image_tag}"
	docker push "${local_registry}/${image_tag}"
}

parse_args "$@"
