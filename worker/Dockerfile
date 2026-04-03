FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common/ /app/common/
COPY worker/ /app/worker/
COPY orchestrator/ /app/orchestrator/

ENV PYTHONPATH=/app

CMD ["python", "-m", "worker.main"]
