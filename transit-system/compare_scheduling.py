
import csv
import sys
from pathlib import Path

# Allow imports from the main project folder
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common.routes import ROUTES
from scheduling_service.scheduling import (
    HEADWAY_BY_DEMAND,
    round_trip_minutes,
)

# Fixed scheduling always uses a 10-minute headway
FIXED_HEADWAY = 10

results = []

for route_id in ROUTES:
    trip_time = round_trip_minutes(route_id)

    for demand in ["OFF_PEAK", "NORMAL", "PEAK"]:
        fixed_headway = FIXED_HEADWAY
        dynamic_headway = HEADWAY_BY_DEMAND[demand]

        # Use the same bus calculation as scheduling.py
        import math

        fixed_buses = math.ceil(trip_time / fixed_headway)
        dynamic_buses = math.ceil(trip_time / dynamic_headway)

        # Estimated average waiting time
        fixed_wait = fixed_headway / 2
        dynamic_wait = dynamic_headway / 2

        wait_reduction = (
            (fixed_wait - dynamic_wait) / fixed_wait * 100
        )

        results.append({
            "Route": route_id,
            "Demand": demand,
            "Round Trip (min)": round(trip_time, 2),
            "Fixed Headway": fixed_headway,
            "Dynamic Headway": dynamic_headway,
            "Fixed Buses": fixed_buses,
            "Dynamic Buses": dynamic_buses,
            "Fixed Avg Wait": fixed_wait,
            "Dynamic Avg Wait": dynamic_wait,
            "Wait Reduction (%)": round(wait_reduction, 1),
        })

        print(
            f"{route_id} {demand}: "
            f"Fixed = {fixed_headway} min / {fixed_buses} buses, "
            f"Dynamic = {dynamic_headway} min / {dynamic_buses} buses, "
            f"Wait reduction = {wait_reduction:.1f}%"
        )

output = Path(__file__).parent / "scheduling_results.csv"

with open(output, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

print(f"\nResults saved to {output}")
