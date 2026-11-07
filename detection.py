"""Event-time sliding windows, configurable policy, rolling incident cooldowns."""

from collections import defaultdict, deque
from datetime import datetime

from pydantic import BaseModel, Field, model_validator

RULE_VERSION = "2.0"


class Policy(BaseModel):
    brute_count: int = Field(default=5, ge=2, le=1000)
    brute_seconds: int = Field(default=60, ge=1, le=3600)
    spray_accounts: int = Field(default=5, ge=2, le=1000)
    window_seconds: int = Field(default=120, ge=1, le=7200)
    cooldown_seconds: int = Field(default=120, ge=1, le=86400)
    working_start: int = Field(default=8, ge=0, le=23)
    working_end: int = Field(default=18, ge=1, le=24)
    failure_minimum: int = Field(default=10, ge=2, le=1000)
    failure_ratio: float = Field(default=0.8, gt=0, lt=1)
    denied_count: int = Field(default=5, ge=2, le=1000)
    telemetry_threshold: float = Field(default=90, ge=0, le=100)

    @model_validator(mode="after")
    def consistent(self):
        if self.working_start >= self.working_end:
            raise ValueError("Working hours must have start before end")
        if self.window_seconds < self.brute_seconds:
            raise ValueError("Window must cover brute-force window")
        return self


def correlate(events, policy=None):
    p = policy or Policy()
    alerts = []
    windows = defaultdict(deque)
    episodes = {}
    for e in sorted(
        events, key=lambda e: (datetime.fromisoformat(e["timestamp"]), e["id"])
    ):
        now = datetime.fromisoformat(e["timestamp"])
        stamp = now.timestamp()
        key = (e["source_ip"], e["device_id"])
        window = windows[key]
        while window and stamp - window[0][0] > p.window_seconds:
            window.popleft()
        window.append((stamp, e))
        group = [x for _, x in window]
        fails = [
            x
            for _, x in window
            if x["status"] == "failure" and x["category"] == "authentication"
        ]
        recent = [
            x
            for t, x in window
            if stamp - t <= p.brute_seconds
            and x["status"] == "failure"
            and x["category"] == "authentication"
        ]
        denied = [x for x in group if x["event_type"] == "access_denied"]
        auth = e["category"] == "authentication"
        checks = [
            (
                "brute_force",
                len(recent) >= p.brute_count,
                recent,
                "high",
                f"At least {p.brute_count} authentication failures within {p.brute_seconds} seconds.",
            ),
            (
                "password_spray",
                len({x["username"] for x in fails}) >= p.spray_accounts,
                fails,
                "high",
                f"At least {p.spray_accounts} distinct accounts targeted within {p.window_seconds} seconds.",
            ),
            (
                "disabled_account",
                auth and e["status"] == "success" and e.get("disabled_account"),
                [e],
                "critical",
                "Successful authentication to a disabled fictional account.",
            ),
            (
                "unusual_time",
                auth
                and e["status"] == "success"
                and not p.working_start <= now.hour < p.working_end,
                [e],
                "medium",
                f"Authentication outside {p.working_start:02}:00–{p.working_end:02}:00 UTC.",
            ),
            (
                "failure_ratio",
                len(group) >= p.failure_minimum
                and len(fails) / len(group) > p.failure_ratio,
                fails,
                "medium",
                f"Failure ratio exceeds {p.failure_ratio:.0%} across at least {p.failure_minimum} events.",
            ),
            (
                "access_denied",
                len(denied) >= p.denied_count,
                denied,
                "medium",
                "Repeated access-denied events in the configured window.",
            ),
            (
                "configuration_change",
                e["event_type"] == "configuration_change",
                [e],
                "high",
                "Unexpected simulated device configuration change.",
            ),
            (
                "device_health",
                e.get("telemetry", 0) > p.telemetry_threshold,
                [e],
                "high",
                f"Synthetic telemetry exceeds {p.telemetry_threshold:g} units.",
            ),
        ]
        for rule, match, ev, severity, explanation in checks:
            if not match:
                continue
            episode_key = (rule, *key)
            episode = episodes.get(episode_key)
            if not episode or stamp - episode["last"] > p.cooldown_seconds:
                id = f"{rule}:{e['source_ip']}:{e['device_id']}:{e['id']}"
                incident = dict(
                    id=id,
                    rule=rule,
                    rule_version=RULE_VERSION,
                    severity=severity,
                    explanation=explanation,
                    evidence=[],
                    timestamp=e["timestamp"],
                    device_id=e["device_id"],
                )
                episode = {"last": stamp, "incident": incident}
                episodes[episode_key] = episode
                alerts.append(incident)
            episode["last"] = stamp
            incident = episode["incident"]
            incident["evidence"] = sorted(
                set(incident["evidence"]) | {x["id"] for x in ev}
            )
    return alerts
