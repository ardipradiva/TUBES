FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY approved_event_notifier_service/. .
EXPOSE 5008
CMD ["python", "app.py"]
