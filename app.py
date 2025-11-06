"""
AMIC Work Order Management & FRACAS System - ENHANCED VERSION (WHITE THEME)
Advanced dashboards, analytics, KPIs, and insights
Hard-coded catalogue + pre-loaded demo data
Light/White background theme
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
import altair as alt
import json

# ============================================================================
# CONFIG & SESSION STATE & THEMING
# ============================================================================
st.set_page_config(
    page_title="AMIC FRACAS System Enhanced",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# WHITE THEME STYLING
# ============================================================================
st.markdown("""
<style>
/* Main app background - White */
[data-testid="stAppViewContainer"] {
    background-color: #FFFFFF;
    color: #111827;
}

/* Sidebar background - Light Gray */
[data-testid="stSidebar"] {
    background-color: #F9FAFB;
}

/* Main content area */
[data-testid="stMain"] {
    background-color: #FFFFFF;
}

/* Block containers - White background */
.block-container {
    background-color: #FFFFFF;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Text inputs - White with dark border */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stNumberInput > div > div > input,
.stDateInput > div > div > input {
    background-color: #FFFFFF !important;
    color: #111827 !important;
    border: 1px solid #D1D5DB !important;
}

/* Text areas */
.stTextArea > div > div > textarea {
    background-color: #FFFFFF !important;
    color: #111827 !important;
    border: 1px solid #D1D5DB !important;
}

/* Dataframes and tables */
[data-testid="stDataFrame"] {
    background-color: #FFFFFF;
}

/* Buttons */
.stButton > button {
    background-color: #3B82F6;
    color: white;
    border: none;
    border-radius: 6px;
    font-weight: 500;
}

.stButton > button:hover {
    background-color: #2563EB;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background-color: #F3F4F6;
    border-bottom: 2px solid #E5E7EB;
}

.stTabs [data-baseweb="tab"] {
    color: #4B5563;
    background-color: transparent;
}

.stTabs [aria-selected="true"] {
    color: #3B82F6;
    border-bottom: 3px solid #3B82F6;
}

/* Metric cards */
.stMetric {
    background-color: #F9FAFB;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 1.5rem;
}

/* Divider */
hr {
    background-color: #E5E7EB;
    border: none;
    height: 1px;
}

/* Headers and text */
h1, h2, h3, h4, h5, h6 {
    color: #111827;
}

/* Info/Success/Error messages */
.stSuccess {
    background-color: #D1FAE5 !important;
    color: #065F46 !important;
    border: 1px solid #A7F3D0 !important;
}

.stError {
    background-color: #FEE2E2 !important;
    color: #7F1D1D !important;
    border: 1px solid #FECACA !important;
}

.stInfo {
    background-color: #DBEAFE !important;
    color: #1E40AF !important;
    border: 1px solid #BFDBFE !important;
}

.stWarning {
    background-color: #FEF3C7 !important;
    color: #78350F !important;
    border: 1px solid #FDE68A !important;
}

/* Charts container */
.altair-container {
    background-color: #FFFFFF;
}

/* Sidebar text */
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
    color: #111827;
}

/* Success badge in sidebar */
.stSidebarContent {
    color: #111827;
}

/* Markdown text */
[data-testid="stMarkdownContainer"] {
    color: #111827;
}

/* Links */
a {
    color: #3B82F6;
    text-decoration: none;
}

a:hover {
    color: #2563EB;
    text-decoration: underline;
}

/* Export button */
[data-testid="stDownloadButton"] > button {
    background-color: #10B981;
    color: white;
}

