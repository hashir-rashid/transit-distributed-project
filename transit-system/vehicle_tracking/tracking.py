import math
import random
import os

from common.bus import MessageBus
from common.messages import VehicleLocation, VEHICLE_LOCATION
from common.routes import ROUTES, VEHICLE_CAPACITY

UPDATE_SECONDS = 3
SPEEDUP = 10          # 1 real second = 10 simulated seconds, so buses visibly move


vehicles = [
    {"vehicleId": "BUS-1", "routeId": "R1", "stopIndex": 0, "direction": 1,  "progress": 0.0, "speedKmh": 30.0, "occupancy": 12},
    {"vehicleId": "BUS-2", "routeId": "R1", "stopIndex": 3, "direction": -1, "progress": 0.0, "speedKmh": 25.0, "occupancy": 35},
    {"vehicleId": "BUS-3", "routeId": "R2", "stopIndex": 0, "direction": 1,  "progress": 0.0, "speedKmh": 20.0, "occupancy": 50},
    {"vehicleId": "BUS-4", "routeId": "R3", "stopIndex": 0, "direction": 1,  "progress": 0.0, "speedKmh": 35.0, "occupancy": 20},
]

PREFIX = os.getenv("HOSTNAME", "L1")[:4]
for vehicle in vehicles:
    vehicle["vehicleId"] = f"{PREFIX}-{vehicle['vehicleId']}"
    vehicle["progress"] = random.uniform(0, 0.9)


def distance_km(a, b):
    dlat = (b[2] - a[2]) * 111
    dlon = (b[3] - a[3]) * 111 * math.cos(math.radians(a[2]))
    return math.hypot(dlat, dlon)


def current_and_next_stop(vehicle):
    stops = ROUTES[vehicle["routeId"]]["stops"]
    return stops[vehicle["stopIndex"]], stops[vehicle["stopIndex"] + vehicle["direction"]]


def arrive_at_stop(vehicle):
    stops = ROUTES[vehicle["routeId"]]["stops"]
    vehicle["stopIndex"] += vehicle["direction"]
    vehicle["progress"] = 0.0

    nxt = vehicle["stopIndex"] + vehicle["direction"]
    if nxt < 0 or nxt >= len(stops):
        vehicle["direction"] *= -1

    vehicle["occupancy"] = max(0, min(VEHICLE_CAPACITY, vehicle["occupancy"] + random.randint(-8, 10)))
    vehicle["speedKmh"] = round(random.uniform(20, 45), 1)


def move(vehicle, seconds):
    current, nxt = current_and_next_stop(vehicle)
    km_travelled = vehicle["speedKmh"] * seconds / 3600
    vehicle["progress"] += km_travelled / distance_km(current, nxt)
    if vehicle["progress"] >= 1:
        arrive_at_stop(vehicle)


def update_locations(bus):
    for vehicle in vehicles:
        move(vehicle, UPDATE_SECONDS * SPEEDUP)

        current, nxt = current_and_next_stop(vehicle)
        p = vehicle["progress"]

        message = VehicleLocation(
            vehicleId=vehicle["vehicleId"],
            routeId=vehicle["routeId"],
            lat=round(current[2] + (nxt[2] - current[2]) * p, 6),
            lon=round(current[3] + (nxt[3] - current[3]) * p, 6),
            speedKmh=vehicle["speedKmh"],
            nextStopId=nxt[0],
            occupancy=vehicle["occupancy"],
            capacity=VEHICLE_CAPACITY,
            direction=vehicle["direction"],
        )

        # Publish the message to RabbitMQ
        bus.publish(VEHICLE_LOCATION, message)

        print(
            f"Published {message.vehicleId}: "
            f"({message.lat:.5f}, {message.lon:.5f}) -> {message.nextStopId}, "
            f"{message.occupancy} passengers"
        )


if __name__ == "__main__":
    print("Starting Vehicle Tracking Service...")

    bus = MessageBus()

    try:
        while True:
            update_locations(bus)

            # Wait while keeping RabbitMQ alive
            bus.sleep(UPDATE_SECONDS)

    except KeyboardInterrupt:
        print("\nVehicle Tracking Service Stopped")

    finally:
        bus.connection.close()