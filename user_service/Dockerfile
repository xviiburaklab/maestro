FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common/ /app/common/
COPY user_service/ /app/user_service/

ENV PYTHONPATH=/app

CMD ["uvicorn", "user_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
