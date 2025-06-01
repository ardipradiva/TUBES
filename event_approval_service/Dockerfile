# product_service/Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY event_approval_service/. .
EXPOSE 5006
CMD ["python", "app.py"]