[data-testid="stDownloadButton"] > button:hover {
    background-color: #059669;
}
</style>
""", unsafe_allow_html=True)

if "app_initialized" not in st.session_state:
    st.session_state.app_initialized = False
if "current_user" not in st.session_state:
    st.session_state.current_user = "tech_001"

# ============================================================================
# HARD-CODED CATALOGUE HIERARCHY
# ============================================================================
CATALOGUE_HIERARCHY = {
    "HVAC": {
        "Air Conditioning": {
            "Compressor": {
                "Mechanical seizure": {"failure_code": "HVAC-AC-001", "cause_code": "HVAC-AC-C001", "resolution_code": "HVAC-AC-R001", "recommended_action": "Replace compressor; Replace clutch; Flush circuit; Replace filter/drier; Vacuum & recharge to spec"},
                "Insufficient displacement": {"failure_code": "NAN-NAN-001", "cause_code": "NAN-NAN-C001", "resolution_code": "NAN-NAN-R001", "recommended_action": "Replace compressor; Check displacement; Recharge system"},
                "Internal wear/contamination": {"failure_code": "NAN-NAN-002", "cause_code": "NAN-NAN-C002", "resolution_code": "NAN-NAN-R002", "recommended_action": "Replace compressor; Flush circuit; Replace drier"}
            },
            "Condenser": {
                "Leak at tubes": {"failure_code": "NAN-NAN-009", "cause_code": "NAN-NAN-C009", "resolution_code": "NAN-NAN-R009", "recommended_action": "Replace condenser; Clean fins; Leak test"},
                "Fin blockage": {"failure_code": "NAN-NAN-011", "cause_code": "NAN-NAN-C011", "resolution_code": "NAN-NAN-R011", "recommended_action": "Clean fins; Replace if damaged"}
            }
        },
        "Heating": {
            "Heater Core": {
                "Leak": {"failure_code": "NAN-HEAT-001", "cause_code": "NAN-HEAT-C001", "resolution_code": "NAN-HEAT-R001", "recommended_action": "Replace heater core; Flush circuit"},
                "Blockage": {"failure_code": "NAN-NAN-040", "cause_code": "NAN-NAN-C040", "resolution_code": "NAN-NAN-R040", "recommended_action": "Flush heater core; Replace if necessary"}
            }
        }
    },
    "Engine": {
        "Fuel System": {
            "Fuel Pump": {
                "Loss of Pressure": {"failure_code": "ENG-FUE-001", "cause_code": "ENG-FUE-C001", "resolution_code": "ENG-FUE-R001", "recommended_action": "Replace fuel pump; Test pressure; Check filter"},
                "Low Flow": {"failure_code": "ENG-FUE-002", "cause_code": "ENG-FUE-C002", "resolution_code": "ENG-FUE-R002", "recommended_action": "Replace pump; Check fuel supply"}
            },
            "Fuel Filter": {
                "Clogging": {"failure_code": "ENG-FUE-003", "cause_code": "ENG-FUE-C003", "resolution_code": "ENG-FUE-R003", "recommended_action": "Replace fuel filter"},
                "Bypass open": {"failure_code": "ENG-FUE-004", "cause_code": "ENG-FUE-C004", "resolution_code": "ENG-FUE-R004", "recommended_action": "Replace fuel filter assembly"}
            }
        },
        "Ignition System": {
            "Spark Plugs": {
                "Fouled": {"failure_code": "ENG-IGN-001", "cause_code": "ENG-IGN-C001", "resolution_code": "ENG-IGN-R001", "recommended_action": "Replace spark plugs; Check gap"},
                "Worn": {"failure_code": "ENG-IGN-002", "cause_code": "ENG-IGN-C002", "resolution_code": "ENG-IGN-R002", "recommended_action": "Replace spark plugs"}
            }
        },
        "Cooling System": {
            "Radiator": {
                "Leak": {"failure_code": "ENG-COL-001", "cause_code": "ENG-COL-C001", "resolution_code": "ENG-COL-R001", "recommended_action": "Replace radiator; Check hoses"},
                "Blocked": {"failure_code": "ENG-COL-002", "cause_code": "ENG-COL-C002", "resolution_code": "ENG-COL-R002", "recommended_action": "Flush radiator; Clean fins"}
            },
            "Water Pump": {
                "Seal leak": {"failure_code": "ENG-COL-003", "cause_code": "ENG-COL-C003", "resolution_code": "ENG-COL-R003", "recommended_action": "Replace water pump"},
                "Bearing failure": {"failure_code": "ENG-COL-004", "cause_code": "ENG-COL-C004", "resolution_code": "ENG-COL-R004", "recommended_action": "Replace pump bearing"}
            }
        }
    },
    "Brakes": {
        "Hydraulic": {
            "Master Cylinder": {
                "Seal bypass": {"failure_code": "BRK-HYD-001", "cause_code": "BRK-HYD-C001", "resolution_code": "BRK-HYD-R001", "recommended_action": "Replace master cylinder; Bleed system"},
                "External leak": {"failure_code": "BRK-HYD-002", "cause_code": "BRK-HYD-C002", "resolution_code": "BRK-HYD-R002", "recommended_action": "Replace master cylinder"}
            }
        },
        "Friction": {
            "Pads/Shoes": {
                "Worn to backing": {"failure_code": "BRK-FRI-001", "cause_code": "BRK-FRI-C001", "resolution_code": "BRK-FRI-R001", "recommended_action": "Replace brake pads; Service hardware"},
                "Glazed": {"failure_code": "BRK-FRI-002", "cause_code": "BRK-FRI-C002", "resolution_code": "BRK-FRI-R002", "recommended_action": "Replace pads; Clean rotors"}
            },
            "Rotors": {
                "Warped": {"failure_code": "BRK-FRI-003", "cause_code": "BRK-FRI-C003", "resolution_code": "BRK-FRI-R003", "recommended_action": "Replace rotor; Check calipers"},
                "Scored": {"failure_code": "BRK-FRI-004", "cause_code": "BRK-FRI-C004", "resolution_code": "BRK-FRI-R004", "recommended_action": "Resurface or replace rotor"}
            }
        }
    },
    "Transmission/Drivetrain": {
        "Manual": {
            "Clutch": {
                "Disc wear": {"failure_code": "TRN-MAN-001", "cause_code": "TRN-MAN-C001", "resolution_code": "TRN-MAN-R001", "recommended_action": "Replace clutch kit; Bleed hydraulics"},
                "Pressure plate crack": {"failure_code": "TRN-MAN-002", "cause_code": "TRN-MAN-C002", "resolution_code": "TRN-MAN-R002", "recommended_action": "Replace clutch assembly"}
            }
        },
        "Automatic": {
            "Fluid": {
                "Overheat": {"failure_code": "TRN-AT-001", "cause_code": "TRN-AT-C001", "resolution_code": "TRN-AT-R001", "recommended_action": "Service fluid/filter; Replace solenoid pack"}
            }
        }
    },
    "Suspension": {
        "Front": {
            "Control Arms": {
                "Bushing wear": {"failure_code": "SUS-FRO-001", "cause_code": "SUS-FRO-C001", "resolution_code": "SUS-FRO-R001", "recommended_action": "Replace bushings; Replace ball joint; Align"},
                "Bent arm": {"failure_code": "SUS-FRO-003", "cause_code": "SUS-FRO-C003", "resolution_code": "SUS-FRO-R003", "recommended_action": "Replace control arm"}
            },
            "Shocks": {
                "Seal leak": {"failure_code": "SUS-FRO-004", "cause_code": "SUS-FRO-C004", "resolution_code": "SUS-FRO-R004", "recommended_action": "Replace shock absorber"},
                "Gas loss": {"failure_code": "SUS-FRO-005", "cause_code": "SUS-FRO-C005", "resolution_code": "SUS-FRO-R005", "recommended_action": "Replace shock"}
            }
        }
    },
    "Steering": {
        "Steering Gear": {
            "Rack and Pinion": {
                "Seal leak": {"failure_code": "STE-GEAR-001", "cause_code": "STE-GEAR-C001", "resolution_code": "STE-GEAR-R001", "recommended_action": "Replace rack; Replace seals"},
                "Play": {"failure_code": "STE-GEAR-002", "cause_code": "STE-GEAR-C002", "resolution_code": "STE-GEAR-R002", "recommended_action": "Replace rack"}
            }
        }
    },
    "Electrical/Power": {
        "Battery System": {
            "12V Battery": {
                "Low capacity": {"failure_code": "ELE-BAT-001", "cause_code": "ELE-BAT-C001", "resolution_code": "ELE-BAT-R001", "recommended_action": "Replace battery; Clean terminals"},
                "Terminal corrosion": {"failure_code": "ELE-BAT-002", "cause_code": "ELE-BAT-C002", "resolution_code": "ELE-BAT-R002", "recommended_action": "Clean terminals; Replace if damaged"}
            }
        },
        "Starting": {
            "Starter Motor": {
                "No crank": {"failure_code": "ELE-STR-001", "cause_code": "ELE-STR-C001", "resolution_code": "ELE-STR-R001", "recommended_action": "Replace starter; Repair wiring"},
                "Solenoid fault": {"failure_code": "ELE-STR-002", "cause_code": "ELE-STR-C002", "resolution_code": "ELE-STR-R002", "recommended_action": "Replace starter"}
            }
        }
    },
    "Tires/Wheels": {
        "Rolling Assembly": {
            "Tires": {
                "Puncture": {"failure_code": "TIR-RLL-001", "cause_code": "TIR-RLL-C001", "resolution_code": "TIR-RLL-R001", "recommended_action": "Repair/replace tire; Balance; Align"},
                "Uneven wear": {"failure_code": "TIR-RLL-004", "cause_code": "TIR-RLL-C004", "resolution_code": "TIR-RLL-R004", "recommended_action": "Replace tire; Align vehicle"}
            },
            "Rims": {
                "Bent": {"failure_code": "TIR-RLL-005", "cause_code": "TIR-RLL-C005", "resolution_code": "TIR-RLL-R005", "recommended_action": "Repair/replace rim"},
                "Cracked": {"failure_code": "TIR-RLL-006", "cause_code": "TIR-RLL-C006", "resolution_code": "TIR-RLL-R006", "recommended_action": "Replace rim"}
            }
        }
    }
}

# ============================================================================
# DATABASE SETUP
# ============================================================================
DB_FILE = "/tmp/amic_fracas_enhanced_white.db"

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
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id)
            )
        """))
    
    with engine.begin() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM vehicles"))
        vehicles_count = result.scalar()
        result = conn.execute(text("SELECT COUNT(*) FROM work_orders"))
        wo_count = result.scalar()
    
    if vehicles_count == 0:
        seed_data(engine)
    if wo_count == 0:
        seed_work_orders(engine)

