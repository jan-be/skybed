from typing import List, Optional

from geopy import Point
from pydantic import BaseModel, Field, ConfigDict, computed_field


class UAVContainer(BaseModel):
    id: str
    throttled_ip: str
    unthrottled_ip: str
    throttled_network_id: str
    unthrottled_network_id: str


class UAVData(BaseModel):
    uav_id: str
    uav_type: str
    speed: float
    direction: float
    vertical_speed: float
    container: UAVContainer = Field(default=None, exclude=True)
    position: Point = Field(exclude=True)

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
    timestamp: float


class UAVResponseModel(BaseModel):
    data: List[UAVData]
    meta: Optional[MetaData] = None
