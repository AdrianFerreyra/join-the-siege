# Adrian Ferreyra - Heron Coding Challenge - File Classifier

## Overview

This is my take around the coding challenge 'join-the-siege' by Heron Data:

```
This repository provides a basic endpoint for classifying files by their filenames. However, the current classifier has limitations when it comes to handling poorly named files, processing larger volumes, and adapting to new industries effectively.

Your task: improve this classifier by adding features and optimisations to handle (1) poorly named files, (2) scaling to new industries, and (3) processing larger volumes of documents.
```

### Architecture

The system is designed around two modules: the API module responding REST calls from users and the Classification Service module evaluating file content using ML and exposing a REST API itself.

The communication between the API and Classification Services is done using HTTP – other options (like gRCP) are available.

The system – designed focussing on the [12 Factor App principles](https://12factor.net/) – is ready to be deployed as 2 running processes or to a K8s cluster, as prefered.

### Considersations

I decided to leave the original API running in Flask as is, to maintain the original implementation. This could cause a problem since Flask is a WSGI API Framework and could represent a bottleneck if processing times scale. My recommendation is to consider moving this API to a ASGI framework like FastAPI that will allow us to leverage non-preemptive cooperative multitasking when calling the Classification service.

On volumes, I have decided to use PermanentVolume mounting to share the model accross Classification Services Instances. This works, but in a production environment I would recommend relying on a more robust storage solution like AWS S3 or GCP CS.

For training purposes, I have decided to run the training code manually and set the model in the mounted folder myself. It could be possible to retrain the model based on certain signals, or periodically. Also, I'd consider monitoring the model efficiency to decide on this.

### Potential Further Enhancements:

- Generate Synthethic data using big LLMs like Anthopic's or OpenAI's.
- CI Workflow for testing and Docker building
- Using PDF2Image to handle images embeeded in PDFs
- Multi-language support in TF-IDF.

### Part 1: Enhancing the Classifier

The original API defined the document type based on string matching on the provided filename. This is not only extremely error-prone, but also very hard to iterate on since we'd have to add any new considered cases manually every time.
My approach uses a small TD-IDF model trained on synthetic data from Claude to categorise the file content itself. Image files are read using Tesseract, and PDF files with PyPDF2.

I decided to use a model for flexibility. This allows us to retrain the model on different industries and document types iteratively.

### Part 2: Productionising the Classifier

I have decided to deploy the system into a K8s cluster to leverage horizontal auto-scaling capabilities. Classifier instances will be created/destroyed depending on the system usage, saving costs and simplifying managing. This architecture also allows other future services to consume the Classifier service from the cluster easily.

## Getting Started

1. Clone the repository:

   ```shell
   git clone <repository_url>
   cd join-the-siege
   ```

### Local Processes Deployment

1. Install dependencies:

   ```shell
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Install Tesseract (MAC - Using Brew) (Required for Image File reading)

   ```shell
   brew install tesseract
   ```

3. Run the Classifier REST service:

   ```shell
   make start-local-classifier-service
   ```

4. Test the classifier using a tool like curl:

   ```shell
   curl -X POST -F 'file=@path_to_pdf.pdf' http://127.0.0.1/classify_file
   ```

5. Run tests:
   ```shell
    pytest
   ```

### Local K8S Deployment

If you wish to run the system in a local minikube K8S Cluster, follow these steps:

1. Install Docker and Minikube and start them locally. I recommend using Docker as a Hypervisor.

   ```shell
   minikube start --driver=docker
   minikube addons enable ingress
   ```

2. Deploy the system. This will keep an alive process running for volume mouting.

   ```shell
   make setup-local-k8s-env
   ```

3. Run a minikube tunnel to access the ingress from our hosting machine network. This will keep an alive process running.

   ```shell
   minikube tunnel
   ```

4. Access the system through the same host and port as above
   ```shell
   curl -X POST -F 'file=@path_to_pdf.pdf' http://127.0.0.1/classify_file
   ```