def seed_data(engine):
    """Seed database with demo vehicles."""
    vehicles_data = [
        ("VEH-0001", "JN15679D00000001", "Nissan", "Patrol", 2022, "SUV", "Unit A", "2022-05-15"),
        ("VEH-0002", "JTE45678B00000002", "Toyota", "Hilux", 2021, "Pickup", "Unit B", "2021-08-20"),
        ("VEH-0003", "HU23456789000003", "Hyundai", "HD65", 2020, "Truck", "Unit C", "2020-12-01"),
        ("VEH-0004", "JN15679D00000004", "Nissan", "Urvan", 2023, "Van", "Unit A", "2023-02-10"),
        ("VEH-0005", "JTE45678B00000005", "Toyota", "Land Cruiser", 2019, "SUV", "Unit D", "2019-11-30"),
    ]
    
    with engine.begin() as conn:
        for vehicle in vehicles_data:
            try:
                conn.execute(text(
                    """INSERT INTO vehicles 
                       (vehicle_id, vin, make, model, year, vehicle_type, owning_unit, in_service_dt, status)
                       VALUES (:vid, :vin, :make, :model, :year, :vtype, :unit, :dt, :status)"""
                ), {
                    "vid": vehicle[0],
                    "vin": vehicle[1],
                    "make": vehicle[2],
                    "model": vehicle[3],
                    "year": vehicle[4],
                    "vtype": vehicle[5],
                    "unit": vehicle[6],
                    "dt": vehicle[7],
                    "status": "Active"
                })
            except:
                pass

