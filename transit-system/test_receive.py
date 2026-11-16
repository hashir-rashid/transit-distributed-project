from common.bus import MessageBus
from common.messages import VehicleLocation, VEHICLE_LOCATION

bus = MessageBus()


def on_message(routing_key, body):
    location = VehicleLocation.from_json(body)
    print(f"Received on '{routing_key}': {location.vehicleId} at "
          f"({location.lat}, {location.lon}), {location.occupancy} riders")


print("Waiting for messages... (Ctrl+C to stop)")
bus.subscribe([VEHICLE_LOCATION], on_message)