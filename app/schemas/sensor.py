from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class SensorData(BaseModel):
    device_id: str
    sensor_type: Literal[
        "temperature", "humidity", "light", "water_level", "soil_moisture", "co2"
    ]
    value: float
    unit: str
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)


class ActuatorCommand(BaseModel):
    device_id: str
    command: Literal["on", "off", "set", "auto", "manual"]
    value: Optional[float] = None
    parameters: Optional[dict] = Field(default_factory=dict)
