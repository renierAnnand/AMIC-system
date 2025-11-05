"""
AMIC Work Order Management & FRACAS System - Streamlit Prototype
Single-file app with SQLite backend, cascading dropdowns, rules engine, and dashboards.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import json
import sqlite3
from sqlalchemy import create_engine, inspect, text, Column, String, Integer, Date, Float, Text, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool
import altair as alt
import io
import hashlib
from typing import List, Dict, Tuple, Optional

# ============================================================================
# CONFIG & SESSION STATE
# ============================================================================

st.set_page_config(
    page_title="AMIC FRACAS System",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "app_initialized" not in st.session_state:
    st.session_state.app_initialized = False
if "current_user" not in st.session_state:
    st.session_state.current_user = "demo_tech"
if "current_role" not in st.session_state:
    st.session_state.current_role = "Technician"

# ============================================================================
# DATABASE SETUP
# ============================================================================

import os

# Use /tmp for Streamlit Cloud, local path for development
if os.path.exists('/tmp'):
    DB_FILE = "/tmp/amic_fracas.db"
else:
    DB_FILE = "./amic_fracas.db"

@st.cache_resource
def get_engine():
    """Get or create SQLAlchemy engine."""
    engine = create_engine(
        f"sqlite:///{DB_FILE}",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    return engine

def init_db():
    """Initialize database schema."""
    engine = get_engine()
    
    with engine.begin() as conn:
        # Vehicles
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS vehicles (
                vehicle_id TEXT PRIMARY KEY,
                vin TEXT UNIQUE,
                make TEXT,
                model TEXT,
                year INTEGER,
                vehicle_type TEXT,
                owning_unit TEXT,
                in_service_dt DATE,
                status TEXT DEFAULT 'Active'
            )
        """))
        
        # Work Orders
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS work_orders (
                wo_id TEXT PRIMARY KEY,
                status TEXT DEFAULT 'Open',
                created_dt DATE NOT NULL,
                completed_dt DATE,
                created_by TEXT,
                assigned_to TEXT,
                workshop TEXT,
                sector TEXT,
                vehicle_id TEXT,
                vin TEXT,
                model TEXT,
                vehicle_type TEXT,
                owning_unit TEXT,
                system TEXT,
                subsystem TEXT,
                component TEXT,
                failure_mode TEXT,
                failure_code TEXT,
                cause_code TEXT,
                resolution_code TEXT,
                cause_text TEXT,
                action_text TEXT,
                notes TEXT,
                labor_hours FLOAT DEFAULT 0,
                parts_cost FLOAT DEFAULT 0,
                total_cost FLOAT DEFAULT 0,
                downtime_hours FLOAT DEFAULT 0,
                attachments_n INTEGER DEFAULT 0,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id)
            )
        """))
        
        # Catalogue
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS catalogue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                system TEXT,
                subsystem TEXT,
                component TEXT,
                failure_mode TEXT,
                recommended_action TEXT,
                failure_code TEXT,
                cause_code TEXT,
                resolution_code TEXT
            )
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_catalogue_combo 
            ON catalogue(system, subsystem, component, failure_mode)
        """))
        
        # FRACAS Cases
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS fracas_cases (
                case_id TEXT PRIMARY KEY,
                open_dt DATE NOT NULL,
                due_dt DATE,
                close_dt DATE,
                status TEXT DEFAULT 'Open',
                severity TEXT,
                owner TEXT,
                problem_statement TEXT,
                scope TEXT,
                linked_wo_ids TEXT,
                failure_codes TEXT,
                cause_codes TEXT,
                resolution_codes TEXT,
                verification_method TEXT,
                validation_result TEXT,
                lessons_learned TEXT
            )
        """))
        
        # FRACAS Actions
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS fracas_actions (
                action_id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL,
                action_type TEXT,
                action_text TEXT,
                owner TEXT,
                due_dt DATE,
                status TEXT DEFAULT 'Open',
                FOREIGN KEY (case_id) REFERENCES fracas_cases(case_id)
            )
        """))
        
        # Rules Config
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS rules_config (
                rule_id TEXT PRIMARY KEY,
                name TEXT,
                enabled BOOLEAN DEFAULT 1,
                params TEXT,
                severity TEXT
            )
        """))
        
        # Users
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                role TEXT,
                workshop TEXT
            )
        """))
        
        # Workshops
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS workshops (
                workshop TEXT PRIMARY KEY,
                sector TEXT
            )
        """))
    
    # Check if data seeded
    with engine.begin() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM vehicles"))
        if result.scalar() == 0:
            seed_data(engine)

def seed_data(engine):
    """Seed database with demo data."""
    
    # Seed workshops
    workshops_data = [
        ("Workshop A", "North"),
        ("Workshop B", "South"),
        ("Workshop C", "Central"),
    ]
    
    # Seed users
    users_data = [
        ("tech_001", "Technician", "Workshop A"),
        ("tech_002", "Technician", "Workshop B"),
        ("supervisor_001", "Supervisor", "Workshop A"),
        ("supervisor_002", "Supervisor", "Workshop B"),
        ("reliability_001", "Reliability", "Workshop C"),
        ("quality_001", "Quality", "Workshop A"),
        ("demo_tech", "Technician", "Workshop A"),
    ]
    
    # Seed vehicles
    makes = ["Toyota", "Nissan", "Hyundai"]
    models = {
        "Toyota": ["Hilux", "Land Cruiser", "Hiace"],
        "Nissan": ["Patrol", "Navara", "Urvan"],
        "Hyundai": ["HD65", "H100", "Solaris"]
    }
    vehicle_types = ["Pickup", "SUV", "Van", "Bus"]
    owning_units = ["Unit A", "Unit B", "Unit C", "Unit D"]
    
    vehicles_data = []
    np.random.seed(42)
    for i in range(15):
        make = np.random.choice(makes)
        model = np.random.choice(models[make])
        vehicle_id = f"VEH-{i+1:04d}"
        vin = f"VIN{i+1:010d}"
        year = np.random.randint(2017, 2024)
        # Convert to date string for SQLite
        in_service_date = (datetime.now() - timedelta(days=np.random.randint(365, 2000))).strftime('%Y-%m-%d')
        
        vehicles_data.append({
            "vehicle_id": vehicle_id,
            "vin": vin,
            "make": make,
            "model": model,
            "year": year,
            "vehicle_type": np.random.choice(vehicle_types),
            "owning_unit": np.random.choice(owning_units),
            "in_service_dt": in_service_date,
            "status": "Active"
        })
    
    # Seed rules config
    rules_data = [
        ("R1", "Repeats (same vehicle + code)", True, json.dumps({"days": 90, "min_count": 2}), "Medium"),
        ("R2", "Surge Detection (model + code)", True, json.dumps({"days": 30, "sigma": 2.0}), "High"),
        ("R3", "High Downtime", True, json.dumps({"threshold_hours": 72}), "High"),
        ("R4", "Cost Spike", True, json.dumps({"sigma": 3.0}), "Medium"),
        ("R5", "Safety Critical Systems", True, json.dumps({"systems": ["Safety", "Brakes", "Steering"]}), "Critical"),
        ("R6", "Parts-driven", True, json.dumps({"min_count": 3, "days": 30}), "Medium"),
        ("R7", "Data Quality (missing codes)", True, json.dumps({}), "Low"),
    ]
    
    with engine.begin() as conn:
        for workshop, sector in workshops_data:
            conn.execute(text(
                "INSERT OR REPLACE INTO workshops (workshop, sector) VALUES (:w, :s)"
            ), {"w": workshop, "s": sector})
        
        for username, role, workshop in users_data:
            conn.execute(text(
                "INSERT OR REPLACE INTO users (username, role, workshop) VALUES (:u, :r, :w)"
            ), {"u": username, "r": role, "w": workshop})
        
        for veh in vehicles_data:
            conn.execute(text(
                """INSERT INTO vehicles (vehicle_id, vin, make, model, year, vehicle_type, 
                   owning_unit, in_service_dt, status) 
                   VALUES (:vid, :vin, :make, :model, :year, :vtype, :ou, :isd, :status)"""
            ), veh)
        
        for rule in rules_data:
            conn.execute(text(
                """INSERT OR REPLACE INTO rules_config (rule_id, name, enabled, params, severity)
                   VALUES (:rid, :name, :enabled, :params, :sev)"""
            ), {"rid": rule[0], "name": rule[1], "enabled": rule[2], "params": rule[3], "sev": rule[4]})

def import_catalogue_from_excel(file_path: str) -> Tuple[int, List[str]]:
    """Import FRACAS catalogue from Excel."""
    engine = get_engine()
    
    try:
        df = pd.read_excel(file_path, sheet_name="FRACAS_FailureMode_Catalogue")
        df = df.dropna(subset=["System", "Subsystem", "Component", "Failure Mode"])
        df = df.fillna("")
        
        # Generate codes if not present
        df["failure_code"] = df["System"].str[:2].str.upper() + "-" + \
                              df["Component"].str[:3].str.upper() + \
                              df.index.astype(str).str.zfill(3)
        df["cause_code"] = df["Subsystem"].str[:2].str.upper() + "C" + \
                           df.index.astype(str).str.zfill(3)
        df["resolution_code"] = "RES-" + df.index.astype(str).str.zfill(4)
        
        # Get required columns with defaults
        columns_to_use = ["System", "Subsystem", "Component", "Failure Mode", 
                         "Recommended Action", "failure_code", "cause_code", "resolution_code"]
        
        df_cleaned = df[columns_to_use].copy()
        
        duplicates = []
        with engine.begin() as conn:
            # Clear existing catalogue
            conn.execute(text("DELETE FROM catalogue"))
            
            for idx, row in df_cleaned.iterrows():
                # Check duplicate key
                dup_key = f"{row['System']}-{row['Subsystem']}-{row['Component']}-{row['Failure Mode']}"
                
                conn.execute(text("""
                    INSERT INTO catalogue (system, subsystem, component, failure_mode, 
                                         recommended_action, failure_code, cause_code, resolution_code)
                    VALUES (:sys, :sub, :comp, :fm, :action, :fc, :cc, :rc)
                """), {
                    "sys": row["System"],
                    "sub": row["Subsystem"],
                    "comp": row["Component"],
                    "fm": row["Failure Mode"],
                    "action": row["Recommended Action"],
                    "fc": row["failure_code"],
                    "cc": row["cause_code"],
                    "rc": row["resolution_code"]
                })
        
        return len(df_cleaned), duplicates
    
    except Exception as e:
        return 0, [str(e)]

def import_work_orders_from_excel(file_path: str) -> Tuple[int, List[str]]:
    """Import work orders from Excel with proper mapping."""
    engine = get_engine()
    warnings = []
    count = 0
    
    try:
        # Try different sheet names and formats
        sheet_name = None
        excel_file = pd.ExcelFile(file_path)
        
        # Look for work order data (usually has wo_id, vehicle, system, etc.)
        for sheet in excel_file.sheet_names:
            df_test = pd.read_excel(file_path, sheet_name=sheet, nrows=1)
            if len(df_test.columns) > 5:
                sheet_name = sheet
                break
        
        if sheet_name is None:
            sheet_name = excel_file.sheet_names[0]
        
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # Skip header rows (rows with description text)
        df = df.iloc[1:].reset_index(drop=True)
        df = df.dropna(how='all')
        df = df.fillna("")
        
        # Get vehicles for linking
        vehicles_df = get_vehicles_list()
        vehicle_map = {v: vid for v, vid in zip(vehicles_df["vin"], vehicles_df["vehicle_id"])}
        
        users = get_users_list()
        workshops = get_workshops_list()
        
        with engine.begin() as conn:
            for idx, row in df.iterrows():
                try:
                    # Skip empty rows
                    if len(row.astype(str).str.strip().unique()) <= 1:
                        continue
                    
                    # Extract data with flexible column mapping
                    vehicle_id = None
                    system = None
                    component = None
                    failure_mode = None
                    cause = None
                    resolution = None
                    
                    # Try to map columns
                    for col in df.columns:
                        col_lower = str(col).lower()
                        val = str(row[col]).strip() if pd.notna(row[col]) else ""
                        
                        if 'asset' in col_lower or 'vehicle' in col_lower:
                            if val and val != "nan":
                                vehicle_id = val if val.startswith("VEH") else list(vehicles_df["vehicle_id"].values)[0]
                        elif 'system' in col_lower or 'group' in col_lower:
                            if val and val != "nan":
                                system = val
                        elif 'component' in col_lower or 'name' in col_lower:
                            if val and val != "nan":
                                component = val
                        elif 'failure' in col_lower and 'code' not in col_lower:
                            if val and val != "nan":
                                failure_mode = val
                        elif 'cause' in col_lower and 'code' not in col_lower:
                            if val and val != "nan":
                                cause = val
                        elif 'resolution' in col_lower and 'code' not in col_lower:
                            if val and val != "nan":
                                resolution = val
                    
                    # Use first vehicle if not found
                    if not vehicle_id:
                        vehicle_id = vehicles_df["vehicle_id"].iloc[0] if len(vehicles_df) > 0 else "VEH-0001"
                    
                    # Get vehicle info
                    vin = vehicles_df[vehicles_df["vehicle_id"] == vehicle_id]["vin"].iloc[0] if vehicle_id in vehicles_df["vehicle_id"].values else ""
                    model = vehicles_df[vehicles_df["vehicle_id"] == vehicle_id]["model"].iloc[0] if vehicle_id in vehicles_df["vehicle_id"].values else ""
                    vehicle_type = vehicles_df[vehicles_df["vehicle_id"] == vehicle_id]["vehicle_type"].iloc[0] if vehicle_id in vehicles_df["vehicle_id"].values else ""
                    owning_unit = vehicles_df[vehicles_df["vehicle_id"] == vehicle_id]["owning_unit"].iloc[0] if vehicle_id in vehicles_df["vehicle_id"].values else ""
                    
                    # Try to get codes from catalogue
                    failure_code = ""
                    cause_code = ""
                    resolution_code = ""
                    
                    if system and component and failure_mode:
                        cat_result = conn.execute(text("""
                            SELECT failure_code, cause_code, resolution_code FROM catalogue 
                            WHERE system = :sys AND component = :comp AND failure_mode = :fm 
                            LIMIT 1
                        """), {"sys": system, "comp": component, "fm": failure_mode})
                        cat_row = cat_result.first()
                        if cat_row:
                            failure_code, cause_code, resolution_code = cat_row
                    
                    # Create work order
                    wo_data = {
                        "wo_id": next_id("WO", "work_orders", "wo_id"),
                        "status": "Open",
                        "created_dt": datetime.now().date().strftime('%Y-%m-%d'),
                        "created_by": users[0] if users else "import",
                        "workshop": workshops[0] if workshops else "Workshop A",
                        "vehicle_id": vehicle_id,
                        "vin": vin,
                        "model": model,
                        "vehicle_type": vehicle_type,
                        "owning_unit": owning_unit,
                        "system": system or "Unknown",
                        "component": component or "Unknown",
                        "failure_mode": failure_mode or "Unknown",
                        "failure_code": failure_code,
                        "cause_code": cause_code,
                        "resolution_code": resolution_code,
                        "cause_text": cause or "",
                        "action_text": resolution or "",
                        "notes": f"Imported from {file_path}",
                        "labor_hours": 0,
                        "parts_cost": 0,
                        "total_cost": 0,
                        "downtime_hours": 0
                    }
                    
                    cols = ", ".join(wo_data.keys())
                    placeholders = ", ".join([f":{k}" for k in wo_data.keys()])
                    conn.execute(text(f"INSERT INTO work_orders ({cols}) VALUES ({placeholders})"), wo_data)
                    
                    count += 1
                
                except Exception as row_error:
                    warnings.append(f"Row {idx + 2}: {str(row_error)[:50]}")
        
        st.cache_data.clear()
        return count, warnings
    
    except Exception as e:
        return 0, [f"Import error: {str(e)}"]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

@st.cache_data
def next_id(prefix: str, table: str, col: str = "id") -> str:
    """Generate next incremental ID."""
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT MAX({col}) FROM {table} WHERE {col} LIKE '{prefix}%'"))
        max_id = result.scalar()
        
        if max_id is None:
            num = 1
        else:
            try:
                num = int(max_id.split("-")[-1]) + 1
            except:
                num = 1
        
        return f"{prefix}-{num:06d}"

def list_systems() -> List[str]:
    """Get all systems from catalogue."""
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("SELECT DISTINCT system FROM catalogue ORDER BY system"))
        return [r[0] for r in result if r[0]]

@st.cache_data
def list_subsystems(system: str) -> List[str]:
    """Get subsystems for a system."""
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT DISTINCT subsystem FROM catalogue WHERE system = :sys ORDER BY subsystem"),
            {"sys": system}
        )
        return [r[0] for r in result if r[0]]

@st.cache_data
def list_components(system: str, subsystem: str) -> List[str]:
    """Get components for subsystem."""
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(
            text("""SELECT DISTINCT component FROM catalogue 
                    WHERE system = :sys AND subsystem = :sub ORDER BY component"""),
            {"sys": system, "sub": subsystem}
        )
        return [r[0] for r in result if r[0]]

@st.cache_data
def list_failure_modes(system: str, subsystem: str, component: str) -> List[str]:
    """Get failure modes for component."""
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(
            text("""SELECT DISTINCT failure_mode FROM catalogue 
                    WHERE system = :sys AND subsystem = :sub AND component = :comp 
                    ORDER BY failure_mode"""),
            {"sys": system, "sub": subsystem, "comp": component}
        )
        return [r[0] for r in result if r[0]]

def get_catalogue_row(system: str, subsystem: str, component: str, failure_mode: str) -> Dict:
    """Get catalogue row with codes."""
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(
            text("""SELECT recommended_action, failure_code, cause_code, resolution_code 
                    FROM catalogue WHERE system = :sys AND subsystem = :sub AND component = :comp 
                    AND failure_mode = :fm LIMIT 1"""),
            {"sys": system, "sub": subsystem, "comp": component, "fm": failure_mode}
        )
        row = result.first()
        if row:
            return {
                "recommended_action": row[0],
                "failure_code": row[1],
                "cause_code": row[2],
                "resolution_code": row[3]
            }
        return {"recommended_action": "", "failure_code": "", "cause_code": "", "resolution_code": ""}

def get_all_catalogue() -> pd.DataFrame:
    """Get all catalogue entries."""
    engine = get_engine()
    query = "SELECT system, subsystem, component, failure_mode, recommended_action, failure_code, cause_code, resolution_code FROM catalogue ORDER BY system, subsystem, component, failure_mode"
    return pd.read_sql(query, engine)

def get_vehicles_list() -> pd.DataFrame:
    """Get all vehicles."""
    engine = get_engine()
    query = "SELECT vehicle_id, vin, make, model, year, vehicle_type, owning_unit, status FROM vehicles ORDER BY vehicle_id"
    return pd.read_sql(query, engine)

def get_users_list() -> List[str]:
    """Get user list."""
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("SELECT username FROM users ORDER BY username"))
        return [r[0] for r in result]

def get_workshops_list() -> List[str]:
    """Get workshops."""
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("SELECT DISTINCT workshop FROM workshops ORDER BY workshop"))
        return [r[0] for r in result]

def save_work_order(wo_data: Dict) -> Tuple[bool, str]:
    """Save work order with validation."""
    engine = get_engine()
    
    # Validations
    errors = []
    if not wo_data.get("vehicle_id"):
        errors.append("Vehicle ID required")
    if not wo_data.get("system") or not wo_data.get("failure_mode"):
        errors.append("Classification (System → Failure Mode) required")
    if wo_data.get("status") in ["Completed", "Closed"]:
        if not wo_data.get("completed_dt"):
            errors.append(f"{wo_data['status']} status requires completion date")
        if wo_data.get("completed_dt") and wo_data.get("created_dt"):
            # Convert to date for comparison
            comp_date = wo_data["completed_dt"] if isinstance(wo_data["completed_dt"], str) else wo_data["completed_dt"].strftime('%Y-%m-%d')
            crea_date = wo_data["created_dt"] if isinstance(wo_data["created_dt"], str) else wo_data["created_dt"].strftime('%Y-%m-%d')
            if comp_date < crea_date:
                errors.append("Completion date cannot be before created date")
    
    # Check codes auto-filled
    if wo_data.get("status") in ["Completed", "Closed"]:
        if not wo_data.get("failure_code") or not wo_data.get("cause_code") or not wo_data.get("resolution_code"):
            errors.append(f"Cannot {wo_data['status'].lower()} WO: missing codes. Check classification.")
    
    if errors:
        return False, " | ".join(errors)
    
    # Convert dates to strings
    if wo_data.get("created_dt"):
        wo_data["created_dt"] = wo_data["created_dt"].strftime('%Y-%m-%d') if not isinstance(wo_data["created_dt"], str) else wo_data["created_dt"]
    if wo_data.get("completed_dt"):
        wo_data["completed_dt"] = wo_data["completed_dt"].strftime('%Y-%m-%d') if not isinstance(wo_data["completed_dt"], str) else wo_data["completed_dt"]
    
    # Calculate total cost
    wo_data["total_cost"] = (wo_data.get("parts_cost") or 0) + (wo_data.get("labor_hours") or 0) * 0
    
    try:
        with engine.begin() as conn:
            if wo_data.get("wo_id") and wo_data["wo_id"] != "NEW":
                # Update
                set_clause = ", ".join([f"{k}=:{k}" for k in wo_data.keys() if k != "wo_id"])
                conn.execute(text(f"UPDATE work_orders SET {set_clause} WHERE wo_id = :wo_id"), wo_data)
            else:
                # Insert - generate ID
                wo_id = next_id("WO", "work_orders", "wo_id")
                wo_data["wo_id"] = wo_id
                cols = ", ".join(wo_data.keys())
                placeholders = ", ".join([f":{k}" for k in wo_data.keys()])
                conn.execute(text(f"INSERT INTO work_orders ({cols}) VALUES ({placeholders})"), wo_data)
        
        return True, f"Work Order saved: {wo_data.get('wo_id', 'created')}"
    except Exception as e:
        return False, f"Error saving: {str(e)}"

def get_work_orders(filters: Dict = None) -> pd.DataFrame:
    """Get work orders with optional filters."""
    engine = get_engine()
    query = "SELECT * FROM work_orders WHERE 1=1"
    params = {}
    
    if filters:
        if filters.get("status"):
            query += " AND status = :status"
            params["status"] = filters["status"]
        if filters.get("workshop"):
            query += " AND workshop = :workshop"
            params["workshop"] = filters["workshop"]
        if filters.get("vehicle_id"):
            query += " AND vehicle_id = :vehicle_id"
            params["vehicle_id"] = filters["vehicle_id"]
        if filters.get("system"):
            query += " AND system = :system"
            params["system"] = filters["system"]
        if filters.get("date_from"):
            query += " AND created_dt >= :date_from"
            params["date_from"] = filters["date_from"]
        if filters.get("date_to"):
            query += " AND created_dt <= :date_to"
            params["date_to"] = filters["date_to"]
    
    query += " ORDER BY created_dt DESC"
    
    with engine.connect() as conn:
        return pd.read_sql(query, conn, params=params)

def get_work_order_by_id(wo_id: str) -> Dict:
    """Get single work order."""
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM work_orders WHERE wo_id = :wo_id"), {"wo_id": wo_id})
        row = result.first()
        if row:
            return dict(row._mapping)
    return {}

def save_fracas_case(case_data: Dict) -> Tuple[bool, str]:
    """Save FRACAS case."""
    engine = get_engine()
    
    # Convert dates to strings
    if case_data.get("open_dt"):
        case_data["open_dt"] = case_data["open_dt"].strftime('%Y-%m-%d') if not isinstance(case_data["open_dt"], str) else case_data["open_dt"]
    if case_data.get("due_dt"):
        case_data["due_dt"] = case_data["due_dt"].strftime('%Y-%m-%d') if not isinstance(case_data["due_dt"], str) else case_data["due_dt"]
    if case_data.get("close_dt"):
        case_data["close_dt"] = case_data["close_dt"].strftime('%Y-%m-%d') if not isinstance(case_data["close_dt"], str) else case_data["close_dt"]
    
    try:
        with engine.begin() as conn:
            if case_data.get("case_id") and case_data["case_id"] != "NEW":
                set_clause = ", ".join([f"{k}=:{k}" for k in case_data.keys() if k != "case_id"])
                conn.execute(text(f"UPDATE fracas_cases SET {set_clause} WHERE case_id = :case_id"), case_data)
            else:
                case_id = next_id("FC", "fracas_cases", "case_id")
                case_data["case_id"] = case_id
                cols = ", ".join(case_data.keys())
                placeholders = ", ".join([f":{k}" for k in case_data.keys()])
                conn.execute(text(f"INSERT INTO fracas_cases ({cols}) VALUES ({placeholders})"), case_data)
        
        return True, f"FRACAS Case saved: {case_data.get('case_id', 'created')}"
    except Exception as e:
        return False, f"Error saving: {str(e)}"

def get_fracas_cases(filters: Dict = None) -> pd.DataFrame:
    """Get FRACAS cases."""
    engine = get_engine()
    query = "SELECT * FROM fracas_cases WHERE 1=1"
    params = {}
    
    if filters:
        if filters.get("status"):
            query += " AND status = :status"
            params["status"] = filters["status"]
        if filters.get("severity"):
            query += " AND severity = :severity"
            params["severity"] = filters["severity"]
        if filters.get("owner"):
            query += " AND owner = :owner"
            params["owner"] = filters["owner"]
    
    query += " ORDER BY open_dt DESC"
    return pd.read_sql(query, get_engine(), params=params)

def get_fracas_case_by_id(case_id: str) -> Dict:
    """Get single FRACAS case."""
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM fracas_cases WHERE case_id = :case_id"), {"case_id": case_id})
        row = result.first()
        if row:
            return dict(row._mapping)
    return {}

def get_fracas_actions(case_id: str) -> pd.DataFrame:
    """Get actions for case."""
    return pd.read_sql(
        "SELECT * FROM fracas_actions WHERE case_id = :case_id ORDER BY action_id",
        get_engine(),
        params={"case_id": case_id}
    )

def save_fracas_action(action_data: Dict) -> bool:
    """Save FRACAS action."""
    engine = get_engine()
    try:
        with engine.begin() as conn:
            if action_data.get("action_id"):
                set_clause = ", ".join([f"{k}=:{k}" for k in action_data.keys() if k != "action_id"])
                conn.execute(text(f"UPDATE fracas_actions SET {set_clause} WHERE action_id = :action_id"), action_data)
            else:
                cols = ", ".join(action_data.keys())
                placeholders = ", ".join([f":{k}" for k in action_data.keys()])
                conn.execute(text(f"INSERT INTO fracas_actions ({cols}) VALUES ({placeholders})"), action_data)
        return True
    except:
        return False

def delete_fracas_action(action_id: int) -> bool:
    """Delete FRACAS action."""
    engine = get_engine()
    try:
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM fracas_actions WHERE action_id = :aid"), {"aid": action_id})
        return True
    except:
        return False

def run_rules(rules_config: List[Dict]) -> pd.DataFrame:
    """Run all enabled rules and return hits."""
    engine = get_engine()
    hits = []
    
    # Get all work orders
    wo_df = pd.read_sql("SELECT * FROM work_orders", engine)
    if len(wo_df) == 0:
        return pd.DataFrame()
    
    wo_df["created_dt"] = pd.to_datetime(wo_df["created_dt"])
    wo_df["completed_dt"] = pd.to_datetime(wo_df["completed_dt"], errors="coerce")
    
    for rule in rules_config:
        if not rule.get("enabled"):
            continue
        
        rule_id = rule.get("rule_id", "")
        name = rule.get("name", "")
        severity = rule.get("severity", "Medium")
        params = json.loads(rule.get("params", "{}"))
        
        # R1: Repeats
        if rule_id == "R1":
            days = params.get("days", 90)
            min_count = params.get("min_count", 2)
            cutoff = datetime.now() - timedelta(days=days)
            recent = wo_df[wo_df["created_dt"] >= cutoff]
            
            repeats = recent.groupby(["vehicle_id", "failure_code"]).size()
            for (vid, fc), count in repeats[repeats >= min_count].items():
                sample_wos = recent[(recent["vehicle_id"] == vid) & (recent["failure_code"] == fc)]["wo_id"].tolist()
                hits.append({
                    "rule_id": rule_id,
                    "description": f"Repeat failure: {fc} on vehicle {vid}",
                    "severity": severity,
                    "affected_vehicle": vid,
                    "failure_code": fc,
                    "count": count,
                    "window_days": days,
                    "sample_wo_ids": ", ".join(sample_wos[:3])
                })
        
        # R2: Surge Detection
        elif rule_id == "R2":
            days_recent = params.get("days", 30)
            sigma = params.get("sigma", 2.0)
            cutoff_recent = datetime.now() - timedelta(days=days_recent)
            cutoff_baseline = datetime.now() - timedelta(days=180)
            
            recent_30 = wo_df[wo_df["created_dt"] >= cutoff_recent]
            baseline = wo_df[(wo_df["created_dt"] >= cutoff_baseline) & (wo_df["created_dt"] < cutoff_recent)]
            
            if len(baseline) > 0:
                baseline_counts = baseline.groupby("failure_code").size()
                mean = baseline_counts.mean()
                std = baseline_counts.std()
                threshold = mean + sigma * std
                
                recent_counts = recent_30.groupby("failure_code").size()
                for fc, count in recent_counts.items():
                    if count > threshold and threshold > 0:
                        hits.append({
                            "rule_id": rule_id,
                            "description": f"Surge detected: {fc} ({count} in {days_recent} days vs baseline {mean:.1f})",
                            "severity": severity,
                            "affected_vehicle": "",
                            "failure_code": fc,
                            "count": count,
                            "window_days": days_recent,
                            "sample_wo_ids": ", ".join(recent_30[recent_30["failure_code"] == fc]["wo_id"].tolist()[:3])
                        })
        
        # R3: High Downtime
        elif rule_id == "R3":
            threshold = params.get("threshold_hours", 72)
            high_dt = wo_df[wo_df["downtime_hours"] > threshold]
            for _, row in high_dt.iterrows():
                hits.append({
                    "rule_id": rule_id,
                    "description": f"High downtime: {row['wo_id']} ({row['downtime_hours']}h > {threshold}h)",
                    "severity": severity,
                    "affected_vehicle": row["vehicle_id"],
                    "failure_code": row["failure_code"],
                    "count": 1,
                    "window_days": 0,
                    "sample_wo_ids": row["wo_id"]
                })
        
        # R4: Cost Spike
        elif rule_id == "R4":
            sigma = params.get("sigma", 3.0)
            monthly = wo_df.groupby([wo_df["created_dt"].dt.to_period("M"), "failure_code"])["total_cost"].sum()
            all_costs = wo_df.groupby("failure_code")["total_cost"].mean()
            std_costs = wo_df.groupby("failure_code")["total_cost"].std()
            
            for (period, fc), cost in monthly.items():
                if fc in all_costs.index:
                    threshold = all_costs[fc] + sigma * (std_costs[fc] or 0)
                    if cost > threshold and threshold > 0:
                        hits.append({
                            "rule_id": rule_id,
                            "description": f"Cost spike: {fc} in {period} (${cost:.2f} > threshold)",
                            "severity": severity,
                            "affected_vehicle": "",
                            "failure_code": fc,
                            "count": 1,
                            "window_days": 30,
                            "sample_wo_ids": ""
                        })
        
        # R5: Safety Critical
        elif rule_id == "R5":
            systems = params.get("systems", ["Safety", "Brakes", "Steering"])
            safety_wos = wo_df[wo_df["system"].isin(systems)]
            for _, row in safety_wos.iterrows():
                hits.append({
                    "rule_id": rule_id,
                    "description": f"Safety critical: {row['system']} on {row['vehicle_id']}",
                    "severity": severity,
                    "affected_vehicle": row["vehicle_id"],
                    "failure_code": row["failure_code"],
                    "count": 1,
                    "window_days": 0,
                    "sample_wo_ids": row["wo_id"]
                })
        
        # R7: Data Quality
        elif rule_id == "R7":
            closed_wo = wo_df[wo_df["status"] == "Closed"]
            missing_codes = closed_wo[(closed_wo["failure_code"].isna()) | (closed_wo["cause_code"].isna())]
            for _, row in missing_codes.iterrows():
                hits.append({
                    "rule_id": rule_id,
                    "description": f"Data quality: {row['wo_id']} closed but missing codes",
                    "severity": severity,
                    "affected_vehicle": row["vehicle_id"],
                    "failure_code": row["failure_code"],
                    "count": 1,
                    "window_days": 0,
                    "sample_wo_ids": row["wo_id"]
                })
    
    return pd.DataFrame(hits) if hits else pd.DataFrame()

# ============================================================================
# PAGE: WORK ORDERS
# ============================================================================

def page_work_orders():
    """Work Orders management page."""
    st.header("📋 Work Orders")
    
    tab1, tab2, tab3 = st.tabs(["Create / Edit", "List & Search", "Vehicle History"])
    
    with tab1:
        st.subheader("Create or Edit Work Order")
        
        with st.form("work_order_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                created_dt = st.date_input("Created Date", datetime.now())
                created_by = st.selectbox("Created By", get_users_list())
                workshop = st.selectbox("Workshop", get_workshops_list())
            
            with col2:
                assigned_to = st.selectbox("Assigned To", [""] + get_users_list())
                sector = st.text_input("Sector")
                status = st.selectbox("Status", ["Open", "In Progress", "Completed", "Closed"])
            
            with col3:
                completed_dt = None
                if status in ["Completed", "Closed"]:
                    completed_dt = st.date_input("Completion Date", datetime.now())
                else:
                    st.text_input("Completion Date (disabled)", value="", disabled=True)
            
            st.divider()
            
            # Vehicle selection
            col1, col2 = st.columns(2)
            with col1:
                vehicle_mode = st.radio("Find Vehicle by:", ["Vehicle ID", "VIN"])
            
            vehicles_df = get_vehicles_list()
            vehicle_dict = {row["vehicle_id"]: f"{row['vehicle_id']} - {row['make']} {row['model']} ({row['year']})" 
                          for _, row in vehicles_df.iterrows()}
            vin_dict = {row["vin"]: f"{row['vin']} - {row['vehicle_id']}" 
                       for _, row in vehicles_df.iterrows()}
            
            vehicle_id = None
            vin = None
            with col1:
                if vehicle_mode == "Vehicle ID":
                    selected_display = st.selectbox("Select Vehicle", [""] + list(vehicle_dict.values()))
                    if selected_display:
                        vehicle_id = selected_display.split(" - ")[0]
                        vin = vehicles_df[vehicles_df["vehicle_id"] == vehicle_id]["vin"].iloc[0]
                else:
                    selected_display = st.selectbox("Select by VIN", [""] + list(vin_dict.values()))
                    if selected_display:
                        vin = selected_display.split(" - ")[0]
                        vehicle_id = selected_display.split(" - ")[1]
            
            st.divider()
            st.subheader("Fault Classification")
            
            col1, col2, col3, col4 = st.columns(4)
            
            system = None
            subsystem = None
            component = None
            failure_mode = None
            
            with col1:
                systems = [""] + list_systems()
                system = st.selectbox("System", systems)
            
            with col2:
                subsystems = []
                if system:
                    subsystems = [""] + list_subsystems(system)
                subsystem = st.selectbox("Subsystem", subsystems)
            
            with col3:
                components = []
                if system and subsystem:
                    components = [""] + list_components(system, subsystem)
                component = st.selectbox("Component", components)
            
            with col4:
                failure_modes = []
                if system and subsystem and component:
                    failure_modes = [""] + list_failure_modes(system, subsystem, component)
                failure_mode = st.selectbox("Failure Mode", failure_modes)
            
            # Auto-fill codes
            recommended_action = ""
            failure_code = ""
            cause_code = ""
            resolution_code = ""
            
            if failure_mode and system and subsystem and component:
                cat_row = get_catalogue_row(system, subsystem, component, failure_mode)
                recommended_action = cat_row.get("recommended_action", "")
                failure_code = cat_row.get("failure_code", "")
                cause_code = cat_row.get("cause_code", "")
                resolution_code = cat_row.get("resolution_code", "")
            
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Recommended Action (auto-filled)", value=recommended_action, disabled=True)
            
            st.divider()
            st.subheader("Codes (Auto-filled from Catalogue)")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.text_input("Failure Code", value=failure_code, disabled=True)
            with col2:
                st.text_input("Cause Code", value=cause_code, disabled=True)
            with col3:
                st.text_input("Resolution Code", value=resolution_code, disabled=True)
            
            st.divider()
            st.subheader("Cause & Action Details")
            
            col1, col2 = st.columns(2)
            with col1:
                cause_text = st.text_area("Cause Text", height=100)
            with col2:
                action_text = st.text_area("Action Text", height=100)
            
            notes = st.text_area("Additional Notes", height=80)
            
            st.divider()
            st.subheader("Costs & Downtime")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                labor_hours = st.number_input("Labor Hours", value=0.0, min_value=0.0)
            with col2:
                parts_cost = st.number_input("Parts Cost ($)", value=0.0, min_value=0.0)
            with col3:
                downtime_hours = st.number_input("Downtime Hours", value=0.0, min_value=0.0)
            with col4:
                attachments_n = st.number_input("Attachments", value=0, min_value=0)
            
            st.divider()
            
            submitted = st.form_submit_button("💾 Save Work Order", use_container_width=True)
            
            if submitted:
                if not vehicle_id:
                    st.error("❌ Please select a vehicle")
                else:
                    wo_data = {
                        "status": status,
                        "created_dt": created_dt,
                        "completed_dt": completed_dt,
                        "created_by": created_by,
                        "assigned_to": assigned_to if assigned_to else None,
                        "workshop": workshop,
                        "sector": sector,
                        "vehicle_id": vehicle_id,
                        "vin": vin,
                        "system": system,
                        "subsystem": subsystem,
                        "component": component,
                        "failure_mode": failure_mode,
                        "failure_code": failure_code if failure_code else None,
                        "cause_code": cause_code if cause_code else None,
                        "resolution_code": resolution_code if resolution_code else None,
                        "cause_text": cause_text,
                        "action_text": action_text,
                        "notes": notes,
                        "labor_hours": labor_hours,
                        "parts_cost": parts_cost,
                        "downtime_hours": downtime_hours,
                        "attachments_n": attachments_n
                    }
                    
                    success, msg = save_work_order(wo_data)
                    if success:
                        st.success(f"✅ {msg}")
                        st.cache_data.clear()
                    else:
                        st.error(f"❌ {msg}")
    
    with tab2:
        st.subheader("Work Order List & Search")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.multiselect("Status", ["Open", "In Progress", "Completed", "Closed"])
        with col2:
            workshop_filter = st.multiselect("Workshop", get_workshops_list())
        with col3:
            date_range = st.date_input("Date Range", value=(datetime.now() - timedelta(days=90), datetime.now()), max_value=datetime.now())
        
        col1, col2 = st.columns(2)
        with col1:
            vehicle_filter = st.text_input("Vehicle ID (partial)")
        with col2:
            system_filter = st.selectbox("System", [""] + list_systems())
        
        filters = {}
        if status_filter:
            for status in status_filter:
                temp_filters = filters.copy()
                temp_filters["status"] = status
                if not filters:
                    filters = temp_filters
        
        if workshop_filter:
            for ws in workshop_filter:
                temp_filters = filters.copy()
                temp_filters["workshop"] = ws
                if not filters:
                    filters = temp_filters
        
        if vehicle_filter:
            filters["vehicle_id"] = f"%{vehicle_filter}%"
        if system_filter:
            filters["system"] = system_filter
        
        filters["date_from"] = date_range[0]
        filters["date_to"] = date_range[1]
        
        wos = get_work_orders(filters) if filters else get_work_orders()
        
        if len(wos) > 0:
            st.dataframe(wos[["wo_id", "status", "created_dt", "vehicle_id", "system", "failure_mode", "workshop", "assigned_to", "total_cost", "downtime_hours"]], use_container_width=True, height=400)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("📥 Export to CSV", use_container_width=True):
                    csv = wos.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"work_orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
        else:
            st.info("No work orders found with current filters.")
    
    with tab3:
        st.subheader("Vehicle History")
        vehicles_df = get_vehicles_list()
        vehicle_options = [f"{row['vehicle_id']} - {row['vin']}" for _, row in vehicles_df.iterrows()]
        
        selected_vehicle = st.selectbox("Select Vehicle", vehicle_options)
        if selected_vehicle:
            vehicle_id = selected_vehicle.split(" - ")[0]
            wos = get_work_orders({"vehicle_id": vehicle_id})
            
            if len(wos) > 0:
                st.write(f"**Total WOs:** {len(wos)} | **Open:** {len(wos[wos['status']=='Open'])} | **Closed:** {len(wos[wos['status']=='Closed'])}")
                st.dataframe(wos[["wo_id", "status", "created_dt", "system", "failure_mode", "total_cost", "downtime_hours"]], use_container_width=True)
            else:
                st.info(f"No work orders for vehicle {vehicle_id}")

# ============================================================================
# PAGE: CATALOGUE
# ============================================================================

def page_catalogue():
    """FRACAS Catalogue page."""
    st.header("📚 FRACAS Codes Catalogue")
    
    tab1, tab2 = st.tabs(["Upload & Manage", "Browse Catalogue"])
    
    with tab1:
        st.subheader("Import Catalogue from Excel")
        
        uploaded_file = st.file_uploader("Choose Excel file", type=["xlsx"])
        
        if uploaded_file:
            if st.button("📤 Load to Database"):
                with st.spinner("Processing..."):
                    file_path = f"/tmp/{uploaded_file.name}"
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    count, errors = import_catalogue_from_excel(file_path)
                    
                    if count > 0:
                        st.success(f"✅ Loaded {count} catalogue entries")
                        st.cache_data.clear()
                    if errors:
                        st.warning(f"⚠️ Issues: {', '.join(errors)}")
    
    with tab2:
        st.subheader("Current Catalogue")
        
        catalogue_df = get_all_catalogue()
        
        if len(catalogue_df) > 0:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                system_filter = st.selectbox("Filter by System", ["All"] + sorted(catalogue_df["system"].unique().tolist()))
            with col2:
                if system_filter != "All":
                    subsystem_filter = st.selectbox("Filter by Subsystem", ["All"] + sorted(catalogue_df[catalogue_df["system"] == system_filter]["subsystem"].unique().tolist()))
                else:
                    subsystem_filter = "All"
            
            if system_filter != "All":
                filtered_cat = catalogue_df[catalogue_df["system"] == system_filter]
                if subsystem_filter != "All":
                    filtered_cat = filtered_cat[filtered_cat["subsystem"] == subsystem_filter]
            else:
                filtered_cat = catalogue_df
            
            st.write(f"**Showing:** {len(filtered_cat)} of {len(catalogue_df)} entries")
            st.dataframe(filtered_cat, use_container_width=True, height=500)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("📥 Export Catalogue to CSV", use_container_width=True):
                    csv = catalogue_df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"catalogue_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
        else:
            st.info("No catalogue entries loaded yet. Upload an Excel file to populate the catalogue.")

# ============================================================================
# PAGE: FRACAS CASES
# ============================================================================

def page_fracas_cases():
    """FRACAS Cases management page."""
    st.header("🔍 FRACAS Cases")
    
    tab1, tab2, tab3 = st.tabs(["Queue", "New Case", "Case Detail"])
    
    with tab1:
        st.subheader("FRACAS Cases Queue")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.multiselect("Status", ["Open", "Containment", "RCA", "Implement", "Validate", "Closed"])
        with col2:
            severity_filter = st.multiselect("Severity", ["Low", "Medium", "High", "Critical"])
        with col3:
            owner_filter = st.multiselect("Owner", get_users_list())
        
        filters = {}
        if status_filter:
            filters["status"] = status_filter[0] if len(status_filter) == 1 else None
        if severity_filter:
            filters["severity"] = severity_filter[0] if len(severity_filter) == 1 else None
        if owner_filter:
            filters["owner"] = owner_filter[0] if len(owner_filter) == 1 else None
        
        cases_df = get_fracas_cases(filters) if filters else get_fracas_cases()
        
        if len(cases_df) > 0:
            # Add overdue indicator
            today = datetime.now().date()
            cases_df["overdue"] = (cases_df["due_dt"].apply(lambda x: pd.to_datetime(x).date() if pd.notna(x) else None) < today) & (cases_df["status"] != "Closed")
            
            st.dataframe(cases_df[["case_id", "status", "severity", "owner", "open_dt", "due_dt", "problem_statement"]], use_container_width=True, height=400)
        else:
            st.info("No FRACAS cases found.")
    
    with tab2:
        st.subheader("Create New FRACAS Case")
        
        with st.form("fracas_case_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                open_dt = st.date_input("Open Date", datetime.now())
                due_dt = st.date_input("Due Date", datetime.now() + timedelta(days=30))
            
            with col2:
                status = st.selectbox("Status", ["Open", "Containment", "RCA", "Implement", "Validate", "Closed"])
                severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
            
            with col3:
                owner = st.selectbox("Owner", get_users_list())
            
            problem_statement = st.text_area("Problem Statement", height=100)
            scope = st.text_area("Scope", height=80)
            
            st.divider()
            st.subheader("Link Work Orders & Codes")
            
            # Link WOs
            wos = get_work_orders()
            if len(wos) > 0:
                wo_options = wos["wo_id"].unique().tolist()
                linked_wos = st.multiselect("Link Work Orders", wo_options)
                linked_wo_ids = ", ".join(linked_wos) if linked_wos else ""
            else:
                linked_wo_ids = ""
            
            col1, col2, col3 = st.columns(3)
            with col1:
                failure_codes = st.text_input("Failure Codes (comma-separated)")
            with col2:
                cause_codes = st.text_input("Cause Codes (comma-separated)")
            with col3:
                resolution_codes = st.text_input("Resolution Codes (comma-separated)")
            
            st.divider()
            verification_method = st.text_input("Verification Method")
            
            submitted = st.form_submit_button("💾 Create FRACAS Case", use_container_width=True)
            
            if submitted:
                case_data = {
                    "open_dt": open_dt,
                    "due_dt": due_dt,
                    "status": status,
                    "severity": severity,
                    "owner": owner,
                    "problem_statement": problem_statement,
                    "scope": scope,
                    "linked_wo_ids": linked_wo_ids,
                    "failure_codes": failure_codes,
                    "cause_codes": cause_codes,
                    "resolution_codes": resolution_codes,
                    "verification_method": verification_method
                }
                
                success, msg = save_fracas_case(case_data)
                if success:
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")
    
    with tab3:
        st.subheader("Case Detail & Actions")
        
        cases_df = get_fracas_cases()
        if len(cases_df) > 0:
            selected_case = st.selectbox("Select Case", cases_df["case_id"].unique())
            
            if selected_case:
                case = get_fracas_case_by_id(selected_case)
                
                if case:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Status", case.get("status", ""))
                    with col2:
                        st.metric("Severity", case.get("severity", ""))
                    with col3:
                        st.metric("Owner", case.get("owner", ""))
                    with col4:
                        st.metric("Days Open", (datetime.now().date() - pd.to_datetime(case.get("open_dt")).date()).days if case.get("open_dt") else "-")
                    
                    st.write(f"**Problem:** {case.get('problem_statement', '')}")
                    st.write(f"**Scope:** {case.get('scope', '')}")
                    
                    st.divider()
                    st.subheader("Linked Work Orders")
                    if case.get("linked_wo_ids"):
                        wo_ids = case["linked_wo_ids"].split(", ")
                        for wo_id in wo_ids:
                            st.write(f"• {wo_id}")
                    
                    st.divider()
                    st.subheader("Codes")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Failure Codes:** {case.get('failure_codes', '')}")
                    with col2:
                        st.write(f"**Cause Codes:** {case.get('cause_codes', '')}")
                    with col3:
                        st.write(f"**Resolution Codes:** {case.get('resolution_codes', '')}")
                    
                    st.divider()
                    st.subheader("Actions")
                    
                    actions_df = get_fracas_actions(selected_case)
                    if len(actions_df) > 0:
                        st.dataframe(actions_df[["action_id", "action_type", "action_text", "owner", "due_dt", "status"]], use_container_width=True)
                    else:
                        st.info("No actions yet.")
                    
                    with st.form("add_action_form"):
                        action_type = st.selectbox("Action Type", ["Containment", "Corrective", "Preventive"])
                        action_text = st.text_area("Action Description")
                        action_owner = st.selectbox("Action Owner", get_users_list())
                        action_due = st.date_input("Action Due Date")
                        
                        if st.form_submit_button("➕ Add Action"):
                            action_data = {
                                "case_id": selected_case,
                                "action_type": action_type,
                                "action_text": action_text,
                                "owner": action_owner,
                                "due_dt": action_due,
                                "status": "Open"
                            }
                            if save_fracas_action(action_data):
                                st.success("✅ Action added")
                            else:
                                st.error("❌ Error adding action")
                    
                    st.divider()
                    st.subheader("Verification & Validation")
                    
                    with st.form("verification_form"):
                        validation_result = st.text_area("Validation Result", value=case.get("validation_result", ""))
                        lessons_learned = st.text_area("Lessons Learned", value=case.get("lessons_learned", ""))
                        new_status = st.selectbox("Status", ["Open", "Containment", "RCA", "Implement", "Validate", "Closed"], index=["Open", "Containment", "RCA", "Implement", "Validate", "Closed"].index(case.get("status", "Open")))
                        
                        if st.form_submit_button("💾 Update Case"):
                            case["status"] = new_status
                            case["validation_result"] = validation_result
                            case["lessons_learned"] = lessons_learned
                            success, msg = save_fracas_case(case)
                            if success:
                                st.success("✅ Case updated")
                            else:
                                st.error("❌ Error updating case")
        else:
            st.info("No FRACAS cases found.")

# ============================================================================
# PAGE: RULES & DETECTION
# ============================================================================

def page_rules_detection():
    """Rules & Detection page."""
    st.header("⚙️ Rules & Detection")
    
    engine = get_engine()
    
    # Load rules config
    rules_df = pd.read_sql("SELECT * FROM rules_config ORDER BY rule_id", engine)
    rules = []
    for _, row in rules_df.iterrows():
        rules.append({
            "rule_id": row["rule_id"],
            "name": row["name"],
            "enabled": bool(row["enabled"]),
            "params": row["params"],
            "severity": row["severity"]
        })
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Rule Configuration")
    with col2:
        if st.button("▶️ Run Rules Now", use_container_width=True):
            st.session_state["run_rules_now"] = True
    
    # Display rules
    for i, rule in enumerate(rules):
        with st.expander(f"{rule['rule_id']}: {rule['name']}", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                enabled = st.checkbox("Enabled", value=rule["enabled"], key=f"enable_{rule['rule_id']}")
            with col2:
                severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"], 
                                       index=["Low", "Medium", "High", "Critical"].index(rule["severity"]),
                                       key=f"sev_{rule['rule_id']}")
            with col3:
                st.write("")  # spacer
            
            params = json.loads(rule["params"])
            new_params = {}
            
            if rule["rule_id"] == "R1":
                new_params["days"] = st.slider("Days window", 1, 365, params.get("days", 90), key=f"p_{rule['rule_id']}_1")
                new_params["min_count"] = st.slider("Min count", 1, 10, params.get("min_count", 2), key=f"p_{rule['rule_id']}_2")
            
            elif rule["rule_id"] == "R2":
                new_params["days"] = st.slider("Days window", 1, 90, params.get("days", 30), key=f"p_{rule['rule_id']}_1")
                new_params["sigma"] = st.slider("Sigma threshold", 0.5, 5.0, params.get("sigma", 2.0), key=f"p_{rule['rule_id']}_2")
            
            elif rule["rule_id"] == "R3":
                new_params["threshold_hours"] = st.slider("Downtime threshold (hours)", 1, 500, params.get("threshold_hours", 72), key=f"p_{rule['rule_id']}_1")
            
            elif rule["rule_id"] == "R4":
                new_params["sigma"] = st.slider("Sigma threshold", 0.5, 5.0, params.get("sigma", 3.0), key=f"p_{rule['rule_id']}_1")
            
            elif rule["rule_id"] == "R5":
                systems_input = st.text_input("Safety systems (comma-separated)", 
                                             ", ".join(params.get("systems", [])), key=f"p_{rule['rule_id']}_1")
                new_params["systems"] = [s.strip() for s in systems_input.split(",")]
            
            # Update rule in DB
            with engine.begin() as conn:
                conn.execute(text("""
                    UPDATE rules_config SET enabled = :enabled, severity = :severity, params = :params
                    WHERE rule_id = :rid
                """), {
                    "enabled": enabled,
                    "severity": severity,
                    "params": json.dumps(new_params) if new_params else rule["params"],
                    "rid": rule["rule_id"]
                })
    
    if st.button("💾 Save Configuration", use_container_width=True):
        st.success("✅ Rules configuration saved")
    
    st.divider()
    
    # Run rules if triggered
    if st.session_state.get("run_rules_now"):
        st.subheader("Rule Hits")
        
        with st.spinner("Running rules..."):
            hits_df = run_rules(rules)
        
        if len(hits_df) > 0:
            st.dataframe(hits_df, use_container_width=True, height=400)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📥 Export Hits to CSV", use_container_width=True):
                    csv = hits_df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"rule_hits_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            
            with col2:
                if st.button("📌 Create FRACAS Case from Hit", use_container_width=True):
                    st.info("Select a hit row from the table to create a case (multi-select in future)")
        else:
            st.info("No rule hits detected.")
        
        st.session_state["run_rules_now"] = False

# ============================================================================
# PAGE: DASHBOARDS
# ============================================================================

def page_dashboards():
    """Dashboards page."""
    st.header("📊 Dashboards")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Work Order Overview",
        "Workshop Performance",
        "Fleet Reliability (FRACAS)",
        "Emerging Issues",
        "Cost & Downtime"
    ])
    
    # Get data
    wos = get_work_orders()
    if len(wos) == 0:
        st.info("No work order data available for dashboards.")
        return
    
    with tab1:
        st.subheader("Work Order Overview")
        
        total_wos = len(wos)
        open_wos = len(wos[wos["status"] == "Open"])
        closed_wos = len(wos[wos["status"] == "Closed"])
        pct_closed = (closed_wos / total_wos * 100) if total_wos > 0 else 0
        
        # Handle dates
        wos["created_dt"] = pd.to_datetime(wos["created_dt"])
        wos["completed_dt"] = pd.to_datetime(wos["completed_dt"], errors="coerce")
        wos["close_time_days"] = (wos["completed_dt"] - wos["created_dt"]).dt.days
        avg_close_time = wos[wos["status"] == "Closed"]["close_time_days"].mean()
        avg_downtime = wos["downtime_hours"].mean()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total WOs", total_wos)
        with col2:
            st.metric("Open", open_wos)
        with col3:
            st.metric("Closed %", f"{pct_closed:.1f}%")
        with col4:
            st.metric("Avg Close (days)", f"{avg_close_time:.1f}" if not pd.isna(avg_close_time) else "N/A")
        with col5:
            st.metric("Avg Downtime (h)", f"{avg_downtime:.1f}" if not pd.isna(avg_downtime) else "N/A")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Status distribution
            status_counts = wos["status"].value_counts()
            chart_status = alt.Chart(pd.DataFrame({
                "Status": status_counts.index,
                "Count": status_counts.values
            })).mark_bar().encode(
                x="Status",
                y="Count",
                color="Status"
            ).properties(width=400, height=300)
            st.altair_chart(chart_status, use_container_width=True)
        
        with col2:
            # Workshop distribution
            workshop_counts = wos["workshop"].value_counts()
            chart_workshop = alt.Chart(pd.DataFrame({
                "Workshop": workshop_counts.index,
                "Count": workshop_counts.values
            })).mark_bar().encode(
                x="Workshop",
                y="Count",
                color="Workshop"
            ).properties(width=400, height=300)
            st.altair_chart(chart_workshop, use_container_width=True)
    
    with tab2:
        st.subheader("Workshop Performance")
        
        workshop_perf = []
        for ws in wos["workshop"].unique():
            ws_wos = wos[wos["workshop"] == ws]
            throughput = len(ws_wos)
            closed = len(ws_wos[ws_wos["status"] == "Closed"])
            avg_days = ws_wos[ws_wos["status"] == "Closed"]["close_time_days"].mean() if closed > 0 else 0
            
            workshop_perf.append({
                "Workshop": ws,
                "Throughput": throughput,
                "Closed": closed,
                "Avg Days to Close": f"{avg_days:.1f}" if not pd.isna(avg_days) else "N/A"
            })
        
        st.dataframe(pd.DataFrame(workshop_perf), use_container_width=True)
    
    with tab3:
        st.subheader("Fleet Reliability Summary (FRACAS)")
        
        num_vehicles = len(get_vehicles_list())
        failures_per_100 = (total_wos / max(num_vehicles, 1) * 100)
        avg_mttr = wos[wos["status"] == "Closed"]["close_time_days"].mean()
        
        # Repeat rate (same vehicle + code)
        repeat_rate = 0
        if len(wos) > 1:
            repeats = wos.groupby(["vehicle_id", "failure_code"]).size()
            repeat_rate = (repeats[repeats > 1].sum() / total_wos * 100) if total_wos > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Failures per 100 vehicles", f"{failures_per_100:.1f}")
        with col2:
            st.metric("MTTR (days)", f"{avg_mttr:.1f}" if not pd.isna(avg_mttr) else "N/A")
        with col3:
            st.metric("Repeat Rate %", f"{repeat_rate:.1f}%")
        with col4:
            st.metric("Fleet Size", num_vehicles)
        
        # Pareto of failure codes
        code_counts = wos["failure_code"].value_counts().head(10)
        chart_codes = alt.Chart(pd.DataFrame({
            "Failure Code": code_counts.index,
            "Count": code_counts.values
        })).mark_bar().encode(
            x="Failure Code",
            y="Count",
            color="Count"
        ).properties(width=600, height=300)
        st.altair_chart(chart_codes, use_container_width=True)
    
    with tab4:
        st.subheader("Emerging Issues")
        st.info("Latest rule runs and top surges would appear here (Rules & Detection must be run first)")
    
    with tab5:
        st.subheader("Cost & Downtime")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Cost by system
            cost_by_system = wos.groupby("system")["total_cost"].sum().sort_values(ascending=False).head(10)
            chart_cost = alt.Chart(pd.DataFrame({
                "System": cost_by_system.index,
                "Total Cost": cost_by_system.values
            })).mark_bar().encode(
                y="System",
                x="Total Cost",
                color="Total Cost"
            ).properties(width=400, height=300)
            st.altair_chart(chart_cost, use_container_width=True)
        
        with col2:
            # Downtime by workshop
            downtime_by_ws = wos.groupby("workshop")["downtime_hours"].sum()
            chart_downtime = alt.Chart(pd.DataFrame({
                "Workshop": downtime_by_ws.index,
                "Downtime Hours": downtime_by_ws.values
            })).mark_bar().encode(
                x="Workshop",
                y="Downtime Hours",
                color="Workshop"
            ).properties(width=400, height=300)
            st.altair_chart(chart_downtime, use_container_width=True)

# ============================================================================
# PAGE: DATA QUALITY
# ============================================================================

def page_data_quality():
    """Data Quality page."""
    st.header("🔍 Data Quality")
    
    engine = get_engine()
    wos = get_work_orders()
    
    if len(wos) == 0:
        st.info("No work orders to analyze.")
        return
    
    # Calculate metrics
    total_wos = len(wos)
    complete_codes = len(wos[(wos["failure_code"].notna()) & (wos["cause_code"].notna()) & (wos["resolution_code"].notna())])
    pct_complete = (complete_codes / total_wos * 100) if total_wos > 0 else 0
    
    closed_missing = len(wos[(wos["status"] == "Closed") & ((wos["failure_code"].isna()) | (wos["cause_code"].isna()))])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("% WOs with Complete Codes", f"{pct_complete:.1f}%", delta=f"{complete_codes} records")
    with col2:
        st.metric("Closed WOs Missing Codes", closed_missing, delta="requires action" if closed_missing > 0 else "✅")
    with col3:
        st.metric("Total Work Orders", total_wos)
    
    st.divider()
    st.subheader("Exceptions")
    
    exceptions = wos[(wos["failure_code"].isna()) | (wos["cause_code"].isna())]
    
    if len(exceptions) > 0:
        st.dataframe(exceptions[["wo_id", "status", "vehicle_id", "system", "failure_mode", "failure_code", "cause_code"]], use_container_width=True, height=300)
        
        st.divider()
        st.subheader("Quick Fix: Update Missing Codes")
        
        selected_wo = st.selectbox("Select WO to fix", exceptions["wo_id"].unique())
        if selected_wo:
            wo = get_work_order_by_id(selected_wo)
            
            if wo:
                with st.form("fix_codes_form"):
                    st.write(f"WO: {selected_wo} | {wo.get('system', '')} / {wo.get('component', '')} / {wo.get('failure_mode', '')}")
                    
                    # Get cascade options
                    systems = [""] + list_systems()
                    system = st.selectbox("System", systems, index=systems.index(wo.get("system", "")) if wo.get("system") in systems else 0)
                    
                    subsystems = []
                    if system:
                        subsystems = [""] + list_subsystems(system)
                    subsystem = st.selectbox("Subsystem", subsystems)
                    
                    components = []
                    if system and subsystem:
                        components = [""] + list_components(system, subsystem)
                    component = st.selectbox("Component", components)
                    
                    failure_modes = []
                    if system and subsystem and component:
                        failure_modes = [""] + list_failure_modes(system, subsystem, component)
                    failure_mode = st.selectbox("Failure Mode", failure_modes)
                    
                    if st.form_submit_button("✅ Update Codes"):
                        if failure_mode:
                            cat_row = get_catalogue_row(system, subsystem, component, failure_mode)
                            wo["system"] = system
                            wo["subsystem"] = subsystem
                            wo["component"] = component
                            wo["failure_mode"] = failure_mode
                            wo["failure_code"] = cat_row.get("failure_code")
                            wo["cause_code"] = cat_row.get("cause_code")
                            wo["resolution_code"] = cat_row.get("resolution_code")
                            
                            success, msg = save_work_order(wo)
                            if success:
                                st.success("✅ Codes updated")
                                st.cache_data.clear()
                            else:
                                st.error(f"❌ {msg}")
    else:
        st.success("✅ All work orders have complete codes!")

# ============================================================================
# PAGE: ADMIN
# ============================================================================

def page_admin():
    """Admin page."""
    st.header("⚙️ Administration")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Vehicles", "Users", "Workshops", "Utilities"])
    
    engine = get_engine()
    
    with tab1:
        st.subheader("Vehicles Management")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            vehicles_df = get_vehicles_list()
            st.dataframe(vehicles_df, use_container_width=True, height=400)
        
        with col2:
            with st.form("add_vehicle_form"):
                st.write("**Add Vehicle**")
                vehicle_id = st.text_input("Vehicle ID")
                vin = st.text_input("VIN")
                make = st.text_input("Make")
                model = st.text_input("Model")
                year = st.number_input("Year", min_value=2000, max_value=2030)
                
                if st.form_submit_button("➕ Add Vehicle"):
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO vehicles (vehicle_id, vin, make, model, year, vehicle_type, status)
                                VALUES (:vid, :vin, :make, :model, :year, 'Unknown', 'Active')
                            """), {
                                "vid": vehicle_id,
                                "vin": vin,
                                "make": make,
                                "model": model,
                                "year": year
                            })
                        st.success("✅ Vehicle added")
                        st.cache_data.clear()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    with tab2:
        st.subheader("Users Management")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            users_df = pd.read_sql("SELECT * FROM users ORDER BY username", engine)
            st.dataframe(users_df, use_container_width=True, height=400)
        
        with col2:
            with st.form("add_user_form"):
                st.write("**Add User**")
                username = st.text_input("Username")
                role = st.selectbox("Role", ["Technician", "Supervisor", "Reliability", "Quality", "Admin"])
                workshop = st.selectbox("Workshop", get_workshops_list())
                
                if st.form_submit_button("➕ Add User"):
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT OR REPLACE INTO users (username, role, workshop)
                                VALUES (:u, :r, :w)
                            """), {"u": username, "r": role, "w": workshop})
                        st.success("✅ User added")
                        st.cache_data.clear()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    with tab3:
        st.subheader("Workshops Management")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            workshops_df = pd.read_sql("SELECT * FROM workshops ORDER BY workshop", engine)
            st.dataframe(workshops_df, use_container_width=True, height=300)
        
        with col2:
            with st.form("add_workshop_form"):
                st.write("**Add Workshop**")
                workshop = st.text_input("Workshop Name")
                sector = st.text_input("Sector")
                
                if st.form_submit_button("➕ Add Workshop"):
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT OR REPLACE INTO workshops (workshop, sector)
                                VALUES (:w, :s)
                            """), {"w": workshop, "s": sector})
                        st.success("✅ Workshop added")
                        st.cache_data.clear()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    with tab4:
        st.subheader("Database Utilities")
        
        st.write("**Import Work Orders from Excel**")
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("📤 Upload an Excel file with work order data. Columns can be flexible (System, Component, Failure, Cause, Resolution, Asset Group)")
            uploaded_wo_file = st.file_uploader("Choose Excel file with work orders", type=["xlsx", "xls"], key="wo_import")
            
            if uploaded_wo_file:
                if st.button("📥 Import Work Orders", use_container_width=True):
                    with st.spinner("Importing work orders..."):
                        file_path = f"/tmp/{uploaded_wo_file.name}"
                        with open(file_path, "wb") as f:
                            f.write(uploaded_wo_file.getbuffer())
                        
                        count, warnings = import_work_orders_from_excel(file_path)
                        
                        if count > 0:
                            st.success(f"✅ Imported {count} work orders successfully!")
                            if warnings:
                                with st.expander("⚠️ Import Warnings"):
                                    for warning in warnings[:10]:  # Show first 10
                                        st.write(f"• {warning}")
                        else:
                            st.error(f"❌ No work orders imported")
                            if warnings:
                                st.error(f"Error: {warnings[0]}")
        
        with col2:
            st.write("**Quick Actions**")
            
            if st.button("🆕 Generate 25 Demo Work Orders", use_container_width=True):
                try:
                    engine = get_engine()
                    vehicles_df = get_vehicles_list()
                    users = get_users_list()
                    workshops = get_workshops_list()
                    
                    if len(vehicles_df) == 0:
                        st.error("No vehicles available. Add vehicles first.")
                    else:
                        systems = list_systems()
                        if systems:
                            np.random.seed(datetime.now().microsecond)
                            
                            with engine.begin() as conn:
                                for i in range(25):
                                    vehicle_id = np.random.choice(vehicles_df["vehicle_id"].values)
                                    vin = vehicles_df[vehicles_df["vehicle_id"] == vehicle_id]["vin"].iloc[0]
                                    model = vehicles_df[vehicles_df["vehicle_id"] == vehicle_id]["model"].iloc[0]
                                    vehicle_type = vehicles_df[vehicles_df["vehicle_id"] == vehicle_id]["vehicle_type"].iloc[0]
                                    owning_unit = vehicles_df[vehicles_df["vehicle_id"] == vehicle_id]["owning_unit"].iloc[0]
                                    
                                    system = np.random.choice(systems)
                                    subsystems = list_subsystems(system)
                                    if subsystems:
                                        subsystem = np.random.choice(subsystems)
                                        components = list_components(system, subsystem)
                                        if components:
                                            component = np.random.choice(components)
                                            failure_modes = list_failure_modes(system, subsystem, component)
                                            if failure_modes:
                                                failure_mode = np.random.choice(failure_modes)
                                                cat_row = get_catalogue_row(system, subsystem, component, failure_mode)
                                                
                                                wo_data = {
                                                    "wo_id": next_id("WO", "work_orders", "wo_id"),
                                                    "status": np.random.choice(["Open", "In Progress", "Completed"]),
                                                    "created_dt": datetime.now().date() - timedelta(days=np.random.randint(0, 180)),
                                                    "created_by": np.random.choice(users),
                                                    "workshop": np.random.choice(workshops),
                                                    "vehicle_id": vehicle_id,
                                                    "vin": vin,
                                                    "model": model,
                                                    "vehicle_type": vehicle_type,
                                                    "owning_unit": owning_unit,
                                                    "system": system,
                                                    "component": component,
                                                    "failure_mode": failure_mode,
                                                    "failure_code": cat_row.get("failure_code"),
                                                    "cause_code": cat_row.get("cause_code"),
                                                    "resolution_code": cat_row.get("resolution_code"),
                                                    "labor_hours": np.random.uniform(0, 20),
                                                    "parts_cost": np.random.uniform(0, 500),
                                                    "total_cost": 0,
                                                    "downtime_hours": np.random.uniform(0, 100)
                                                }
                                                
                                                cols = ", ".join(wo_data.keys())
                                                placeholders = ", ".join([f":{k}" for k in wo_data.keys()])
                                                conn.execute(text(f"INSERT INTO work_orders ({cols}) VALUES ({placeholders})"), wo_data)
                            
                            st.success("✅ Generated 25 demo work orders")
                            st.cache_data.clear()
                        else:
                            st.error("No systems in catalogue. Upload catalogue first.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        st.divider()
        col1, col2 = st.columns(2)
        
        with col1:
            pass  # Spacer
        
        with col2:
            if st.button("⚠️ Reset Database (Danger Zone)", type="secondary", use_container_width=True):
                if st.checkbox("I understand this will delete all data"):
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("DELETE FROM work_orders"))
                            conn.execute(text("DELETE FROM fracas_cases"))
                            conn.execute(text("DELETE FROM fracas_actions"))
                            conn.execute(text("DELETE FROM catalogue"))
                        st.success("✅ Database reset. Refresh to re-seed.")
                        st.cache_data.clear()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

