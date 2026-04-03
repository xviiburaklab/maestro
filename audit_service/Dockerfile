FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common/ /app/common/
COPY audit_service/ /app/audit_service/

ENV PYTHONPATH=/app

CMD ["uvicorn", "audit_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
