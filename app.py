"""
AMIC Work Order Management & FRACAS System - PRODUCTION DEMO VERSION
All features + Stability fixes + Proper error handling
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
import altair as alt

# ============================================================================
# CONFIG
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
[data-testid="stAppViewContainer"] { background-color: #FFFFFF; color: #111827; }
[data-testid="stSidebar"] { background-color: #F9FAFB; }
[data-testid="stMain"] { background-color: #FFFFFF; }
.stButton > button { background-color: #3B82F6; color: white; border: none; border-radius: 6px; }
.stButton > button:hover { background-color: #2563EB; }
h1, h2, h3 { color: #111827; }
.stMetric { background-color: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CATALOGUE HIERARCHY
# ============================================================================
CATALOGUE_HIERARCHY = {
    "HVAC": {
        "Air Conditioning": {
            "Compressor": {
                "Mechanical seizure": {"failure_code": "HVAC-AC-001", "cause_code": "HVAC-AC-C001", "resolution_code": "HVAC-AC-R001", "recommended_action": "Replace compressor; Replace clutch; Flush circuit; Replace filter/drier; Vacuum & recharge to spec"},
                "Insufficient displacement": {"failure_code": "HVAC-AC-002", "cause_code": "HVAC-AC-C002", "resolution_code": "HVAC-AC-R002", "recommended_action": "Replace compressor; Check displacement; Recharge system"},
            },
            "Condenser": {
                "Leak at tubes": {"failure_code": "HVAC-AC-003", "cause_code": "HVAC-AC-C003", "resolution_code": "HVAC-AC-R003", "recommended_action": "Replace condenser; Clean fins; Leak test"},
                "Fin blockage": {"failure_code": "HVAC-AC-004", "cause_code": "HVAC-AC-C004", "resolution_code": "HVAC-AC-R004", "recommended_action": "Clean fins; Replace if damaged"}
            }
        },
        "Heating": {
            "Heater Core": {
                "Leak": {"failure_code": "HVAC-HT-001", "cause_code": "HVAC-HT-C001", "resolution_code": "HVAC-HT-R001", "recommended_action": "Replace heater core; Flush circuit"},
                "Blockage": {"failure_code": "HVAC-HT-002", "cause_code": "HVAC-HT-C002", "resolution_code": "HVAC-HT-R002", "recommended_action": "Flush heater core; Replace if necessary"}
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
            }
        }
    },
    "Brakes": {
        "Hydraulic": {
            "Master Cylinder": {
                "Seal bypass": {"failure_code": "BRK-HYD-001", "cause_code": "BRK-HYD-C001", "resolution_code": "BRK-HYD-R001", "recommended_action": "Replace master cylinder; Bleed system"},
            }
        },
        "Friction": {
            "Pads/Shoes": {
                "Worn to backing": {"failure_code": "BRK-FRI-001", "cause_code": "BRK-FRI-C001", "resolution_code": "BRK-FRI-R001", "recommended_action": "Replace brake pads; Service hardware"},
                "Glazed": {"failure_code": "BRK-FRI-002", "cause_code": "BRK-FRI-C002", "resolution_code": "BRK-FRI-R002", "recommended_action": "Replace pads; Clean rotors"}
            }
        }
    },
    "Suspension": {
        "Front": {
            "Shocks": {
                "Seal leak": {"failure_code": "SUS-FRO-001", "cause_code": "SUS-FRO-C001", "resolution_code": "SUS-FRO-R001", "recommended_action": "Replace shock absorber"},
                "Gas loss": {"failure_code": "SUS-FRO-002", "cause_code": "SUS-FRO-C002", "resolution_code": "SUS-FRO-R002", "recommended_action": "Replace shock"}
            }
        }
    },
    "Electrical/Power": {
        "Battery System": {
            "12V Battery": {
                "Low capacity": {"failure_code": "ELE-BAT-001", "cause_code": "ELE-BAT-C001", "resolution_code": "ELE-BAT-R001", "recommended_action": "Replace battery; Clean terminals"},
                "Terminal corrosion": {"failure_code": "ELE-BAT-002", "cause_code": "ELE-BAT-C002", "resolution_code": "ELE-BAT-R002", "recommended_action": "Clean terminals; Replace if damaged"}
            }
        }
    },
    "Tires/Wheels": {
        "Rolling Assembly": {
            "Tires": {
                "Puncture": {"failure_code": "TIR-RLL-001", "cause_code": "TIR-RLL-C001", "resolution_code": "TIR-RLL-R001", "recommended_action": "Repair/replace tire; Balance; Align"},
                "Uneven wear": {"failure_code": "TIR-RLL-002", "cause_code": "TIR-RLL-C002", "resolution_code": "TIR-RLL-R002", "recommended_action": "Replace tire; Align vehicle"}
            }
        }
    }
}

# ============================================================================
# DATABASE
# ============================================================================
DB_FILE = "/tmp/amic_fracas_demo.db"

@st.cache_resource
def get_engine():
    return create_engine(
        f"sqlite:///{DB_FILE}",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )

def init_db():
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
        vc = conn.execute(text("SELECT COUNT(*) FROM vehicles")).scalar()
        wc = conn.execute(text("SELECT COUNT(*) FROM work_orders")).scalar()
    
    if vc == 0:
        seed_vehicles(engine)
    if wc == 0:
        seed_work_orders(engine)

def seed_vehicles(engine):
    vehicles = [
        ("VEH-0001", "JN15679D00000001", "Nissan", "Patrol", 2022, "SUV", "Unit A", "2022-05-15"),
        ("VEH-0002", "JTE45678B00000002", "Toyota", "Hilux", 2021, "Pickup", "Unit B", "2021-08-20"),
        ("VEH-0003", "HU23456789000003", "Hyundai", "HD65", 2020, "Truck", "Unit C", "2020-12-01"),
        ("VEH-0004", "JN15679D00000004", "Nissan", "Urvan", 2023, "Van", "Unit A", "2023-02-10"),
        ("VEH-0005", "JTE45678B00000005", "Toyota", "Land Cruiser", 2019, "SUV", "Unit D", "2019-11-30"),
    ]
    
    with engine.begin() as conn:
        for v in vehicles:
            try:
                conn.execute(text(
                    "INSERT INTO vehicles (vehicle_id, vin, make, model, year, vehicle_type, owning_unit, in_service_dt, status) VALUES (:vid, :vin, :make, :model, :year, :vtype, :unit, :dt, 'Active')"
                ), {"vid": v[0], "vin": v[1], "make": v[2], "model": v[3], "year": v[4], "vtype": v[5], "unit": v[6], "dt": v[7]})
            except:
                pass

def seed_work_orders(engine):
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
        ("Suspension", "Front", "Shocks", "Seal leak", "SUS-FRO-001", "SUS-FRO-C001", "SUS-FRO-R001"),
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
                    INSERT INTO work_orders 
                    (wo_id, status, created_dt, completed_dt, created_by, assigned_to, workshop, sector, vehicle_id, vin, model, vehicle_type, owning_unit, system, subsystem, component, failure_mode, failure_code, cause_code, resolution_code, labor_hours, parts_cost, total_cost, downtime_hours)
                    VALUES (:woid, :status, :created, :completed, :cby, :ato, :workshop, :sector, :vid, :vin, :model, :vtype, :unit, :sys, :sub, :comp, :fm, :fc, :cc, :rc, :labor, :cost, :total, :downtime)
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
                    "total": round(np.random.uniform(500, 3000), 2),
                    "downtime": round(np.random.uniform(2, 72), 1)
                })
            except:
                continue

# ============================================================================
# HELPERS
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
        return CATALOGUE_HIERARCHY[system][subsystem][component][failure_mode]
    except:
        return {"failure_code": "", "cause_code": "", "resolution_code": "", "recommended_action": ""}

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
    
    if not wo_data.get("vehicle_id") or not wo_data.get("system"):
        return False, "Vehicle and System required"
    
    try:
        with engine.begin() as conn:
            wo_id = next_id("WO", "work_orders", "wo_id")
            wo_data["wo_id"] = wo_id
            cols = ", ".join(wo_data.keys())
            placeholders = ", ".join([f":{k}" for k in wo_data.keys()])
            conn.execute(text(f"INSERT INTO work_orders ({cols}) VALUES ({placeholders})"), wo_data)
        return True, f"✅ Work Order saved: {wo_id}"
    except Exception as e:
        return False, f"Error: {str(e)[:100]}"

def get_work_orders(filters=None):
    engine = get_engine()
    query = "SELECT * FROM work_orders WHERE 1=1"
    params = {}
    if filters:
        if filters.get("status"):
            query += " AND status = :status"
            params["status"] = filters["status"]
    query += " ORDER BY created_dt DESC"
    return pd.read_sql(query, engine, params=params)

def get_vehicles_list():
    engine = get_engine()
    return pd.read_sql("SELECT vehicle_id, vin, make, model, year FROM vehicles ORDER BY vehicle_id", engine)

# ============================================================================
# ANALYTICS
# ============================================================================
def calculate_metrics(wos):
    if len(wos) == 0:
        return {'total': 0, 'completed': 0, 'completion_rate': 0, 'mttr': 0, 'avg_downtime': 0}
    
    total = len(wos)
    completed = len(wos[wos['status'] == 'Completed'])
    completed_wos = wos[wos['status'].isin(['Completed', 'Closed'])]
    
    return {
        'total': total,
        'completed': completed,
        'completion_rate': (completed / total * 100) if total > 0 else 0,
        'mttr': completed_wos['labor_hours'].mean() if len(completed_wos) > 0 else 0,
        'avg_downtime': wos['downtime_hours'].mean() if len(wos) > 0 else 0,
    }

# ============================================================================
# PAGES
# ============================================================================
def page_dashboards():
    st.header("📊 Advanced Analytics Dashboard")
    
    wos = get_work_orders()
    
    if len(wos) == 0:
        st.warning("No work orders available")
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
        metrics = calculate_metrics(wos)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total WOs", int(metrics['total']))
        with col2:
            st.metric("Completion Rate", f"{metrics['completion_rate']:.1f}%")
        with col3:
            st.metric("MTTR (hrs)", f"{metrics['mttr']:.1f}")
        with col4:
            st.metric("Avg Downtime", f"{metrics['avg_downtime']:.1f}h")
        with col5:
            open_wos = len(wos[wos['status'] == 'Open'])
            st.metric("Open WOs", int(open_wos))
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Work Order Trends (Last 30 Days)")
            today = datetime.now().date()
            daily_data = []
            for i in range(30):
                date = today - timedelta(days=29-i)
                count = len(wos[pd.to_datetime(wos['created_dt']).dt.date == date])
                daily_data.append({"Date": date, "WOs": count})
            
            trend_df = pd.DataFrame(daily_data)
            try:
                chart = alt.Chart(trend_df).mark_line(point=True).encode(
                    x='Date:T',
                    y='WOs:Q'
                ).properties(height=300)
                st.altair_chart(chart, use_container_width=True)
            except:
                st.dataframe(trend_df)
        
        with col2:
            st.subheader("Status Distribution")
            status_data = wos['status'].value_counts().reset_index()
            status_data.columns = ['Status', 'Count']
            try:
                chart = alt.Chart(status_data).mark_bar().encode(
                    x='Status:N',
                    y='Count:Q',
                    color='Status:N'
                ).properties(height=300)
                st.altair_chart(chart, use_container_width=True)
            except:
                st.dataframe(status_data)
    
    with tab2:
        st.subheader("System Health & Reliability")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Top Failing Systems")
            system_data = wos['system'].value_counts().head(10).reset_index()
            system_data.columns = ['System', 'Count']
            try:
                chart = alt.Chart(system_data).mark_bar().encode(
                    x='Count:Q',
                    y=alt.Y('System:N')
                ).properties(height=300)
                st.altair_chart(chart, use_container_width=True)
            except:
                st.dataframe(system_data)
        
        with col2:
            st.subheader("System Reliability Score")
            system_failures = wos['system'].value_counts()
            total = len(wos)
            reliability_data = []
            for system, count in system_failures.items():
                reliability = (1 - (count / total)) * 100
                reliability_data.append({'System': system, 'Reliability %': reliability})
            
            reliability_df = pd.DataFrame(reliability_data).sort_values('Reliability %', ascending=False).head(10)
            try:
                chart = alt.Chart(reliability_df).mark_bar().encode(
                    x=alt.X('Reliability %:Q', scale=alt.Scale(domain=[0, 100])),
                    y='System:N'
                ).properties(height=300)
                st.altair_chart(chart, use_container_width=True)
            except:
                st.dataframe(reliability_df)
        
        st.divider()
        st.subheader("Top Failure Modes")
        failure_data = wos['failure_mode'].value_counts().head(15).reset_index()
        failure_data.columns = ['Failure Mode', 'Count']
        try:
            chart = alt.Chart(failure_data).mark_bar().encode(
                x='Count:Q',
                y=alt.Y('Failure Mode:N')
            ).properties(height=400)
            st.altair_chart(chart, use_container_width=True)
        except:
            st.dataframe(failure_data)
    
    with tab3:
        st.subheader("Vehicle Health Analysis")
        
        health_data = []
        for vid in wos['vehicle_id'].unique():
            v_wos = wos[wos['vehicle_id'] == vid]
            open_count = len(v_wos[v_wos['status'] == 'Open'])
            total_issues = len(v_wos)
            health = max(0, 100 - (open_count * 20) - (total_issues * 2))
            health_data.append({'Vehicle': vid, 'Health Score': health, 'Open': open_count, 'Total': total_issues})
        
        health_df = pd.DataFrame(health_data)
        try:
            chart = alt.Chart(health_df).mark_bar().encode(
                x=alt.X('Health Score:Q', scale=alt.Scale(domain=[0, 100])),
                y='Vehicle:N',
                color=alt.condition(alt.datum['Health Score'] >= 70, alt.value('#10B981'), alt.value('#EF4444'))
            ).properties(height=300)
            st.altair_chart(chart, use_container_width=True)
        except:
            st.dataframe(health_df)
    
    with tab4:
        st.subheader("Technician Performance")
        
        tech_data = []
        for tech in wos['assigned_to'].unique():
            tech_wos = wos[wos['assigned_to'] == tech]
            completed = len(tech_wos[tech_wos['status'] == 'Completed'])
            total = len(tech_wos)
            rate = (completed / total * 100) if total > 0 else 0
            tech_data.append({'Technician': tech, 'Completion Rate': rate, 'Total': total})
        
        tech_df = pd.DataFrame(tech_data)
        try:
            chart = alt.Chart(tech_df).mark_bar().encode(
                x=alt.X('Completion Rate:Q', scale=alt.Scale(domain=[0, 100])),
                y='Technician:N',
                color='Completion Rate:Q'
            ).properties(height=300)
            st.altair_chart(chart, use_container_width=True)
        except:
            st.dataframe(tech_df)
    
    with tab5:
        st.subheader("Cost Analysis")
        
        total_parts = wos['parts_cost'].sum()
        total_labor = (wos['labor_hours'].sum() * 50)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Parts", f"${total_parts:,.0f}")
        with col2:
            st.metric("Total Labor", f"${total_labor:,.0f}")
        with col3:
            st.metric("Avg Cost/WO", f"${(total_parts + total_labor) / len(wos):,.0f}")
        with col4:
            st.metric("Total Cost", f"${total_parts + total_labor:,.0f}")
        
        st.divider()
        
        cost_data = wos.groupby('system')['parts_cost'].sum().reset_index().sort_values('parts_cost', ascending=False).head(10)
        cost_data.columns = ['System', 'Cost']
        try:
            chart = alt.Chart(cost_data).mark_bar().encode(
                x='Cost:Q',
                y=alt.Y('System:N')
            ).properties(height=300)
            st.altair_chart(chart, use_container_width=True)
        except:
            st.dataframe(cost_data)

def page_work_orders():
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
        vehicle_options = [""] + [f"{row['vehicle_id']} - {row['make']} {row['model']}" for _, row in vehicles_df.iterrows()]
        selected_vehicle = st.selectbox("Select Vehicle", vehicle_options)
        
        vehicle_id = None
        if selected_vehicle and selected_vehicle != "":
            vehicle_id = selected_vehicle.split(" - ")[0]
        
        st.divider()
        st.subheader("Fault Classification")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            systems = [""] + list_systems()
            system = st.selectbox("System", systems, key="sys")
        
        with col2:
            subsystems = [""] if not system else [""] + list_subsystems(system)
            subsystem = st.selectbox("Subsystem", subsystems, key="sub")
        
        with col3:
            components = [""] if not (system and subsystem) else [""] + list_components(system, subsystem)
            component = st.selectbox("Component", components, key="comp")
        
        with col4:
            failure_modes = [""] if not (system and subsystem and component) else [""] + list_failure_modes(system, subsystem, component)
            failure_mode = st.selectbox("Failure Mode", failure_modes, key="fm")
        
        failure_code = ""
        cause_code = ""
        resolution_code = ""
        recommended_action = ""
        
        if system and subsystem and component and failure_mode:
            codes = get_codes(system, subsystem, component, failure_mode)
            failure_code = codes.get("failure_code", "")
            cause_code = codes.get("cause_code", "")
            resolution_code = codes.get("resolution_code", "")
            recommended_action = codes.get("recommended_action", "")
        
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Failure Code", value=failure_code, disabled=True)
        with col2:
            st.text_input("Cause Code", value=cause_code, disabled=True)
        
        st.text_input("Resolution Code", value=resolution_code, disabled=True)
        st.text_area("Recommended Action", value=recommended_action, disabled=True, height=60)
        
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            cause_text = st.text_area("Cause Text", height=80)
        with col2:
            action_text = st.text_area("Action Text", height=80)
        
        notes = st.text_area("Notes", height=60)
        
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
                    "created_dt": created_dt.strftime('%Y-%m-%d'),
                    "completed_dt": completed_dt.strftime('%Y-%m-%d') if completed_dt else None,
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
                    st.rerun()
                else:
                    st.error(msg)
    
    with tab2:
        st.subheader("Work Order List")
        
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.multiselect("Filter by Status", ["Open", "In Progress", "Completed", "Closed"])
        with col2:
            vehicle_filter = st.text_input("Filter by Vehicle ID")
        
        filters = {}
        if status_filter:
            filters["status"] = status_filter[0]
        
        wos = get_work_orders(filters)
        
        if vehicle_filter:
            wos = wos[wos['vehicle_id'].str.contains(vehicle_filter, case=False, na=False)]
        
        if len(wos) > 0:
            st.dataframe(
                wos[["wo_id", "status", "created_dt", "vehicle_id", "system", "failure_mode", "labor_hours", "parts_cost"]],
                use_container_width=True,
                height=400
            )
            
            csv = wos.to_csv(index=False)
            st.download_button(
                "📥 Export to CSV",
                csv,
                f"work_orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "text/csv"
            )
        else:
            st.info("No work orders found")

def page_about():
    st.header("ℹ️ About AMIC FRACAS System")
    st.markdown("""
    ### AMIC FRACAS System v2.5 - PRODUCTION DEMO
    
    **Status**: ✅ All Features Active
    
    #### Features
    - ✅ Advanced Analytics Dashboard (5 tabs)
    - ✅ Work Order Creation with Cascading Dropdowns
    - ✅ System Health & Reliability Analysis
    - ✅ Vehicle Health Scoring
    - ✅ Technician Performance Tracking
    - ✅ Cost Analysis & Trends
    - ✅ MTTR Calculations
    - ✅ 300+ Demo Work Orders
    - ✅ Professional White Theme
    - ✅ Error Handling & Stability
    """)

# ============================================================================
# MAIN
# ============================================================================
def main():
    init_db()
    
    st.markdown("""
    <style>
    .header { font-size: 2.5rem; font-weight: bold; color: #1F2937; }
    .subtitle { font-size: 1.1rem; color: #4B5563; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='header'>🚗 AMIC FRACAS System v2.5</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Advanced Analytics Dashboard for Work Order Management</div>", unsafe_allow_html=True)
    
    st.sidebar.title("Navigation")
    
    engine = get_engine()
    with engine.connect() as conn:
        wo_count = conn.execute(text("SELECT COUNT(*) FROM work_orders")).scalar()
    
    st.sidebar.success(f"✅ System Ready\n📦 {wo_count} Work Orders\n📊 Analytics Active")
    
    page = st.sidebar.radio("Select Page", ["Enhanced Dashboards", "Work Orders", "About"])
    
    if page == "Enhanced Dashboards":
        page_dashboards()
    elif page == "Work Orders":
        page_work_orders()
    elif page == "About":
        page_about()

if __name__ == "__main__":
    main()
