# ====================================================================
# PYTHON 3.13 KAFKA SELECTOR PATCH
# ====================================================================
import selectors

# Target the runtime active selector class directly
_orig_unregister = selectors.DefaultSelector.unregister

def _safe_unregister(self, fileobj):
    try:
        return _orig_unregister(self, fileobj)
    except (ValueError, KeyError) as e:
        # Ignore dead -1 descriptors or missing socket cleanup keys safely
        if "Invalid file descriptor: -1" in str(e) or isinstance(e, KeyError):
            return None
        raise

selectors.DefaultSelector.unregister = _safe_unregister
# ====================================================================

import json
import threading
import time
from collections import defaultdict, deque
from datetime import datetime, timezone

from kafka import KafkaConsumer
from config import KAFKA_BOOTSTRAP_SERVERS, WINDOW_SECONDS

TOPICS = ["api-request-metrics", "api-system-metrics", "api-error-logs"]

# in-memory rolling buffers, keyed by service_name, each holding recent raw events
_buffers = {
    "api-request-metrics": defaultdict(lambda: deque(maxlen=2000)),
    "api-system-metrics": defaultdict(lambda: deque(maxlen=2000)),
    "api-error-logs": defaultdict(lambda: deque(maxlen=2000)),
}
_lock = threading.Lock()


def _consume_topic(topic: str):
    while True:  # outer loop: reconnect on failure instead of letting the thread die
        try:
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                group_id="cg-ai-prediction",
                auto_offset_reset="latest",
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                consumer_timeout_ms=30000,  # periodically fall through the for-loop to re-check health
            )
            print(f"[kafka_consumer] successfully listening on topic: {topic}")
            for message in consumer:
                event = message.value
                service_name = event.get("serviceName")
                if not service_name:
                    continue
                with _lock:
                    _buffers[topic][service_name].append(event)
        except Exception as e:
            print(f"[kafka_consumer] connection error on topic '{topic}': {e!r} — reconnecting in 10s")
            time.sleep(10)


def start_consumers():
    """Starts one background thread per topic. Call once at service startup."""
    threads = []
    for topic in TOPICS:
        t = threading.Thread(target=_consume_topic, args=(topic,), daemon=True)
        t.start()
        threads.append(t)
    return threads


def get_recent_events(topic: str, service_name: str, seconds: int = WINDOW_SECONDS * 5):
    """Returns buffered events for a service within the last `seconds`, for feature computation."""
    cutoff = datetime.now(timezone.utc).timestamp() - seconds
    with _lock:
        events = list(_buffers[topic].get(service_name, []))

    def _ts(e):
        try:
            val = e.get("timestamp")
            # If it's already a number (int or float from Java), use it directly
            if isinstance(val, (int, float)):
                return val
            # Fallback if it comes as an ISO string
            if isinstance(val, str):
                return datetime.fromisoformat(val.replace("Z", "+00:00")).timestamp()
            return 0
        except Exception:
            return 0

    return [e for e in events if _ts(e) >= cutoff]


def known_services():
    with _lock:
        names = set()
        for topic_buffer in _buffers.values():
            names.update(topic_buffer.keys())
        return names