# ============================================================================
# PAGE: ABOUT
# ============================================================================

def page_about():
    """About page."""
    st.header("ℹ️ About AMIC FRACAS System")
    
    st.markdown("""
    ### AMIC Work Order Management & FRACAS System
    
    **Prototype Version 1.0**
    
    This application provides comprehensive management of work orders and failure reporting analysis using Corrective and Preventive Actions (FRACAS) methodology.
    
    #### Key Features
    - **Work Order Management**: Create, track, and analyze vehicle maintenance work orders
    - **FRACAS Cases**: Manage failure analysis and corrective actions
    - **Cascading Classification**: System → Subsystem → Component → Failure Mode with auto-populated codes
    - **Rules Engine**: Automated detection of failure patterns, anomalies, and data quality issues
    - **Dashboards**: Real-time KPIs and performance metrics
    - **Data Quality**: Identify and fix incomplete or problematic records
    
    #### Technology Stack
    - **Frontend**: Streamlit
    - **Database**: SQLite with SQLAlchemy ORM
    - **Charts**: Altair
    - **Data Processing**: Pandas, NumPy
    
    #### Rules Engine
    - **R1**: Repeat failure detection (same vehicle + code within timeframe)
    - **R2**: Surge detection (failure code spike vs. baseline)
    - **R3**: High downtime alerts
    - **R4**: Cost spike detection
    - **R5**: Safety-critical systems
    - **R6**: Parts-driven detection
    - **R7**: Data quality checks
    
    #### Database
    - Vehicles master data
    - Work orders with costs and downtime tracking
    - FRACAS catalogue (System/Subsystem/Component/Failure Mode combinations)
    - FRACAS cases with linked work orders
    - Configurable rules and thresholds
    - User and workshop master data
    
    #### Notes
    - This is a **prototype** with demo data
    - All data stored locally in SQLite (`amic_fracas.db`)
    - Designed for team demos and requirements validation
    - Support for bulk import of FRACAS catalogues via Excel
    
    **Version**: 1.0 Prototype  
    **Last Updated**: 2024  
    **Prototype Data Notice**: Not production data
    """)

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Main application entry point."""
    
    # Initialize database
    init_db()
    
    # Header
    st.markdown("""
    <style>
    .header-text {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .footer-text {
        font-size: 0.75rem;
        color: #888;
        text-align: center;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #ddd;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='header-text'>🚗 AMIC Work Order Management & FRACAS System</div>", unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select Page", [
        "Work Orders",
        "Catalogue (FRACAS Codes)",
        "FRACAS Cases",
        "Rules & Detection",
        "Dashboards",
        "Admin (Master Data)",
        "Data Quality",
        "About"
    ])
    
    # Dispatch pages
    if page == "Work Orders":
        page_work_orders()
    elif page == "Catalogue (FRACAS Codes)":
        page_catalogue()
    elif page == "FRACAS Cases":
        page_fracas_cases()
    elif page == "Rules & Detection":
        page_rules_detection()
    elif page == "Dashboards":
        page_dashboards()
    elif page == "Admin (Master Data)":
        page_admin()
    elif page == "Data Quality":
        page_data_quality()
    elif page == "About":
        page_about()
    
    # Footer
    st.markdown("""
    <div class='footer-text'>
    AMIC Work Order Management & FRACAS System - Prototype v1.0 | Not production data
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
