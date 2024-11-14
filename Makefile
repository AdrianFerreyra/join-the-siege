# Default shell
SHELL := /bin/bash

.PHONY: docker-env docker-build-all setup-local-env stop-local-env clean k8s-mount-data-dir

API_IMAGE_NAME_TAG := api:v1

# Setup docker environment to use minikube's docker daemon
docker-env:
	@echo "⚙️ Configuring Docker environment for Minikube..."
	@eval $$(minikube -p minikube docker-env)

docker-build-api: docker-env
	@echo "🚪 Building Docker image $(API_IMAGE_NAME_TAG)..."
	docker build -t $(API_IMAGE_NAME_TAG) -f ./deployment/build/api/Dockerfile .

docker-build-classifier-service: docker-env
	@echo "🐕‍🦺 Building Docker image classifier-service:v1..."
	docker build -t classifier-service:v1 -f ./deployment/build/classifier/Dockerfile .

docker-build-all: docker-env
	@echo "✨ Building all Docker images..."
	make docker-build-api docker-build-classifier-service

# Clean up old images
docker-clean: docker-env
	@echo "🧹 Removing old Docker images..."
	docker rmi $(API_IMAGE_NAME_TAG) || true
	docker rmi classifier-service:v1 || true

# Deploy environment to Kubernetes
k8s-deploy:
	@echo "🚀 Deploying system to Kubernetes..."
	kubectl apply -k ./deployment/k8s 

k8s-clean:
	@echo "🧹 Cleaning system from Kubernetes..."
	kubectl delete all -l "release=application"

k8s-mount-data-dir:
	@echo "🔨 Mounting `data` dir to k8s `/mnt/data`"
	minikube mount ./data:/mnt/data

# Local Env
start-local-classifier-service:
	@echo "Starting local Classifier service..."
	python -m uvicorn src.classifier:app --host=0.0.0.0 --port=80

start-local-api:
	@echo "Starting local API..."
	python -m gunicorn -b "0.0.0.0:8080" src.app:app

# Setup commands
setup-local-k8s-env:
	make docker-build-all k8s-deploy k8s-mount-data-dir

stop-local-k8s-env:
	make k8s-clean docker-clean
