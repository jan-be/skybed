from typing import Optional

from geopy import Point
from pydantic import BaseModel, Field, ConfigDict, computed_field


class UAVContainer(BaseModel):
    id: str
    throttled_ip: str
    unthrottled_ip: str
    throttled_network_id: str
    unthrottled_network_id: str
    tc_class_added: bool = False


class UAVEvaluation(BaseModel):
    network_update_count: int = 0


class UAV(BaseModel):
    uav_id: str
    uav_type: str
    speed: float
    direction: float
    vertical_speed: float
    container: UAVContainer = Field(default=None, exclude=True)
    evaluation: UAVEvaluation = Field(default=UAVEvaluation(), exclude=True)
    position: Point = Field(exclude=True)
    currently_in_collision: bool = Field(default=False)
    previously_in_collision: bool = Field(default=False)

    @computed_field
    @property
    def latitude(self) -> float:
        return self.position.latitude

    @computed_field
    @property
    def longitude(self) -> float:
        return self.position.longitude

    @computed_field
    @property
    def altitude(self) -> float:
        return self.position.altitude

    def __init__(self, **data):
        latitude = data.pop('latitude')
        longitude = data.pop('longitude')
        altitude = data.pop('altitude')

        data['position'] = Point(latitude, longitude, altitude)

        super().__init__(**data)

    model_config = ConfigDict(arbitrary_types_allowed=True)


class MetaData(BaseModel):
    origin: str
    timestamp: Optional[float]
    ingest_timestamp: Optional[float]


class UAVResponseModel(BaseModel):
    data: list[UAV]
    meta: Optional[MetaData] = None
