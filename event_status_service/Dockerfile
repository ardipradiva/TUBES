# user_service/Dockerfile
FROM python:3.10-slim
WORKDIR /app

# Salin requirements.txt dari root context
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Salin kode aplikasi dari subdirektori user_service di dalam context
COPY event_status_service/. .
WORKDIR /app/

EXPOSE 5007
CMD ["python", "app.py"]