def seed_work_orders(engine):
    """Seed database with 300 demo work orders."""
    np.random.seed(42)
    
    vehicles = ["VEH-0001", "VEH-0002", "VEH-0003", "VEH-0004", "VEH-0005"]
    vehicle_info = {
        "VEH-0001": ("JN15679D00000001", "Patrol", "SUV"),
        "VEH-0002": ("JTE45678B00000002", "Hilux", "Pickup"),
        "VEH-0003": ("HU23456789000003", "HD65", "Truck"),
        "VEH-0004": ("JN15679D00000004", "Urvan", "Van"),
        "VEH-0005": ("JTE45678B00000005", "Land Cruiser", "SUV"),
    }
    
    workshops = ["Riyadh_Main", "Jeddah_South", "Central"]
    statuses = ["Completed", "Open", "In Progress", "Closed"]
    users = ["tech_001", "tech_002", "tech_003", "supervisor_001"]
    
    sample_failures = [
        ("HVAC", "Air Conditioning", "Compressor", "Mechanical seizure", "HVAC-AC-001", "HVAC-AC-C001", "HVAC-AC-R001"),
        ("Engine", "Fuel System", "Fuel Pump", "Loss of Pressure", "ENG-FUE-001", "ENG-FUE-C001", "ENG-FUE-R001"),
        ("Brakes", "Friction", "Pads/Shoes", "Worn to backing", "BRK-FRI-001", "BRK-FRI-C001", "BRK-FRI-R001"),
        ("Suspension", "Front", "Shocks", "Seal leak", "SUS-FRO-004", "SUS-FRO-C004", "SUS-FRO-R004"),
        ("Steering", "Steering Gear", "Rack and Pinion", "Seal leak", "STE-GEAR-001", "STE-GEAR-C001", "STE-GEAR-R001"),
        ("Electrical/Power", "Battery System", "12V Battery", "Low capacity", "ELE-BAT-001", "ELE-BAT-C001", "ELE-BAT-R001"),
        ("Tires/Wheels", "Rolling Assembly", "Tires", "Puncture", "TIR-RLL-001", "TIR-RLL-C001", "TIR-RLL-R001"),
    ]
    
    with engine.begin() as conn:
        for i in range(300):
            vehicle_id = np.random.choice(vehicles)
            vin, model, vtype = vehicle_info[vehicle_id]
            created_dt = datetime.now() - timedelta(days=np.random.randint(0, 120))
            status = np.random.choice(statuses, p=[0.6, 0.15, 0.2, 0.05])
            
            completed_dt = None
            if status in ["Completed", "Closed"]:
                completed_dt = created_dt + timedelta(days=np.random.randint(1, 20))
            
            system, subsystem, component, failure_mode, fc, cc, rc = sample_failures[np.random.randint(0, len(sample_failures))]
            
            try:
                conn.execute(text("""
                    INSERT INTO work_orders (
                        wo_id, status, created_dt, completed_dt, created_by, assigned_to,
                        workshop, sector, vehicle_id, vin, model, vehicle_type, owning_unit,
                        system, subsystem, component, failure_mode, failure_code, cause_code,
                        resolution_code, labor_hours, parts_cost, total_cost, downtime_hours
                    ) VALUES (
                        :woid, :status, :created, :completed, :cby, :ato, :workshop, :sector,
                        :vid, :vin, :model, :vtype, :unit, :sys, :sub, :comp, :fm, :fc, :cc,
                        :rc, :labor, :cost, :total, :downtime
                    )
                """), {
                    "woid": f"WO-{i+1:06d}",
                    "status": status,
                    "created": created_dt.strftime('%Y-%m-%d'),
                    "completed": completed_dt.strftime('%Y-%m-%d') if completed_dt else None,
                    "cby": np.random.choice(users),
                    "ato": np.random.choice(users),
                    "workshop": np.random.choice(workshops),
                    "sector": "Central",
                    "vid": vehicle_id,
                    "vin": vin,
                    "model": model,
                    "vtype": vtype,
                    "unit": f"Unit {chr(65 + np.random.randint(0, 4))}",
                    "sys": system,
                    "sub": subsystem,
                    "comp": component,
                    "fm": failure_mode,
                    "fc": fc,
                    "cc": cc,
                    "rc": rc,
                    "labor": round(np.random.uniform(1, 20), 1),
                    "cost": round(np.random.uniform(100, 2000), 2),
                    "total": round(np.random.uniform(100, 2000), 2),
                    "downtime": round(np.random.uniform(2, 72), 1)
                })
            except:
                continue

# ============================================================================
# DROPDOWN FUNCTIONS
# ============================================================================
def list_systems():
    return sorted(list(CATALOGUE_HIERARCHY.keys()))

def list_subsystems(system):
    if not system or system not in CATALOGUE_HIERARCHY:
        return []
    return sorted(list(CATALOGUE_HIERARCHY[system].keys()))

def list_components(system, subsystem):
    if not system or not subsystem:
        return []
    if system not in CATALOGUE_HIERARCHY or subsystem not in CATALOGUE_HIERARCHY[system]:
        return []
    return sorted(list(CATALOGUE_HIERARCHY[system][subsystem].keys()))

def list_failure_modes(system, subsystem, component):
    if not system or not subsystem or not component:
        return []
    if system not in CATALOGUE_HIERARCHY:
        return []
    if subsystem not in CATALOGUE_HIERARCHY[system]:
        return []
    if component not in CATALOGUE_HIERARCHY[system][subsystem]:
        return []
    return sorted(list(CATALOGUE_HIERARCHY[system][subsystem][component].keys()))

def get_codes(system, subsystem, component, failure_mode):
    try:
        data = CATALOGUE_HIERARCHY[system][subsystem][component][failure_mode]
        return data
    except:
        return {"failure_code": "", "cause_code": "", "resolution_code": "", "recommended_action": ""}

# ============================================================================
# DATABASE HELPER FUNCTIONS
# ============================================================================
def next_id(prefix, table, col="wo_id"):
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT MAX({col}) FROM {table}"))
        max_id = result.scalar()
        if max_id is None:
            num = 1
        else:
            try:
                num = int(max_id.split("-")[-1]) + 1
            except:
                num = 1
        return f"{prefix}-{num:06d}"

def save_work_order(wo_data):
    engine = get_engine()
    
    errors = []
    if not wo_data.get("vehicle_id"):
        errors.append("Vehicle ID required")
    if not wo_data.get("system"):
        errors.append("System required")
    
    if errors:
        return False, " | ".join(errors)
    
    if isinstance(wo_data.get("created_dt"), object) and hasattr(wo_data["created_dt"], 'strftime'):
        wo_data["created_dt"] = wo_data["created_dt"].strftime('%Y-%m-%d')
    if isinstance(wo_data.get("completed_dt"), object) and hasattr(wo_data["completed_dt"], 'strftime'):
        wo_data["completed_dt"] = wo_data["completed_dt"].strftime('%Y-%m-%d')
    
    try:
        with engine.begin() as conn:
            wo_id = next_id("WO", "work_orders", "wo_id")
            wo_data["wo_id"] = wo_id
            cols = ", ".join(wo_data.keys())
            placeholders = ", ".join([f":{k}" for k in wo_data.keys()])
            conn.execute(text(f"INSERT INTO work_orders ({cols}) VALUES ({placeholders})"), wo_data)
        return True, f"✅ Work Order saved: {wo_id}"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

