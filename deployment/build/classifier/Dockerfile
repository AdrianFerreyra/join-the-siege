FROM python:3.12.0-slim

WORKDIR /app

COPY . /app/

RUN apt-get update && apt-get -y install tesseract-ocr

RUN pip install -r deployment/build/classifier/requirements.txt

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "uvicorn", "src.classifier:app", "--host", "0.0.0.0", "--port", "8080"]