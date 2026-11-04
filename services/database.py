import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "aiml_farmer.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    with get_connection() as conn:

        # Fields Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS fields (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                field_name TEXT NOT NULL,
                area REAL NOT NULL,
                location TEXT,
                crop TEXT,
                soil_type TEXT,
                irrigation_method TEXT
            )
        """)

        # Crop Configurations Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS crop_configurations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                crop TEXT NOT NULL,
                growth_stage TEXT,
                sowing_date TEXT,
                field_area REAL,
                soil_type TEXT,
                field_capacity REAL,
                wilting_point REAL,
                root_depth REAL
            )
        """)

        # Reports Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Soil Moisture Readings Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS soil_moisture_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                field_id INTEGER,
                moisture REAL NOT NULL,
                source TEXT DEFAULT 'manual',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (field_id) REFERENCES fields(id)
            )
        """)


# Save Field
def save_field(field):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO fields
            (field_name, area, location, crop, soil_type, irrigation_method)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            field["field_name"],
            field["area"],
            field.get("location", ""),
            field.get("crop", ""),
            field.get("soil_type", ""),
            field.get("irrigation_method", "")
        ))


# Get Fields
def get_fields():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM fields ORDER BY id DESC"
        ).fetchall()

        return [dict(row) for row in rows]


# Save Crop Configuration
def save_crop_configuration(config):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO crop_configurations
            (crop, growth_stage, sowing_date, field_area, soil_type,
             field_capacity, wilting_point, root_depth)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            config["crop"],
            config["growth_stage"],
            config["sowing_date"],
            config["field_area"],
            config["soil_type"],
            config["field_capacity"],
            config["wilting_point"],
            config["root_depth"]
        ))


# Get Crop Configurations
def get_crop_configurations():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT * FROM crop_configurations ORDER BY id DESC
        """).fetchall()

        return [dict(row) for row in rows]


# Save Report
def save_report(report):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO reports (report_data) VALUES (?)",
            (json.dumps(report, default=str),)
        )


# Get Reports
def get_reports():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT * FROM reports ORDER BY id DESC
        """).fetchall()

        return [
            {
                "id": row["id"],
                "report": json.loads(row["report_data"]),
                "created_at": row["created_at"]
            }
            for row in rows
        ]


# Initialize Database
initialize_database()
