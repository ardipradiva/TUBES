FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY room_booking_status_service/. .
EXPOSE 5009
CMD ["python", "app.py"]
