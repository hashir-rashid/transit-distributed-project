import json
import time
from dataclasses import asdict, dataclass, field

VEHICLE_LOCATION = "vehicle.location"
DEMAND_UPDATE = "demand.update"
SCHEDULE_UPDATE = "schedule.update"


def now_ms():
    return int(time.time() * 1000)


class Message:

    def to_json(self):
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, raw):
        return cls(**json.loads(raw))


@dataclass
class VehicleLocation(Message):
    vehicleId: str
    routeId: str
    lat: float
    lon: float
    speedKmh: float
    nextStopId: str
    occupancy: int
    capacity: int
    direction: int = 1
    timestamp: int = field(default_factory=now_ms)

@dataclass
class DemandUpdate(Message):
    routeId: str
    windowStart: str  # e.g. "08:00"
    windowEnd: str  # e.g. "08:15"
    passengerCount: int
    demandLevel: str  # "PEAK", "NORMAL" or "OFF_PEAK"
    timestamp: int = field(default_factory=now_ms)

@dataclass
class ScheduleUpdate(Message):
    routeId: str
    headwayMinutes: int  # minutes between buses
    vehiclesAssigned: int
    reason: str  # e.g. "PEAK demand"
    timestamp: int = field(default_factory=now_ms)