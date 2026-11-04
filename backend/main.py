import json
import requests
from fastapi import HTTPException

from backend.schemes import AdvisoryRequest
from services.advisory_engine import generate_irrigation_advisory

from backend.schemes import SoilMoistureCreate
from backend.schemes import CropConfigCreate


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from services.database import get_connection, get_fields

app = FastAPI(
    title="AIML FARMER API",
    description="Smart Agriculture Intelligence Platform",
    version="1.0.0"
)


# Field data validation
class FieldCreate(BaseModel):
    field_name: str
    area: float = Field(gt=0)
    location: Optional[str] = None
    crop: Optional[str] = None
    soil_type: Optional[str] = None
    irrigation_method: Optional[str] = None


# Home API
@app.get("/")
def home():
    return {
        "status": "success",
        "message": "AIML FARMER Backend is running!"
    }


# Health API
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "backend": "FastAPI",
        "project": "AIML FARMER"
    }


# Add new field
@app.post("/fields")
def create_field(field: FieldCreate):

    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO fields
            (field_name, area, location, crop, soil_type, irrigation_method)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            field.field_name,
            field.area,
            field.location,
            field.crop,
            field.soil_type,
            field.irrigation_method
        ))

        field_id = cursor.lastrowid

    return {
        "status": "success",
        "message": "Field added successfully",
        "field_id": field_id
    }


# View all fields
@app.get("/fields")
def read_fields():
    return {
        "status": "success",
        "fields": get_fields()
    }


# Update field
@app.put("/fields/{field_id}")
def update_field(field_id: int, field: FieldCreate):

    with get_connection() as conn:
        cursor = conn.execute("""
            UPDATE fields
            SET field_name=?, area=?, location=?, crop=?,
                soil_type=?, irrigation_method=?
            WHERE id=?
        """, (
            field.field_name,
            field.area,
            field.location,
            field.crop,
            field.soil_type,
            field.irrigation_method,
            field_id
        ))

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Field not found")

    return {
        "status": "success",
        "message": "Field updated successfully"
    }


# Delete field
@app.delete("/fields/{field_id}")
def delete_field(field_id: int):

    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM fields WHERE id=?",
            (field_id,)
        )

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Field not found")

    return {
        "status": "success",
        "message": "Field deleted successfully"
    }
# Add Crop Configuration
@app.post("/crop-configurations")
def create_crop_configuration(config: CropConfigCreate):

    if config.field_capacity <= config.wilting_point:
        raise HTTPException(
            status_code=400,
            detail="Field capacity must be greater than wilting point"
        )

    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO crop_configurations
            (crop, growth_stage, sowing_date, field_area,
             soil_type, field_capacity, wilting_point, root_depth)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            config.crop,
            config.growth_stage,
            config.sowing_date.isoformat() if config.sowing_date else None,
            config.field_area,
            config.soil_type,
            config.field_capacity,
            config.wilting_point,
            config.root_depth
        ))

        config_id = cursor.lastrowid

    return {
        "status": "success",
        "message": "Crop configuration saved successfully",
        "configuration_id": config_id
    }


# View Crop Configurations
@app.get("/crop-configurations")
def read_crop_configurations():

    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM crop_configurations"
        ).fetchall()

    return {
        "status": "success",
        "configurations": [dict(row) for row in rows]
    }
# Save Soil Moisture Reading
@app.post("/soil-moisture")
def create_soil_moisture(reading: SoilMoistureCreate):

    with get_connection() as conn:

        if reading.field_id is not None:
            field = conn.execute(
                "SELECT id FROM fields WHERE id = ?",
                (reading.field_id,)
            ).fetchone()

            if field is None:
                raise HTTPException(
                    status_code=404,
                    detail="Field not found"
                )

        cursor = conn.execute("""
            INSERT INTO soil_moisture_readings
            (field_id, moisture, source, notes)
            VALUES (?, ?, ?, ?)
        """, (
            reading.field_id,
            reading.moisture,
            reading.source,
            reading.notes
        ))

        reading_id = cursor.lastrowid

    return {
        "status": "success",
        "message": "Soil moisture reading saved",
        "reading_id": reading_id
    }


