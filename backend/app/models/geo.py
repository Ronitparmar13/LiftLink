"""GeoJSON models — coordinates are always [longitude, latitude]."""

from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator

from app.config import get_settings


class GeoPoint(BaseModel):
    type: Literal["Point"] = "Point"
    coordinates: Annotated[list[float], Field(min_length=2, max_length=2)]

    @field_validator("coordinates")
    @classmethod
    def validate_coordinates(cls, v: list[float]) -> list[float]:
        lng, lat = v[0], v[1]
        if not (-180 <= lng <= 180):
            raise ValueError("longitude must be between -180 and 180")
        if not (-90 <= lat <= 90):
            raise ValueError("latitude must be between -90 and 90")
        settings = get_settings()
        if not settings.is_within_campus_bounds(lng, lat):
            raise ValueError(
                "coordinates are outside the Parul University campus bounding box"
            )
        return [lng, lat]


class GeoLineString(BaseModel):
    type: Literal["LineString"] = "LineString"
    coordinates: Annotated[list[list[float]], Field(min_length=2)]

    @field_validator("coordinates")
    @classmethod
    def validate_coordinates(cls, v: list[list[float]]) -> list[list[float]]:
        validated: list[list[float]] = []
        for pair in v:
            if len(pair) != 2:
                raise ValueError("each coordinate pair must be [lng, lat]")
            point = GeoPoint(coordinates=pair)
            validated.append(point.coordinates)
        return validated
