import time

COOLDOWN_SECONDS = 300  # 5 minutes: don't re-publish the same prediction type+service unless severity increases

SEVERITY_RANK = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}


class Debouncer:
    def __init__(self, cooldown_seconds: int = COOLDOWN_SECONDS):
        self.cooldown_seconds = cooldown_seconds
        self._last_published = {}  # (service_name, prediction_type) -> (timestamp, severity)

    def should_publish(self, service_name: str, prediction_type: str, severity: str) -> bool:
        key = (service_name, prediction_type)
        now = time.time()
        last = self._last_published.get(key)

        if last is None:
            self._last_published[key] = (now, severity)
            return True

        last_time, last_severity = last
        severity_increased = SEVERITY_RANK[severity] > SEVERITY_RANK[last_severity]
        cooldown_expired = (now - last_time) >= self.cooldown_seconds

        if severity_increased or cooldown_expired:
            self._last_published[key] = (now, severity)
            return True

        return False