def get_work_orders(filters=None):
    engine = get_engine()
    query = "SELECT * FROM work_orders WHERE 1=1"
    params = {}
    
    if filters:
        if filters.get("status"):
            query += " AND status = :status"
            params["status"] = filters["status"]
        if filters.get("vehicle_id"):
            query += " AND vehicle_id = :vehicle_id"
            params["vehicle_id"] = filters["vehicle_id"]
    
    query += " ORDER BY created_dt DESC"
    with engine.connect() as conn:
        return pd.read_sql(query, conn, params=params)

def get_vehicles_list():
    engine = get_engine()
    query = "SELECT vehicle_id, vin, make, model, year, vehicle_type FROM vehicles ORDER BY vehicle_id"
    return pd.read_sql(query, engine)

# ============================================================================
# ANALYTICS FUNCTIONS
# ============================================================================
def calculate_mttr(wos):
    """Calculate Mean Time To Repair in hours"""
    completed = wos[(wos['status'].isin(['Completed', 'Closed'])) & (wos['labor_hours'] > 0)]
    if len(completed) > 0:
        return completed['labor_hours'].mean()
    return 0

def calculate_failure_rate(wos):
    """Calculate failure rate per vehicle"""
    if len(wos) == 0:
        return 0
    vehicles_count = wos['vehicle_id'].nunique()
    return len(wos) / vehicles_count if vehicles_count > 0 else 0

def get_system_reliability(wos):
    """Get reliability score for each system"""
    if len(wos) == 0:
        return {}
    system_failures = wos.groupby('system').size()
    total = len(wos)
    reliability = {}
    for system, count in system_failures.items():
        reliability[system] = round((1 - (count / total)) * 100, 1) if total > 0 else 0
    return reliability

def get_vehicle_health(wos):
    """Get health score for each vehicle"""
    vehicles = wos['vehicle_id'].unique()
    health_scores = {}
    for vehicle in vehicles:
        vehicle_wos = wos[wos['vehicle_id'] == vehicle]
        open_count = len(vehicle_wos[vehicle_wos['status'] == 'Open'])
        in_prog_count = len(vehicle_wos[vehicle_wos['status'] == 'In Progress'])
        total_issues = len(vehicle_wos)
        
        active_issues = open_count + in_prog_count
        health_scores[vehicle] = max(0, 100 - (active_issues * 20) - (total_issues * 2))
    return health_scores

def get_technician_stats(wos):
    """Get performance stats for each technician"""
    if len(wos) == 0:
        return {}
    tech_stats = {}
    for tech in wos['assigned_to'].unique():
        tech_wos = wos[wos['assigned_to'] == tech]
        completed = len(tech_wos[tech_wos['status'].isin(['Completed', 'Closed'])])
        total = len(tech_wos)
        avg_labor = tech_wos['labor_hours'].mean() if len(tech_wos) > 0 else 0
        
        tech_stats[tech] = {
            'total': total,
            'completed': completed,
            'completion_rate': (completed / total * 100) if total > 0 else 0,
            'avg_labor': round(avg_labor, 1)
        }
    return tech_stats

