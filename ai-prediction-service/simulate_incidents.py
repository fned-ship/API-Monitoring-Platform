import argparse
import time
import urllib.request

BASE_URL = "http://localhost:8090"


def hit(path: str):
    try:
        urllib.request.urlopen(f"{BASE_URL}{path}", timeout=5).read()
    except Exception:
        pass  # failures are expected for /fail — that's the point


def steady_traffic(n: int, delay: float = 1.0):
    print(f"[scenario] steady traffic: {n} requests, {delay}s apart")
    for i in range(n):
        hit(f"/api/bookings/{i}")
        time.sleep(delay)


def error_burst(n: int, delay: float = 0.5):
    print(f"[scenario] error burst: {n} forced 500s")
    for _ in range(n):
        hit("/api/bookings/fail")
        time.sleep(delay)


def latency_spike(n: int, delay: float = 0.5):
    print(f"[scenario] latency spike: {n} forced slow responses")
    for _ in range(n):
        hit("/api/bookings/slow")
        time.sleep(delay)


def realistic_incident():
    """Combined scenario: normal traffic, gradual degradation, spike, recovery —
    this is the one to run for the lead-time validation in 2E.3."""
    print("[scenario] realistic incident: baseline -> degradation -> spike -> recovery")
    steady_traffic(20, delay=1.5)
    print("[scenario] degradation phase...")
    for i in range(10):
        hit("/api/bookings/slow" if i % 3 == 0 else "/api/bookings/1")
        time.sleep(1.5)
    print("[scenario] acute spike...")
    error_burst(8, delay=0.3)
    latency_spike(4, delay=0.5)
    print("[scenario] recovery phase...")
    steady_traffic(20, delay=1.5)
    print("[scenario] done")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("scenario", choices=["steady", "errors", "latency", "realistic"])
    parser.add_argument("--count", type=int, default=20)
    args = parser.parse_args()

    if args.scenario == "steady":
        steady_traffic(args.count)
    elif args.scenario == "errors":
        error_burst(args.count)
    elif args.scenario == "latency":
        latency_spike(args.count)
    elif args.scenario == "realistic":
        realistic_incident()