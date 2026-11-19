import csv
import json
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))   # so "common" can be imported

from common.bus import MessageBus

DURATION_SECONDS = int(sys.argv[1]) if len(sys.argv) > 1 else 60   # how long to measure
OUTPUT_FILE = Path(__file__).parent / "latency_results.csv"

latencies = {}   # message type -> list of latencies in ms, e.g. {"vehicle.location": [2.1, 3.4, ...]}
rows = []        # every single measurement, saved to the CSV file


def record(routing_key, body, received_ms):
    """Latency = time it arrived - time it was created (the message's timestamp)."""
    data = json.loads(body)
    latency_ms = received_ms - data["timestamp"]
    latencies.setdefault(routing_key, []).append(latency_ms)
    rows.append([routing_key, data["timestamp"], round(received_ms), round(latency_ms, 2)])


def summary(values, seconds):
    """Average, median, 95th percentile and max latency, plus messages per second."""
    ordered = sorted(values)
    p95 = ordered[min(len(ordered) - 1, int(len(ordered) * 0.95))]
    return {
        "messages": len(values),
        "per_second": round(len(values) / seconds, 2),
        "avg_ms": round(statistics.mean(values), 2),
        "median_ms": round(statistics.median(values), 2),
        "p95_ms": round(p95, 2),
        "max_ms": round(max(values), 2),
    }


def print_report(seconds):
    print(f"\nLatency results ({seconds:.0f} seconds)")
    print(f"{'Message type':<18}{'Messages':>9}{'Per sec':>9}{'Avg ms':>9}{'Median':>9}{'95%':>9}{'Max ms':>9}")
    all_values = []
    for key in sorted(latencies):
        s = summary(latencies[key], seconds)
        all_values += latencies[key]
        print(f"{key:<18}{s['messages']:>9}{s['per_second']:>9}{s['avg_ms']:>9}"
              f"{s['median_ms']:>9}{s['p95_ms']:>9}{s['max_ms']:>9}")
    s = summary(all_values, seconds)
    print(f"{'ALL':<18}{s['messages']:>9}{s['per_second']:>9}{s['avg_ms']:>9}"
          f"{s['median_ms']:>9}{s['p95_ms']:>9}{s['max_ms']:>9}")


if __name__ == "__main__":
    print(f"Measuring latency for {DURATION_SECONDS} seconds...")
    bus = MessageBus()
    start = time.time()

    def on_message(routing_key, body):
        record(routing_key, body, time.time() * 1000)
        if time.time() - start >= DURATION_SECONDS:
            bus.channel.stop_consuming()      # time's up: stop listening

    bus.subscribe(["#"], on_message)          # "#" = every message type
    elapsed = time.time() - start

    if not rows:
        print("No messages received. Is the system running? (docker compose up -d)")
        sys.exit(1)

    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["message_type", "sent_ms", "received_ms", "latency_ms"])
        writer.writerows(rows)

    print_report(elapsed)
    print(f"\nSaved every measurement to {OUTPUT_FILE}")