# View Soil Moisture History
@app.get("/soil-moisture")
def get_soil_moisture():

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT * FROM soil_moisture_readings
            ORDER BY id DESC
        """).fetchall()

    return {
        "status": "success",
        "readings": [dict(row) for row in rows]
    }

# AI Irrigation Advisory API
@app.post("/advisory")
def create_advisory(request: AdvisoryRequest):

    with get_connection() as conn:
        config = conn.execute("""
            SELECT * FROM crop_configurations
            WHERE id = ?
        """, (request.field_id,)).fetchone()

    if config is None:
        raise HTTPException(
            status_code=404,
            detail="Crop configuration not found"
        )

    crop_coefficients = {
        "wheat": 1.15,
        "rice": 1.10,
        "maize": 1.20,
        "mustard": 1.00,
        "tomato": 1.15
    }

    crop_name = config["crop"].lower()
    kc = crop_coefficients.get(crop_name)

    if kc is None:
        raise HTTPException(
            status_code=400,
            detail="Crop coefficient not configured for this crop"
        )

    try:
        result = generate_irrigation_advisory(
            field_capacity=config["field_capacity"],
            wilting_point=config["wilting_point"],
            current_moisture=request.current_moisture,
            root_depth=config["root_depth"],
            et0=request.et0,
            crop_coefficient=kc,
            depletion_fraction=0.5,
            field_area=config["field_area"],
            forecast_rain=request.forecast_rain
        )

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return {
        "status": "success",
        "advisory": result
    }# AI Irrigation Advisory API
@app.post("/advisory")
def create_advisory(request: AdvisoryRequest):

    with get_connection() as conn:
        config = conn.execute("""
            SELECT * FROM crop_configurations
            WHERE id = ?
        """, (request.field_id,)).fetchone()

    if config is None:
        raise HTTPException(
            status_code=404,
            detail="Crop configuration not found"
        )

    crop_coefficients = {
        "wheat": 1.15,
        "rice": 1.10,
        "maize": 1.20,
        "mustard": 1.00,
        "tomato": 1.15
    }

    crop_name = config["crop"].lower()
    kc = crop_coefficients.get(crop_name)

    if kc is None:
        raise HTTPException(
            status_code=400,
            detail="Crop coefficient not configured for this crop"
        )

    try:
        result = generate_irrigation_advisory(
            field_capacity=config["field_capacity"],
            wilting_point=config["wilting_point"],
            current_moisture=request.current_moisture,
            root_depth=config["root_depth"],
            et0=request.et0,
            crop_coefficient=kc,
            depletion_fraction=0.5,
            field_area=config["field_area"],
            forecast_rain=request.forecast_rain
        )

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return {
        "status": "success",
        "advisory": result
    }
@app.get("/reports")
def get_all_reports():

    with get_connection() as conn:
        reports = conn.execute("""
            SELECT * FROM reports
            ORDER BY created_at DESC
        """).fetchall()

    return {
        "status": "success",
        "total_reports": len(reports),
        "reports": [dict(report) for report in reports]
    }
@app.get("/dashboard-summary")
def dashboard_summary():

    with get_connection() as conn:
        total_fields = conn.execute(
            "SELECT COUNT(*) FROM fields"
        ).fetchone()[0]

        total_crops = conn.execute(
            "SELECT COUNT(*) FROM crop_configurations"
        ).fetchone()[0]

        total_readings = conn.execute(
            "SELECT COUNT(*) FROM soil_moisture_readings"
        ).fetchone()[0]

        total_reports = conn.execute(
            "SELECT COUNT(*) FROM reports"
        ).fetchone()[0]

    return {
        "status": "success",
        "summary": {
            "total_fields": total_fields,
            "total_crop_configurations": total_crops,
            "total_soil_readings": total_readings,
            "total_reports": total_reports
        }
    }
@app.get("/soil-moisture/{field_id}/latest")
def get_latest_soil_moisture(field_id: int):

    with get_connection() as conn:
        readings = conn.execute("""
            SELECT * FROM soil_moisture_readings
            WHERE field_id = ?
            ORDER BY created_at DESC
            LIMIT 10
        """, (field_id,)).fetchall()

    return {
        "status": "success",
        "field_id": field_id,
        "readings": [dict(row) for row in readings]
    }
@app.post("/reports")
def create_report(report: dict):

    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO reports (report_data)
            VALUES (?)
        """, (json.dumps(report),))

        report_id = cursor.lastrowid

    return {
        "status": "success",
        "message": "Report saved successfully",
        "report_id": report_id
    }

@app.get("/weather")
def get_weather(latitude: float, longitude: float):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,relative_humidity_2m,"
            "apparent_temperature,precipitation,"
            "weather_code,wind_speed_10m"
        ),
        "daily": (
            "weather_code,temperature_2m_max,"
            "temperature_2m_min,precipitation_sum,"
            "precipitation_probability_max"
        ),
        "forecast_days": 5,
        "timezone": "auto"
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()

    except requests.RequestException as e:
        raise HTTPException(
            status_code=502,
            detail=f"Weather service unavailable: {str(e)}"
        )
@app.post("/hour-prediction")
def hour_prediction(data: dict):

    current = float(data.get("current_moisture", 0))
    change = float(data.get("expected_change", 0))

    if not 0 <= current <= 100:
        raise HTTPException(400, "Moisture must be between 0 and 100.")

    if not -10 <= change <= 10:
        raise HTTPException(400, "Expected change must be between -10 and 10.")

    hours = list(range(0, 25, 4))

    forecast = [
        {
            "Hours Ahead": hour,
            "Soil Moisture (%)": round(
                max(0, min(100, current + change * hour / 24)), 2
            )
        }
        for hour in hours
    ]

    return {
        "status": "success",
        "forecast": forecast
    }