# ============================================================================
# PAGE: ENHANCED DASHBOARDS
# ============================================================================
def page_enhanced_dashboards():
    """Enhanced dashboards with advanced analytics"""
    st.header("📊 Advanced Analytics Dashboard")
    
    wos = get_work_orders()
    
    if len(wos) == 0:
        st.info("No work order data available.")
        return
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Executive Summary",
        "🔧 System Health",
        "🚗 Vehicle Analysis",
        "👥 Technician Performance",
        "💰 Cost Analysis"
    ])
    
    with tab1:
        st.subheader("Executive Summary")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        total_wos = len(wos)
        completed = len(wos[wos['status'] == 'Completed'])
        open_wos = len(wos[wos['status'] == 'Open'])
        in_progress = len(wos[wos['status'] == 'In Progress'])
        completion_rate = (completed / total_wos * 100) if total_wos > 0 else 0
        
        with col1:
            st.metric("Total WOs", total_wos, "All time")
        with col2:
            st.metric("Completion Rate", f"{completion_rate:.1f}%", f"{completed} completed")
        with col3:
            st.metric("MTTR (hours)", f"{calculate_mttr(wos):.1f}", "Mean Time To Repair")
        with col4:
            st.metric("Avg Downtime", f"{wos['downtime_hours'].mean():.1f}h", "Per incident")
        with col5:
            st.metric("Failure Rate", f"{calculate_failure_rate(wos):.1f}", "Per vehicle")
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Work Order Trends (Last 30 Days)")
            
            today = datetime.now().date()
            last_30_days = wos[pd.to_datetime(wos['created_dt']).dt.date >= (today - timedelta(days=30))]
            
            daily_data = []
            for i in range(30):
                date = today - timedelta(days=29-i)
                count = len(last_30_days[pd.to_datetime(last_30_days['created_dt']).dt.date == date])
                daily_data.append({"Date": date, "WOs Created": count})
            
            trend_df = pd.DataFrame(daily_data)
            
            if len(trend_df) > 0:
                trend_chart = alt.Chart(trend_df).mark_line(point=True, color='#3B82F6').encode(
                    x=alt.X("Date:T", title="Date"),
                    y=alt.Y("WOs Created:Q", title="Work Orders"),
                    tooltip=["Date", "WOs Created"]
                ).properties(height=300).interactive()
                
                st.altair_chart(trend_chart, use_container_width=True)
            else:
                st.info("No data available for trend")
        
        with col2:
            st.subheader("Status Distribution")
            
            status_data = wos['status'].value_counts()
            status_df = pd.DataFrame({
                'Status': status_data.index,
                'Count': status_data.values
            })
            
            if len(status_df) > 0:
                status_chart = alt.Chart(status_df).mark_bar().encode(
                    x=alt.X("Status:N", title="Status"),
                    y=alt.Y("Count:Q", title="Count"),
                    color=alt.Color("Status:N", scale=alt.Scale(
                        domain=['Completed', 'Closed', 'In Progress', 'Open'], 
                        range=['#10B981', '#059669', '#F59E0B', '#EF4444']
                    ))
                ).properties(height=300)
                
                st.altair_chart(status_chart, use_container_width=True)
    
    with tab2:
        st.subheader("System Health & Reliability")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Top Failing Systems")
            
            system_failures = wos['system'].value_counts().head(10)
            if len(system_failures) > 0:
                system_df = pd.DataFrame({
                    'System': system_failures.index,
                    'Failures': system_failures.values
                })
                
                system_chart = alt.Chart(system_df).mark_barh().encode(
                    y=alt.Y("System:N", sort="-x", title="System"),
                    x=alt.X("Failures:Q", title="Number of Failures"),
                    color=alt.Color("Failures:Q", scale=alt.Scale(scheme='reds'))
                ).properties(height=300)
                
                st.altair_chart(system_chart, use_container_width=True)
            else:
                st.info("No system data available")
        
        with col2:
            st.subheader("System Reliability Score")
            
            reliability = get_system_reliability(wos)
            if len(reliability) > 0:
                reliability_df = pd.DataFrame({
                    'System': list(reliability.keys()),
                    'Reliability %': list(reliability.values())
                }).sort_values('Reliability %', ascending=False).head(10)
                
                reliability_chart = alt.Chart(reliability_df).mark_bar().encode(
                    y=alt.Y("System:N", sort="-x", title="System"),
                    x=alt.X("Reliability %:Q", scale=alt.Scale(domain=[0, 100]), title="Reliability %"),
                    color=alt.Color("Reliability %:Q", scale=alt.Scale(scheme='greens'))
                ).properties(height=300)
                
                st.altair_chart(reliability_chart, use_container_width=True)
            else:
                st.info("No reliability data available")
        
        st.divider()
        
        st.subheader("Top Failure Modes")
        top_failures = wos['failure_mode'].value_counts().head(15)
        if len(top_failures) > 0:
            failure_df = pd.DataFrame({
                'Failure Mode': top_failures.index,
                'Count': top_failures.values
            })
            
            failure_chart = alt.Chart(failure_df).mark_bar(color='#F97316').encode(
                y=alt.Y("Failure Mode:N", sort="-x", title="Failure Mode"),
                x=alt.X("Count:Q", title="Count"),
                color=alt.Color("Count:Q", scale=alt.Scale(scheme='oranges'))
            ).properties(height=400)
            
            st.altair_chart(failure_chart, use_container_width=True)
        else:
            st.info("No failure mode data available")
    
    with tab3:
        st.subheader("Vehicle Health Analysis")
        
        health_scores = get_vehicle_health(wos)
        if len(health_scores) > 0:
            health_df = pd.DataFrame({
                'Vehicle': list(health_scores.keys()),
                'Health Score': list(health_scores.values())
            }).sort_values('Health Score', ascending=False)
            
            health_chart = alt.Chart(health_df).mark_bar().encode(
                y=alt.Y("Vehicle:N", sort="-x", title="Vehicle"),
                x=alt.X("Health Score:Q", scale=alt.Scale(domain=[0, 100]), title="Health Score"),
                color=alt.condition(
                    alt.datum['Health Score'] >= 70,
                    alt.value('#10B981'),
                    alt.condition(
                        alt.datum['Health Score'] >= 40,
                        alt.value('#F59E0B'),
                        alt.value('#EF4444')
                    )
                )
            ).properties(height=300)
            
            st.altair_chart(health_chart, use_container_width=True)
            
            st.divider()
            
            st.subheader("Active Issues by Vehicle")
            vehicle_issues = []
            for vehicle in wos['vehicle_id'].unique():
                vehicle_wos = wos[wos['vehicle_id'] == vehicle]
                vehicle_issues.append({
                    'Vehicle': vehicle,
                    'Open': len(vehicle_wos[vehicle_wos['status'] == 'Open']),
                    'In Progress': len(vehicle_wos[vehicle_wos['status'] == 'In Progress']),
                    'Total Issues': len(vehicle_wos)
                })
            
            issues_df = pd.DataFrame(vehicle_issues)
            st.dataframe(issues_df, use_container_width=True)
        else:
            st.info("No vehicle data available")
    
    with tab4:
        st.subheader("Technician Performance Metrics")
        
        tech_stats = get_technician_stats(wos)
        
        if len(tech_stats) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Completion Rate by Technician")
                
                tech_comp_df = pd.DataFrame({
                    'Technician': list(tech_stats.keys()),
                    'Completion Rate %': [tech_stats[t]['completion_rate'] for t in tech_stats.keys()]
                }).sort_values('Completion Rate %', ascending=False)
                
                if len(tech_comp_df) > 0:
                    comp_chart = alt.Chart(tech_comp_df).mark_bar(color='#3B82F6').encode(
                        y=alt.Y("Technician:N", sort="-x", title="Technician"),
                        x=alt.X("Completion Rate %:Q", scale=alt.Scale(domain=[0, 100]), title="Completion %"),
                        color=alt.Color("Completion Rate %:Q", scale=alt.Scale(scheme='blues'))
                    ).properties(height=300)
                    
                    st.altair_chart(comp_chart, use_container_width=True)
            
            with col2:
                st.subheader("Average Labor Hours")
                
                tech_labor_df = pd.DataFrame({
                    'Technician': list(tech_stats.keys()),
                    'Avg Labor Hours': [tech_stats[t]['avg_labor'] for t in tech_stats.keys()]
                }).sort_values('Avg Labor Hours', ascending=False)
                
                if len(tech_labor_df) > 0:
                    labor_chart = alt.Chart(tech_labor_df).mark_bar(color='#8B5CF6').encode(
                        y=alt.Y("Technician:N", sort="-x", title="Technician"),
                        x=alt.X("Avg Labor Hours:Q", title="Hours"),
                        color=alt.Color("Avg Labor Hours:Q", scale=alt.Scale(scheme='purples'))
                    ).properties(height=300)
                    
                    st.altair_chart(labor_chart, use_container_width=True)
            
            st.divider()
            
            st.subheader("Detailed Technician Statistics")
            
            tech_detail_df = pd.DataFrame({
                'Technician': list(tech_stats.keys()),
                'Total WOs': [tech_stats[t]['total'] for t in tech_stats.keys()],
                'Completed': [tech_stats[t]['completed'] for t in tech_stats.keys()],
                'Completion Rate %': [f"{tech_stats[t]['completion_rate']:.1f}%" for t in tech_stats.keys()],
                'Avg Labor Hours': [f"{tech_stats[t]['avg_labor']:.1f}" for t in tech_stats.keys()]
            }).sort_values('Total WOs', ascending=False)
            
            st.dataframe(tech_detail_df, use_container_width=True)
        else:
            st.info("No technician data available")
    
    with tab5:
        st.subheader("Cost Analysis & Trends")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Cost by System")
            
            cost_by_system = wos.groupby('system')[['parts_cost', 'labor_hours']].agg({
                'parts_cost': 'sum',
                'labor_hours': 'sum'
            }).reset_index()
            cost_by_system['Labor Cost'] = cost_by_system['labor_hours'] * 50
            cost_by_system['Total Cost'] = cost_by_system['parts_cost'] + cost_by_system['Labor Cost']
            cost_by_system = cost_by_system.sort_values('Total Cost', ascending=False).head(10)
            
            if len(cost_by_system) > 0:
                cost_chart = alt.Chart(cost_by_system).mark_bar(color='#DC2626').encode(
                    y=alt.Y("system:N", sort="-x", title="System"),
                    x=alt.X("Total Cost:Q", title="Total Cost ($)"),
                    color=alt.Color("Total Cost:Q", scale=alt.Scale(scheme='reds'))
                ).properties(height=300)
                
                st.altair_chart(cost_chart, use_container_width=True)
        
        with col2:
            st.subheader("Parts vs Labor Cost Breakdown")
            
            total_parts = wos['parts_cost'].sum()
            avg_labor_cost = (wos['labor_hours'].sum() * 50)
            
            breakdown_df = pd.DataFrame({
                'Category': ['Parts Cost', 'Labor Cost'],
                'Amount': [total_parts, avg_labor_cost]
            })
            
            if len(breakdown_df) > 0:
                breakdown_chart = alt.Chart(breakdown_df).mark_pie().encode(
                    theta=alt.Theta("Amount:Q"),
                    color=alt.Color("Category:N", scale=alt.Scale(domain=['Parts Cost', 'Labor Cost'], range=['#3B82F6', '#10B981']))
                ).properties(height=300)
                
                st.altair_chart(breakdown_chart, use_container_width=True)
        
        st.divider()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Parts Cost", f"${total_parts:,.0f}")
        with col2:
            st.metric("Total Labor Cost", f"${avg_labor_cost:,.0f}", "@ $50/hr")
        with col3:
            st.metric("Avg Cost per WO", f"${(total_parts + avg_labor_cost) / len(wos):,.0f}")
        with col4:
            st.metric("Total Spent", f"${total_parts + avg_labor_cost:,.0f}", "All WOs")
        
        st.divider()
        
        st.subheader("Cumulative Cost Over Time")
        
        wos_sorted = wos.sort_values('created_dt').copy()
        wos_sorted['Cumulative Cost'] = (wos_sorted['parts_cost'] + (wos_sorted['labor_hours'] * 50)).cumsum()
        
        if len(wos_sorted) > 0:
            cost_trend_chart = alt.Chart(wos_sorted).mark_line(point=True, color='#6366F1', size=3).encode(
                x=alt.X("created_dt:T", title="Date"),
                y=alt.Y("Cumulative Cost:Q", title="Cumulative Cost ($)"),
                tooltip=["created_dt", "Cumulative Cost"]
            ).properties(height=300).interactive()
            
            st.altair_chart(cost_trend_chart, use_container_width=True)

