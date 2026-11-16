from common.bus import MessageBus
from common.messages import VehicleLocation, VEHICLE_LOCATION

bus = MessageBus()

msg = VehicleLocation("BUS-1", "R1", 43.9445, -78.8964, 30.0, "S4", 25, 60)
bus.publish(VEHICLE_LOCATION, msg)
print("Sent:", msg.to_json())