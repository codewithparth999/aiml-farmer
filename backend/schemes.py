from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class CropConfigCreate(BaseModel):
    crop: str
    growth_stage: Optional[str] = None
    sowing_date: Optional[date] = None
    field_area: float = Field(gt=0)
    soil_type: str
    field_capacity: float = Field(gt=0, le=100)
    wilting_point: float = Field(ge=0, lt=100)
    root_depth: float = Field(gt=0)


class SoilMoistureCreate(BaseModel):
    field_id: Optional[int] = None
    moisture: float = Field(ge=0, le=100)
    source: str = "manual"
    notes: Optional[str] = None


class AdvisoryRequest(BaseModel):
    field_id: int
    current_moisture: float = Field(ge=0, le=100)
    et0: float = Field(ge=0)
    forecast_rain: float = Field(ge=0)


class APIResponse(BaseModel):
    status: str
    message: str
    