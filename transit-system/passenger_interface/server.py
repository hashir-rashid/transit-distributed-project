import json
import sys
import threading
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse

from common.bus import MessageBus
from common.messages import VEHICLE_LOCATION, SCHEDULE_UPDATE
from common.routes import ROUTES
from eta import calculate_etas

app = FastAPI()

vehicles = {}
schedules = {}


def listen_to_rabbitmq():
    """Runs in the background: saves every bus location and schedule that arrives."""
    bus = MessageBus()

    def on_message(routing_key, body):
        data = json.loads(body)
        if routing_key == VEHICLE_LOCATION:
            vehicles[data["vehicleId"]] = data
        elif routing_key == SCHEDULE_UPDATE:
            schedules[data["routeId"]] = data

    bus.subscribe([VEHICLE_LOCATION, SCHEDULE_UPDATE], on_message)


@app.get("/")
def index():
    """Send the map page to the browser."""
    return FileResponse(HERE / "index.html")


@app.get("/api/routes")
def get_routes():
    """Send the routes and stops so the map can draw them."""
    return ROUTES


@app.get("/api/vehicles")
def get_vehicles():
    """Send the latest location of every bus."""
    return list(vehicles.values())


@app.get("/api/etas")
def get_etas():
    """For every stop, the buses coming and their ETA in minutes."""
    return calculate_etas(list(vehicles.values()))


@app.get("/api/schedules")
def get_schedules():
    """Send the latest schedule of every route."""
    return dict(schedules)


if __name__ == "__main__":
    # Start listening to RabbitMQ in the background, then start the web server
    threading.Thread(target=listen_to_rabbitmq, daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=8000)