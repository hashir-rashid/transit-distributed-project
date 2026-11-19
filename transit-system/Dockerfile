
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY common/ ./common/
COPY vehicle_tracking/ ./vehicle_tracking/
COPY demand_service/ ./demand_service/
COPY scheduling_service/ ./scheduling_service/
COPY passenger_interface/ ./passenger_interface/

ENV PYTHONUNBUFFERED=1
ENV RABBITMQ_HOST=rabbitmq

CMD ["python", "-m", "vehicle_tracking.tracking"]
