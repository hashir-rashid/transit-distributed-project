import math

from common.routes import ROUTES


def distance_km(lat1, lon1, lat2, lon2):
    dlat = (lat2 - lat1) * 111
    dlon = (lon2 - lon1) * 111 * math.cos(math.radians(lat1))
    return math.hypot(dlat, dlon)


def upcoming_stops(bus):
    stops = ROUTES[bus["routeId"]]["stops"]
    stop_ids = [stop[0] for stop in stops]
    i = stop_ids.index(bus["nextStopId"])
    direction = bus.get("direction", 1)

    # Distance from the bus to its next stop
    km = distance_km(bus["lat"], bus["lon"], stops[i][2], stops[i][3])
    result = [(stops[i][0], km)]

    for _ in range(2 * (len(stops) - 1) - 1):
        nxt = i + direction
        if nxt < 0 or nxt >= len(stops):
            direction *= -1
            nxt = i + direction
        km += distance_km(stops[i][2], stops[i][3], stops[nxt][2], stops[nxt][3])
        i = nxt
        result.append((stops[i][0], km))
    return result


def calculate_etas(vehicles):
    etas = {}
    for bus in vehicles:
        speed = max(bus["speedKmh"], 1)
        seen = set()
        for stop_id, km in upcoming_stops(bus):
            if stop_id in seen:
                continue
            seen.add(stop_id)
            etas.setdefault(stop_id, []).append({
                "vehicleId": bus["vehicleId"],
                "routeId": bus["routeId"],
                "minutes": round(km / speed * 60, 1),
            })
    for arrivals in etas.values():
        arrivals.sort(key=lambda a: a["minutes"])
    return etas