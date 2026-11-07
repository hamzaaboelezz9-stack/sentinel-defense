from datetime import UTC, datetime
from ipaddress import ip_address, ip_network
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Event(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(min_length=1, max_length=100, pattern=r"^[\w-]+$")
    timestamp: datetime
    device_id: str = Field(min_length=1, max_length=60)
    source_ip: str
    destination_ip: str | None = None
    username: str = Field(min_length=1, max_length=60)
    category: Literal["authentication", "network", "device"] = "authentication"
    event_type: Literal[
        "login", "access_denied", "configuration_change", "telemetry"
    ] = "login"
    status: Literal["success", "failure"] = "failure"
    severity: Literal["low", "medium", "high", "critical"] = "low"
    environment: Literal["synthetic-lab"] = "synthetic-lab"
    related_incident_id: str | None = Field(default=None, max_length=250)
    label: Literal[0, 1] | None = None
    disabled_account: bool = False
    telemetry: float = Field(default=0, ge=0, le=100)

    @field_validator("timestamp")
    @classmethod
    def utc(cls, v):
        if v.tzinfo is None:
            raise ValueError("Timezone required")
        return v.astimezone(UTC)

    @field_validator("source_ip", "destination_ip")
    @classmethod
    def documentation_ip(cls, v):
        if v is None:
            return v
        ip = ip_address(v)
        if not any(
            ip in ip_network(n)
            for n in ["192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24"]
        ):
            raise ValueError("Documentation IP ranges only")
        return v


class Login(BaseModel):
    username: str = Field(max_length=60)
    password: str = Field(max_length=200)


class Update(BaseModel):
    severity: Literal["low", "medium", "high", "critical"] | None = None
    classification: Literal["unreviewed", "confirmed", "false_positive"] = "unreviewed"
    status: Literal["open", "acknowledged", "resolved", "false_positive"] = "open"
    assignment: str = Field(default="", max_length=60)
    note: str = Field(default="", max_length=2000)
