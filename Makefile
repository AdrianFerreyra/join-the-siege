# Default shell
SHELL := /bin/bash

.PHONY: docker-env docker-build-all setup-local-env stop-local-env clean k8s-mount-data-dir

API_IMAGE_NAME_TAG := api:v1
CLASSIFIER_IMAGE_NAME_TAG := classifier-service:v1
# Setup docker environment to use minikube's docker daemon
docker-env:
	@echo "⚙️ Configuring Docker environment for Minikube..."
	@eval $$(minikube -p minikube docker-env)

docker-build-api: 
	@echo "🚪 Building Docker image $(API_IMAGE_NAME_TAG)..."
	docker build -t $(API_IMAGE_NAME_TAG) -f ./deployment/build/api/Dockerfile .

docker-build-classifier-service: 
	@echo "🐕‍🦺 Building Docker image classifier-service:v1..."
	docker build -t classifier-service:v1 -f ./deployment/build/classifier/Dockerfile .

docker-build-all:
	@echo "✨ Building all Docker images..."
	@eval $$(minikube -p minikube docker-env) && make docker-build-api && make docker-build-classifier-service

# Clean up old images
docker-clean: 
	@echo "🧹 Removing old Docker images..."
	@eval $$(minikube -p minikube docker-env) &&
	docker rmi $(API_IMAGE_NAME_TAG) || true &&
	docker rmi $(CLASSIFIER_IMAGE_NAME_TAG) || true

# Deploy environment to Kubernetes
k8s-deploy:
	@echo "🚀 Deploying system to Kubernetes..."
	kubectl apply -k ./deployment/k8s 

k8s-clean:
	@echo "🧹 Cleaning system from Kubernetes..."
	kubectl delete all -l "release=application"

k8s-mount-data-dir:
	@echo "🔨 Mounting 'data' dir to k8s '/mnt/data'"
	minikube mount ./data:/mnt/data &

# Local Env
start-local-classifier-service:
	@echo "Starting local Classifier service..."
	export CLASSIFIER_SERVICE_DATA_VOLUME="./data" && \
	export CLASSIFIER_SERVICE_MODEL_FILENAME="naive_bayes_model.pkl" && \
	export CLASSIFIER_SERVICE_VECTORIZER_FILENAME="tfidf_vectorizer.pkl" &&\
	python -m uvicorn src.classifier:app --host=0.0.0.0 --port=8080

start-local-api:
	@echo "Starting local API..."
	export CLASSIFIER_SERVICE_HOST="http://localhost" && \
	export CLASSIFIER_SERVICE_PORT="8080" && \
	CLASSIFIER_SERVICE_ENDPOINT="classify_file" && \
	python -m gunicorn -b "0.0.0.0:80" src.app:app

# Setup commands
setup-local-k8s-env: docker-env
	@eval $$(minikube -p minikube docker-env) && make k8s-mount-data-dir & make docker-build-all && make k8s-deploy

stop-local-k8s-env:
	@eval $$(minikube -p minikube docker-env) && make k8s-clean && make docker-clean
