import random

from common.bus import MessageBus
from common.messages import DemandUpdate, DEMAND_UPDATE
from common.routes import ROUTES

WINDOW_MINUTES = 15           # analyze passengers in 15-minute windows
REAL_SECONDS_PER_WINDOW = 5   # each window takes 5 real seconds -> a full day in ~8 minutes
START_HOUR = 6                # simulated day starts at 6:00 AM

# How busy each hour of the day is (1.0 = rush hour, 0.05 = middle of the night)
HOURLY_DEMAND = [
    0.05, 0.05, 0.05, 0.05, 0.05, 0.2,   # 00:00 - 05:59  night
    0.5,  1.0,  1.0,  0.65,              # 06:00 - 09:59  morning rush (7-9)
    0.5,  0.5,  0.6,  0.5,  0.5,  0.65,  # 10:00 - 15:59  midday
    1.0,  1.0,  0.65,                    # 16:00 - 18:59  evening rush (16-18)
    0.4,  0.4,  0.25, 0.2,  0.1,         # 19:00 - 23:59  evening / night
]

# Passengers per 15 minutes on each route at rush hour
ROUTE_PEAK_PASSENGERS = {"R1": 120, "R2": 150, "R3": 80}


def simulate_taps(minute_of_day):
    hour = minute_of_day // 60
    taps = []
    for route_id, route in ROUTES.items():
        expected = ROUTE_PEAK_PASSENGERS[route_id] * HOURLY_DEMAND[hour]
        count = max(0, round(random.gauss(expected, expected * 0.1)))
        for _ in range(count):
            stop = random.choice(route["stops"])
            taps.append({"routeId": route_id, "stopId": stop[0]})
    return taps


def analyze(taps):

    counts = {route_id: 0 for route_id in ROUTES}
    for tap in taps:
        counts[tap["routeId"]] += 1
    return counts


def classify(route_id, count):
    ratio = count / ROUTE_PEAK_PASSENGERS[route_id]
    if ratio >= 0.8:
        return "PEAK"
    if ratio <= 0.3:
        return "OFF_PEAK"
    return "NORMAL"


def time_label(minute):
    return f"{(minute // 60) % 24:02d}:{minute % 60:02d}"


if __name__ == "__main__":
    print("Starting Demand Analysis Service...")
    bus = MessageBus()
    minute = START_HOUR * 60

    try:
        while True:
            taps = simulate_taps(minute)
            counts = analyze(taps)

            for route_id, count in counts.items():
                message = DemandUpdate(
                    routeId=route_id,
                    windowStart=time_label(minute),
                    windowEnd=time_label(minute + WINDOW_MINUTES),
                    passengerCount=count,
                    demandLevel=classify(route_id, count),
                )
                bus.publish(DEMAND_UPDATE, message)
                print(f"[{message.windowStart}-{message.windowEnd}] {route_id}: "
                      f"{count} passengers -> {message.demandLevel}")

            minute = (minute + WINDOW_MINUTES) % (24 * 60)   # next window, wraps at midnight
            bus.sleep(REAL_SECONDS_PER_WINDOW)

    except KeyboardInterrupt:
        print("\nDemand Analysis Service Stopped")