# ============================================================================
# PAGE: WORK ORDERS
# ============================================================================
def page_work_orders():
    """Work Orders page."""
    st.header("📋 Work Orders")
    
    tab1, tab2 = st.tabs(["Create New WO", "View Work Orders"])
    
    with tab1:
        st.subheader("Create New Work Order")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            created_dt = st.date_input("Created Date", datetime.now())
            created_by = st.selectbox("Created By", ["tech_001", "tech_002", "tech_003", "supervisor_001"])
            workshop = st.selectbox("Workshop", ["Riyadh_Main", "Jeddah_South", "Central"])
        
        with col2:
            assigned_to = st.selectbox("Assigned To", ["tech_001", "tech_002", "tech_003", "supervisor_001"])
            sector = st.selectbox("Sector", ["Central", "North", "South", "East", "West"])
            status = st.selectbox("Status", ["Open", "In Progress", "Completed", "Closed"])
        
        with col3:
            if status in ["Completed", "Closed"]:
                completed_dt = st.date_input("Completion Date", datetime.now())
            else:
                st.text_input("Completion Date", value="(N/A)", disabled=True)
                completed_dt = None
        
        st.divider()
        
        vehicles_df = get_vehicles_list()
        vehicle_options = [f"{row['vehicle_id']} - {row['make']} {row['model']}" for _, row in vehicles_df.iterrows()]
        selected_vehicle = st.selectbox("Select Vehicle", [""] + vehicle_options)
        
        vehicle_id = None
        if selected_vehicle:
            vehicle_id = selected_vehicle.split(" - ")[0]
        
        st.divider()
        st.subheader("Fault Classification (Cascading Dropdowns)")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            systems = [""] + list_systems()
            system = st.selectbox("System", systems, key="system_select")
        
        with col2:
            subsystems = [""]
            if system:
                subsystems = [""] + list_subsystems(system)
            subsystem = st.selectbox("Subsystem", subsystems, key="subsystem_select")
        
        with col3:
            components = [""]
            if system and subsystem:
                components = [""] + list_components(system, subsystem)
            component = st.selectbox("Component", components, key="component_select")
        
        with col4:
            failure_modes = [""]
            if system and subsystem and component:
                failure_modes = [""] + list_failure_modes(system, subsystem, component)
            failure_mode = st.selectbox("Failure Mode", failure_modes, key="failure_mode_select")
        
        recommended_action = ""
        failure_code = ""
        cause_code = ""
        resolution_code = ""
        
        if system and subsystem and component and failure_mode:
            codes = get_codes(system, subsystem, component, failure_mode)
            recommended_action = codes.get("recommended_action", "")
            failure_code = codes.get("failure_code", "")
            cause_code = codes.get("cause_code", "")
            resolution_code = codes.get("resolution_code", "")
        
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Failure Code (Auto-filled)", value=failure_code, disabled=True)
        with col2:
            st.text_input("Cause Code (Auto-filled)", value=cause_code, disabled=True)
        
        st.text_input("Resolution Code (Auto-filled)", value=resolution_code, disabled=True)
        st.text_area("Recommended Action", value=recommended_action, disabled=True, height=80)
        
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            cause_text = st.text_area("Cause Text", height=100, placeholder="Describe the root cause...")
        with col2:
            action_text = st.text_area("Action Text", height=100, placeholder="Describe the work performed...")
        
        notes = st.text_area("Notes", height=80, placeholder="Additional notes...")
        
        st.divider()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            labor_hours = st.number_input("Labor Hours", value=0.0, min_value=0.0)
        with col2:
            parts_cost = st.number_input("Parts Cost ($)", value=0.0, min_value=0.0)
        with col3:
            downtime_hours = st.number_input("Downtime Hours", value=0.0, min_value=0.0)
        
        st.divider()
        
        if st.button("💾 Save Work Order", use_container_width=True, type="primary"):
            if not vehicle_id:
                st.error("❌ Please select a vehicle")
            elif not system:
                st.error("❌ Please select a system")
            else:
                wo_data = {
                    "status": status,
                    "created_dt": created_dt,
                    "completed_dt": completed_dt,
                    "created_by": created_by,
                    "assigned_to": assigned_to,
                    "workshop": workshop,
                    "sector": sector,
                    "vehicle_id": vehicle_id,
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
                    "total_cost": parts_cost + (labor_hours * 50),
                    "downtime_hours": downtime_hours
                }
                
                success, msg = save_work_order(wo_data)
                if success:
                    st.success(msg)
                    st.balloons()
                else:
                    st.error(msg)
    
    with tab2:
        st.subheader("Work Order List")
        
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.multiselect("Filter by Status", ["Open", "In Progress", "Completed", "Closed"])
        with col2:
            vehicle_filter = st.text_input("Filter by Vehicle ID (optional)")
        
        filters = {}
        if status_filter:
            filters["status"] = status_filter[0]
        if vehicle_filter:
            filters["vehicle_id"] = vehicle_filter
        
        wos = get_work_orders(filters)
        
        if len(wos) > 0:
            st.dataframe(
                wos[["wo_id", "status", "created_dt", "vehicle_id", "system", "failure_mode", "workshop", "labor_hours", "parts_cost"]],
                use_container_width=True,
                height=400
            )
            
            if st.button("📥 Export to CSV"):
                csv = wos.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"work_orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("No work orders found.")

