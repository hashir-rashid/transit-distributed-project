import math

from common.bus import MessageBus
from common.messages import DemandUpdate, ScheduleUpdate, DEMAND_UPDATE, SCHEDULE_UPDATE
from common.routes import ROUTES

AVERAGE_SPEED_KMH = 32    # average bus speed, including stops

# How often a bus comes (minutes between buses) for each demand level
HEADWAY_BY_DEMAND = {"PEAK": 5, "NORMAL": 10, "OFF_PEAK": 20}

current_schedules = {}    # latest schedule for each route (kept if the demand service goes down)


def distance_km(a, b):
    """Approximate distance between two stops."""
    dlat = (b[2] - a[2]) * 111
    dlon = (b[3] - a[3]) * 111 * math.cos(math.radians(a[2]))
    return math.hypot(dlat, dlon)


def round_trip_minutes(route_id):
    """How long one bus takes to drive the whole route and come back."""
    stops = ROUTES[route_id]["stops"]
    one_way_km = sum(distance_km(stops[i], stops[i + 1]) for i in range(len(stops) - 1))
    return 2 * one_way_km / AVERAGE_SPEED_KMH * 60


def make_schedule(demand):
    """Decide bus frequency and number of buses for a route, based on its demand."""
    headway = HEADWAY_BY_DEMAND[demand.demandLevel]
    vehicles = math.ceil(round_trip_minutes(demand.routeId) / headway)
    return ScheduleUpdate(
        routeId=demand.routeId,
        headwayMinutes=headway,
        vehiclesAssigned=vehicles,
        reason=f"{demand.demandLevel} demand ({demand.passengerCount} passengers, "
               f"{demand.windowStart}-{demand.windowEnd})",
    )


if __name__ == "__main__":
    print("Starting Scheduling Service...")
    bus = MessageBus()

    def on_demand(routing_key, body):
        demand = DemandUpdate.from_json(body)
        schedule = make_schedule(demand)

        # Only print when the schedule actually changes, to keep the output readable
        previous = current_schedules.get(schedule.routeId)
        if previous is None or previous.headwayMinutes != schedule.headwayMinutes:
            print(f"[{demand.windowStart}] {schedule.routeId}: bus every {schedule.headwayMinutes} min, "
                  f"{schedule.vehiclesAssigned} buses ({demand.demandLevel})")

        current_schedules[schedule.routeId] = schedule
        bus.publish(SCHEDULE_UPDATE, schedule)

    bus.subscribe([DEMAND_UPDATE], on_demand)