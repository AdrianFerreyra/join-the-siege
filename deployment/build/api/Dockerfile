FROM python:3.12.0-slim

WORKDIR /app

COPY . /app/

RUN pip install -r deployment/build/api/requirements.txt

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "gunicorn", "src.app:app", "-b", "0.0.0.0:80"]