# ============================================================================
# PAGE: ABOUT
# ============================================================================
def page_about():
    """About page."""
    st.header("ℹ️ About AMIC FRACAS System - Enhanced (White Theme)")
    
    st.markdown("""
    ### AMIC Work Order Management & FRACAS System
    **Version 2.5 - Enhanced (White Theme)** ✨
    
    #### 🎨 Theme
    - ✅ Clean white background for professional appearance
    - ✅ Light gray sidebar for contrast
    - ✅ High contrast text for readability
    - ✅ Colorful charts with improved visibility
    - ✅ Professional button and input styling
    
    #### 🎯 Features
    - ✅ Advanced Analytics Dashboard
    - ✅ Executive Summary with KPIs
    - ✅ System Health & Reliability Metrics
    - ✅ Vehicle Health Scoring
    - ✅ Technician Performance Analytics
    - ✅ Cost Analysis & Trends
    - ✅ MTTR Calculations
    - ✅ Failure Rate Analysis
    - ✅ 30-day Trend Analysis
    """)

# ============================================================================
# MAIN APP
# ============================================================================
def main():
    """Main application."""
    
    init_db()
    
    st.markdown("""
    <style>
    .header-text {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1F2937;
        margin-bottom: 0.5rem;
    }
    .subtitle-text {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='header-text'>🚗 AMIC FRACAS System v2.5 (Enhanced - White Theme)</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle-text'>Advanced Analytics Dashboard for Work Order Management</div>", unsafe_allow_html=True)
    
    st.sidebar.title("Navigation")
    
    engine = get_engine()
    with engine.connect() as conn:
        wo_count = conn.execute(text("SELECT COUNT(*) FROM work_orders")).scalar()
    
    st.sidebar.success(f"✅ System Ready\n📦 {wo_count} Work Orders\n📊 Advanced Analytics Active")
    
    page = st.sidebar.radio("Select Page", [
        "Enhanced Dashboards",
        "Work Orders",
        "About"
    ])
    
    if page == "Enhanced Dashboards":
        page_enhanced_dashboards()
    elif page == "Work Orders":
        page_work_orders()
    elif page == "About":
        page_about()

if __name__ == "__main__":
    main()
