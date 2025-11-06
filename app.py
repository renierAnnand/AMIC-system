"""
AMIC Work Order Management & FRACAS System - COMPLETE VERSION
Advanced dashboards, analytics, KPIs, insights, AND work order creation
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
import os

# ============================================================================
# CONFIG & SESSION STATE & THEMING
# ============================================================================
st.set_page_config(
    page_title="AMIC FRACAS System Complete",
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
# DATABASE SETUP
# ============================================================================
DB_FILE = "/tmp/amic_fracas_complete.db"

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
                make TEXT,
                model TEXT,
                vehicle_type TEXT,
                owning_unit TEXT,
                system TEXT,
                subsystem TEXT,
                component TEXT,
                failure_mode TEXT,
                failure_description TEXT,
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
        result = conn.execute(text("SELECT COUNT(*) FROM work_orders"))
        wo_count = result.scalar()
    
    if wo_count == 0:
        seed_work_orders(engine)

def seed_work_orders(engine):
    """Seed database with work orders from Excel file (5000 records)."""
    excel_file = '/mnt/user-data/uploads/Fake_WorkOrders_AMIC_Enhanced_5000.xlsx'
    
    if os.path.exists(excel_file):
        try:
            st.info("📊 Loading 5,000 work orders from Excel file...")
            df = pd.read_excel(excel_file)
            
            # Clean up data
            df = df.fillna('')
            
            success_count = 0
            error_count = 0
            
            with engine.begin() as conn:
                for idx, row in df.iterrows():
                    try:
                        # Convert dates properly
                        created_dt = pd.to_datetime(row['Date Created']).date() if pd.notna(row['Date Created']) else None
                        completed_dt = pd.to_datetime(row['Completion Date']).date() if pd.notna(row['Completion Date']) else None
                        
                        # Safe value extraction
                        wo_id = str(row['Work Order ID']).strip() if row['Work Order ID'] else f'WO-{idx:06d}'
                        status = str(row['Status']).strip() if row['Status'] else 'Open'
                        
                        labor_hours = float(row['Labor Hours']) if row['Labor Hours'] and str(row['Labor Hours']).replace('.','',1).isdigit() else 0.0
                        parts_cost = float(row['Parts Cost']) if row['Parts Cost'] and str(row['Parts Cost']).replace('.','',1).isdigit() else 0.0
                        downtime_hours = float(row['Downtime Hours']) if row['Downtime Hours'] and str(row['Downtime Hours']).replace('.','',1).isdigit() else 0.0
                        
                        total_cost = parts_cost + (labor_hours * 50)
                        
                        conn.execute(text("""
                            INSERT INTO work_orders (
                                wo_id, status, created_dt, completed_dt, created_by, assigned_to,
                                workshop, sector, vehicle_id, vin, make, model, vehicle_type, owning_unit,
                                system, subsystem, component, failure_mode, failure_description,
                                failure_code, cause_code, resolution_code, 
                                cause_text, action_text, notes,
                                labor_hours, parts_cost, total_cost, downtime_hours
                            ) VALUES (
                                :woid, :status, :created, :completed, :cby, :ato,
                                :workshop, :sector, :vid, :vin, :make, :model, :vtype, :unit,
                                :sys, :sub, :comp, :fm, :fdesc,
                                :fc, :cc, :rc,
                                :cause, :action, :notes,
                                :labor, :cost, :total, :downtime
                            )
                        """), {
                            "woid": wo_id,
                            "status": status,
                            "created": created_dt,
                            "completed": completed_dt,
                            "cby": str(row['Created By']).strip() if row['Created By'] else 'Unknown',
                            "ato": str(row['Assigned To']).strip() if row['Assigned To'] else 'Unassigned',
                            "workshop": str(row['Workshop']).strip() if row['Workshop'] else 'Central',
                            "sector": str(row['Sector']).strip() if row['Sector'] else 'Central',
                            "vid": str(row['Vehicle ID']).strip() if row['Vehicle ID'] else 'Unknown',
                            "vin": str(row['VIN']).strip() if row['VIN'] else '',
                            "make": str(row['Make']).strip() if row['Make'] else '',
                            "model": str(row['Model']).strip() if row['Model'] else '',
                            "vtype": str(row['Vehicle Type']).strip() if row['Vehicle Type'] else '',
                            "unit": "Unit A",
                            "sys": str(row['System']).strip() if row['System'] else '',
                            "sub": str(row['Subsystem']).strip() if row['Subsystem'] else '',
                            "comp": str(row['Component']).strip() if row['Component'] else '',
                            "fm": str(row['Failure Mode']).strip() if row['Failure Mode'] else '',
                            "fdesc": str(row['Failure Description']).strip() if row['Failure Description'] else '',
                            "fc": str(row['Failure Code']).strip() if row['Failure Code'] else '',
                            "cc": str(row['Cause Code']).strip() if row['Cause Code'] else '',
                            "rc": str(row['Resolution Code']).strip() if row['Resolution Code'] else '',
                            "cause": str(row['Cause']).strip() if row['Cause'] else '',
                            "action": str(row['Recommended Action']).strip() if row['Recommended Action'] else '',
                            "notes": str(row['Remarks']).strip() if row['Remarks'] else '',
                            "labor": labor_hours,
                            "cost": parts_cost,
                            "total": total_cost,
                            "downtime": downtime_hours
                        })
                        success_count += 1
                    except Exception as e:
                        error_count += 1
                        if error_count <= 5:
                            st.write(f"Row {idx} error: {str(e)}")
                        continue
            
            st.success(f"✅ Loaded {success_count:,} work orders successfully!")
            if error_count > 0:
                st.warning(f"⚠️ {error_count} rows had errors (but data still loaded)")
            return
        except Exception as e:
            st.error(f"❌ Could not load Excel: {str(e)}")
            return
    else:
        st.warning(f"⚠️ Excel file not found. Creating sample data...")
        create_sample_data(engine)

def create_sample_data(engine):
    """Create sample work orders if Excel file not found."""
    sample_data = []
    systems = ["Engine", "Transmission", "Brakes", "Electrical", "HVAC", "Suspension"]
    statuses = ["Open", "In Progress", "Completed", "Closed"]
    workshops = ["Central Workshop", "North Workshop", "South Workshop", "East Workshop"]
    makes = ["Toyota", "Ford", "Chevrolet", "Honda", "Dodge"]
    
    for i in range(50):
        sample_data.append({
            "woid": f"WO-{i+1:06d}",
            "status": np.random.choice(statuses),
            "created": (datetime.now() - timedelta(days=np.random.randint(1, 90))).date(),
            "completed": None,
            "cby": "System",
            "ato": f"Tech-{np.random.randint(1,10):02d}",
            "workshop": np.random.choice(workshops),
            "sector": "Central",
            "vid": f"VEH-{np.random.randint(1,100):03d}",
            "vin": f"VIN{np.random.randint(10000,99999)}",
            "make": np.random.choice(makes),
            "model": "Model X",
            "vtype": "Truck",
            "unit": "Unit A",
            "sys": np.random.choice(systems),
            "sub": "Subsystem",
            "comp": "Component",
            "fm": "Wear",
            "fdesc": "Sample failure description",
            "fc": f"FC-{i+1}",
            "cc": f"CC-{i+1}",
            "rc": "",
            "cause": "Normal wear",
            "action": "Replace component",
            "notes": "Sample notes",
            "labor": np.random.uniform(1, 10),
            "cost": np.random.uniform(100, 1000),
            "total": 0,
            "downtime": np.random.uniform(0, 24)
        })
    
    with engine.begin() as conn:
        for data in sample_data:
            data["total"] = data["cost"] + (data["labor"] * 50)
            conn.execute(text("""
                INSERT INTO work_orders (
                    wo_id, status, created_dt, completed_dt, created_by, assigned_to,
                    workshop, sector, vehicle_id, vin, make, model, vehicle_type, owning_unit,
                    system, subsystem, component, failure_mode, failure_description,
                    failure_code, cause_code, resolution_code,
                    cause_text, action_text, notes,
                    labor_hours, parts_cost, total_cost, downtime_hours
                ) VALUES (
                    :woid, :status, :created, :completed, :cby, :ato,
                    :workshop, :sector, :vid, :vin, :make, :model, :vtype, :unit,
                    :sys, :sub, :comp, :fm, :fdesc,
                    :fc, :cc, :rc,
                    :cause, :action, :notes,
                    :labor, :cost, :total, :downtime
                )
            """), data)
    
    st.success(f"✅ Created {len(sample_data)} sample work orders!")

def get_work_orders(filters=None):
    """Get work orders with optional filters"""
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
    return round(len(wos) / vehicles_count, 2) if vehicles_count > 0 else 0

def get_system_reliability(wos):
    """Get reliability score for each system"""
    if len(wos) == 0:
        return {}
    system_failures = wos['system'].value_counts()
    total = len(wos)
    reliability = {}
    for system, count in system_failures.items():
        if system and str(system).strip():
            reliability[system] = round((1 - (count / total)) * 100, 1) if total > 0 else 0
    return dict(sorted(reliability.items(), key=lambda x: x[1], reverse=True))

def get_vehicle_health(wos):
    """Get health score for each vehicle"""
    vehicles = wos['vehicle_id'].unique()
    health_scores = {}
    for vehicle in vehicles:
        if vehicle and str(vehicle).strip():
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
        if tech and str(tech).strip():
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
# PAGE: CREATE WORK ORDER
# ============================================================================
def page_create_work_order():
    """Create new work order page."""
    st.header("➕ Create New Work Order")
    
    st.markdown("""
    <div style='background-color: #DBEAFE; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #3B82F6; margin-bottom: 2rem;'>
        <strong>📝 Instructions:</strong> Fill out the form below to create a new work order. All fields marked with * are required.
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("create_work_order_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🚗 Vehicle Information")
            vehicle_id = st.text_input("Vehicle ID *", placeholder="e.g., VEH-001")
            vin = st.text_input("VIN", placeholder="Vehicle Identification Number")
            make = st.selectbox("Make *", ["", "Toyota", "Ford", "Chevrolet", "Honda", "Dodge", "GMC", "RAM", "Nissan", "Jeep", "Other"])
            model = st.text_input("Model *", placeholder="e.g., Camry, F-150, Silverado")
            vehicle_type = st.selectbox("Vehicle Type", ["", "Sedan", "Truck", "SUV", "Van", "Bus", "Heavy Equipment", "Other"])
            
            st.subheader("📍 Location & Assignment")
            workshop = st.selectbox("Workshop *", ["", "Central Workshop", "North Workshop", "South Workshop", "East Workshop", "West Workshop", "Mobile Unit"])
            sector = st.selectbox("Sector", ["", "Central", "North", "South", "East", "West"])
            assigned_to = st.text_input("Assigned To *", placeholder="Technician name or ID")
        
        with col2:
            st.subheader("🔧 Issue Details")
            system = st.selectbox("System *", [
                "", "Engine", "Transmission", "Brakes", "Electrical", "HVAC", 
                "Suspension", "Steering", "Fuel System", "Exhaust", "Cooling System",
                "Body & Frame", "Tires & Wheels", "Safety Systems", "Other"
            ])
            subsystem = st.text_input("Subsystem", placeholder="e.g., Front Brake System")
            component = st.text_input("Component", placeholder="e.g., Brake Pads")
            
            failure_mode = st.selectbox("Failure Mode", [
                "", "Complete Failure", "Degraded Performance", "Intermittent", 
                "Leak", "Noise", "Vibration", "Warning Light", "Wear", "Other"
            ])
            
            failure_description = st.text_area("Failure Description *", 
                placeholder="Describe the issue in detail...", 
                height=100)
            
            st.subheader("💰 Cost & Time Estimates")
            estimated_hours = st.number_input("Estimated Labor Hours", min_value=0.0, max_value=100.0, value=1.0, step=0.5)
            parts_cost = st.number_input("Estimated Parts Cost ($)", min_value=0.0, max_value=50000.0, value=0.0, step=50.0)
        
        st.divider()
        
        st.subheader("📝 Additional Information")
        col3, col4 = st.columns(2)
        
        with col3:
            failure_code = st.text_input("Failure Code", placeholder="e.g., ENG-001")
            cause_code = st.text_input("Cause Code", placeholder="e.g., WEAR-01")
        
        with col4:
            priority = st.selectbox("Priority", ["Medium", "Low", "High", "Critical"], index=0)
            due_date = st.date_input("Due Date", value=datetime.now() + timedelta(days=7))
        
        notes = st.text_area("Additional Notes", placeholder="Any additional information...", height=100)
        
        st.divider()
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 3])
        
        with col_btn1:
            submit_button = st.form_submit_button("✅ Create Work Order", use_container_width=True)
        
        with col_btn2:
            cancel_button = st.form_submit_button("❌ Cancel", use_container_width=True)
    
    if submit_button:
        # Validation
        errors = []
        if not vehicle_id:
            errors.append("Vehicle ID is required")
        if not make:
            errors.append("Make is required")
        if not model:
            errors.append("Model is required")
        if not workshop:
            errors.append("Workshop is required")
        if not assigned_to:
            errors.append("Assigned To is required")
        if not system:
            errors.append("System is required")
        if not failure_description:
            errors.append("Failure Description is required")
        
        if errors:
            for error in errors:
                st.error(f"❌ {error}")
        else:
            # Create work order
            engine = get_engine()
            
            # Generate new WO ID
            with engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM work_orders"))
                count = result.scalar()
                new_wo_id = f"WO-{count + 1:06d}"
            
            # Calculate total cost
            labor_cost = estimated_hours * 50  # $50/hour
            total_cost = parts_cost + labor_cost
            
            # Insert into database
            try:
                with engine.begin() as conn:
                    conn.execute(text("""
                        INSERT INTO work_orders (
                            wo_id, status, created_dt, completed_dt, created_by, assigned_to,
                            workshop, sector, vehicle_id, vin, make, model, vehicle_type, owning_unit,
                            system, subsystem, component, failure_mode, failure_description,
                            failure_code, cause_code, resolution_code,
                            cause_text, action_text, notes,
                            labor_hours, parts_cost, total_cost, downtime_hours
                        ) VALUES (
                            :woid, :status, :created, :completed, :cby, :ato,
                            :workshop, :sector, :vid, :vin, :make, :model, :vtype, :unit,
                            :sys, :sub, :comp, :fm, :fdesc,
                            :fc, :cc, :rc,
                            :cause, :action, :notes,
                            :labor, :cost, :total, :downtime
                        )
                    """), {
                        "woid": new_wo_id,
                        "status": "Open",
                        "created": datetime.now().date(),
                        "completed": None,
                        "cby": st.session_state.current_user,
                        "ato": assigned_to,
                        "workshop": workshop,
                        "sector": sector if sector else "Central",
                        "vid": vehicle_id,
                        "vin": vin if vin else "",
                        "make": make,
                        "model": model,
                        "vtype": vehicle_type if vehicle_type else "Unknown",
                        "unit": "Unit A",
                        "sys": system,
                        "sub": subsystem if subsystem else "",
                        "comp": component if component else "",
                        "fm": failure_mode if failure_mode else "",
                        "fdesc": failure_description,
                        "fc": failure_code if failure_code else "",
                        "cc": cause_code if cause_code else "",
                        "rc": "",
                        "cause": "",
                        "action": "",
                        "notes": notes if notes else "",
                        "labor": estimated_hours,
                        "cost": parts_cost,
                        "total": total_cost,
                        "downtime": 0
                    })
                
                st.success(f"✅ Work Order {new_wo_id} created successfully!")
                
                # Show summary
                st.markdown(f"""
                <div style='background-color: #D1FAE5; padding: 1.5rem; border-radius: 0.5rem; border-left: 4px solid #10B981; margin-top: 1rem;'>
                    <h4 style='color: #065F46; margin-top: 0;'>📋 Work Order Summary</h4>
                    <p><strong>WO ID:</strong> {new_wo_id}</p>
                    <p><strong>Vehicle:</strong> {vehicle_id} - {make} {model}</p>
                    <p><strong>System:</strong> {system}</p>
                    <p><strong>Assigned To:</strong> {assigned_to}</p>
                    <p><strong>Workshop:</strong> {workshop}</p>
                    <p><strong>Estimated Cost:</strong> ${total_cost:,.2f}</p>
                    <p><strong>Status:</strong> Open</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Error creating work order: {str(e)}")
    
    if cancel_button:
        st.info("❌ Work order creation cancelled")

# ============================================================================
# PAGE: ENHANCED DASHBOARDS
# ============================================================================
def page_enhanced_dashboards():
    """Enhanced dashboards with advanced analytics"""
    st.header("📊 Advanced Analytics Dashboard")
    
    wos = get_work_orders()
    
    if len(wos) == 0:
        st.info("⏳ Loading work order data...")
        st.rerun()
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
            st.metric("Total WOs", f"{total_wos:,}", "All time")
        with col2:
            st.metric("Completion Rate", f"{completion_rate:.1f}%", f"{completed:,} completed")
        with col3:
            st.metric("MTTR (hours)", f"{calculate_mttr(wos):.1f}", "Mean Time To Repair")
        with col4:
            st.metric("Avg Downtime", f"{wos['downtime_hours'].mean():.1f}h", "Per incident")
        with col5:
            st.metric("Failure Rate", f"{calculate_failure_rate(wos):.1f}", "Per vehicle")
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Work Order Status Distribution")
            
            status_data = wos['status'].value_counts()
            status_df = pd.DataFrame({
                'Status': status_data.index,
                'Count': status_data.values
            })
            
            if len(status_df) > 0:
                status_chart = alt.Chart(status_df).mark_bar().encode(
                    x=alt.X("Status", title="Status"),
                    y=alt.Y("Count", title="Count"),
                    color=alt.Color("Status", scale=alt.Scale(
                        domain=['Completed', 'Closed', 'In Progress', 'Open'], 
                        range=['#10B981', '#059669', '#F59E0B', '#EF4444']
                    ))
                ).properties(height=300)
                
                st.altair_chart(status_chart, use_container_width=True)
        
        with col2:
            st.subheader("Top 10 Workshops by WO Count")
            
            workshop_data = wos['workshop'].value_counts().head(10)
            workshop_df = pd.DataFrame({
                'Workshop': workshop_data.index,
                'Count': workshop_data.values
            }).sort_values('Count', ascending=True)
            
            if len(workshop_df) > 0:
                workshop_chart = alt.Chart(workshop_df).mark_bar().encode(
                    y=alt.Y("Workshop", title="Workshop"),
                    x=alt.X("Count", title="Work Orders"),
                    color=alt.Color("Count", scale=alt.Scale(scheme='blues'))
                ).properties(height=300)
                
                st.altair_chart(workshop_chart, use_container_width=True)
    
    with tab2:
        st.subheader("System Health & Reliability")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Top 15 Failing Systems")
            
            system_failures = wos['system'].value_counts().head(15)
            if len(system_failures) > 0:
                system_df = pd.DataFrame({
                    'System': system_failures.index,
                    'Failures': system_failures.values
                }).sort_values('Failures', ascending=True)
                
                system_chart = alt.Chart(system_df).mark_bar().encode(
                    y=alt.Y("System", title="System"),
                    x=alt.X("Failures", title="Number of Failures"),
                    color=alt.Color("Failures", scale=alt.Scale(scheme='reds'))
                ).properties(height=300)
                
                st.altair_chart(system_chart, use_container_width=True)
        
        with col2:
            st.subheader("System Reliability Score (Top 15)")
            
            reliability = get_system_reliability(wos)
            if len(reliability) > 0:
                reliability_df = pd.DataFrame({
                    'System': list(reliability.keys())[:15],
                    'Reliability %': list(reliability.values())[:15]
                }).sort_values('Reliability %', ascending=True)
                
                reliability_chart = alt.Chart(reliability_df).mark_bar().encode(
                    y=alt.Y("System", title="System"),
                    x=alt.X("Reliability %", scale=alt.Scale(domain=[0, 100]), title="Reliability %"),
                    color=alt.Color("Reliability %", scale=alt.Scale(scheme='greens'))
                ).properties(height=300)
                
                st.altair_chart(reliability_chart, use_container_width=True)
        
        st.divider()
        
        st.subheader("Top 20 Failure Modes")
        top_failures = wos['failure_mode'].value_counts().head(20)
        if len(top_failures) > 0:
            failure_df = pd.DataFrame({
                'Failure Mode': top_failures.index,
                'Count': top_failures.values
            }).sort_values('Count', ascending=True)
            
            failure_chart = alt.Chart(failure_df).mark_bar(color='#F97316').encode(
                y=alt.Y("Failure Mode", title="Failure Mode"),
                x=alt.X("Count", title="Count"),
                color=alt.Color("Count", scale=alt.Scale(scheme='oranges'))
            ).properties(height=500)
            
            st.altair_chart(failure_chart, use_container_width=True)
    
    with tab3:
        st.subheader("Vehicle Health Analysis")
        
        health_scores = get_vehicle_health(wos)
        if len(health_scores) > 0:
            health_df = pd.DataFrame({
                'Vehicle': list(health_scores.keys())[:20],  # Top 20
                'Health Score': list(health_scores.values())[:20]
            }).sort_values('Health Score', ascending=True)
            
            health_chart = alt.Chart(health_df).mark_bar().encode(
                y=alt.Y("Vehicle", title="Vehicle"),
                x=alt.X("Health Score", scale=alt.Scale(domain=[0, 100]), title="Health Score"),
                color=alt.condition(
                    alt.datum['Health Score'] >= 70,
                    alt.value('#10B981'),
                    alt.condition(
                        alt.datum['Health Score'] >= 40,
                        alt.value('#F59E0B'),
                        alt.value('#EF4444')
                    )
                )
            ).properties(height=400)
            
            st.altair_chart(health_chart, use_container_width=True)
            
            st.divider()
            
            st.subheader("Issues by Vehicle (Top 20)")
            vehicle_issues = []
            for vehicle in sorted(wos['vehicle_id'].unique())[:20]:
                if vehicle and str(vehicle).strip():
                    vehicle_wos = wos[wos['vehicle_id'] == vehicle]
                    vehicle_issues.append({
                        'Vehicle': vehicle,
                        'Open': len(vehicle_wos[vehicle_wos['status'] == 'Open']),
                        'In Progress': len(vehicle_wos[vehicle_wos['status'] == 'In Progress']),
                        'Completed': len(vehicle_wos[vehicle_wos['status'] == 'Completed']),
                        'Total Issues': len(vehicle_wos)
                    })
            
            if vehicle_issues:
                issues_df = pd.DataFrame(vehicle_issues)
                st.dataframe(issues_df, use_container_width=True)
    
    with tab4:
        st.subheader("Technician Performance Metrics")
        
        tech_stats = get_technician_stats(wos)
        
        if len(tech_stats) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Completion Rate by Technician (Top 15)")
                
                tech_comp_df = pd.DataFrame({
                    'Technician': list(tech_stats.keys())[:15],
                    'Completion Rate %': [tech_stats[t]['completion_rate'] for t in list(tech_stats.keys())[:15]]
                }).sort_values('Completion Rate %', ascending=True)
                
                if len(tech_comp_df) > 0:
                    comp_chart = alt.Chart(tech_comp_df).mark_bar(color='#3B82F6').encode(
                        y=alt.Y("Technician", title="Technician"),
                        x=alt.X("Completion Rate %", scale=alt.Scale(domain=[0, 100]), title="Completion %"),
                        color=alt.Color("Completion Rate %", scale=alt.Scale(scheme='blues'))
                    ).properties(height=300)
                    
                    st.altair_chart(comp_chart, use_container_width=True)
            
            with col2:
                st.subheader("Average Labor Hours (Top 15)")
                
                tech_labor_df = pd.DataFrame({
                    'Technician': list(tech_stats.keys())[:15],
                    'Avg Labor Hours': [tech_stats[t]['avg_labor'] for t in list(tech_stats.keys())[:15]]
                }).sort_values('Avg Labor Hours', ascending=True)
                
                if len(tech_labor_df) > 0:
                    labor_chart = alt.Chart(tech_labor_df).mark_bar(color='#8B5CF6').encode(
                        y=alt.Y("Technician", title="Technician"),
                        x=alt.X("Avg Labor Hours", title="Hours"),
                        color=alt.Color("Avg Labor Hours", scale=alt.Scale(scheme='purples'))
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
            
            st.dataframe(tech_detail_df, use_container_width=True, height=400)
    
    with tab5:
        st.subheader("Cost Analysis & Trends")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Total Cost by System (Top 15)")
            
            cost_by_system = wos.groupby('system').agg({
                'parts_cost': 'sum',
                'labor_hours': 'sum'
            }).reset_index()
            cost_by_system['Labor Cost'] = cost_by_system['labor_hours'] * 50
            cost_by_system['Total Cost'] = cost_by_system['parts_cost'] + cost_by_system['Labor Cost']
            cost_by_system = cost_by_system.sort_values('Total Cost', ascending=True).tail(15)
            
            if len(cost_by_system) > 0:
                cost_chart = alt.Chart(cost_by_system).mark_bar(color='#DC2626').encode(
                    y=alt.Y("system", title="System"),
                    x=alt.X("Total Cost", title="Total Cost ($)"),
                    color=alt.Color("Total Cost", scale=alt.Scale(scheme='reds'))
                ).properties(height=300)
                
                st.altair_chart(cost_chart, use_container_width=True)
        
        with col2:
            st.subheader("Parts vs Labor Cost")
            
            total_parts = wos['parts_cost'].sum()
            avg_labor_cost = (wos['labor_hours'].sum() * 50)
            
            breakdown_df = pd.DataFrame({
                'Category': ['Parts Cost', 'Labor Cost'],
                'Amount': [total_parts, avg_labor_cost]
            })
            
            if len(breakdown_df) > 0:
                breakdown_chart = alt.Chart(breakdown_df).mark_arc().encode(
                    theta=alt.Theta("Amount"),
                    color=alt.Color("Category", scale=alt.Scale(domain=['Parts Cost', 'Labor Cost'], range=['#3B82F6', '#10B981']))
                ).properties(height=300)
                
                st.altair_chart(breakdown_chart, use_container_width=True)
        
        st.divider()
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_cost = total_parts + avg_labor_cost
        
        with col1:
            st.metric("Total Parts Cost", f"${total_parts:,.0f}")
        with col2:
            st.metric("Total Labor Cost", f"${avg_labor_cost:,.0f}", "@ $50/hr")
        with col3:
            st.metric("Avg Cost per WO", f"${(total_cost) / len(wos):,.0f}")
        with col4:
            st.metric("Total Invested", f"${total_cost:,.0f}", "All WOs")

# ============================================================================
# PAGE: WORK ORDERS
# ============================================================================
def page_work_orders():
    """Work Orders page."""
    st.header("📋 Work Orders")
    
    tab1, tab2, tab3 = st.tabs(["View All Work Orders", "Search & Filter", "Work Order Details"])
    
    with tab1:
        st.subheader(f"All Work Orders ({len(get_work_orders()):,} total)")
        
        wos = get_work_orders()
        
        if len(wos) > 0:
            # Display columns
            display_cols = ["wo_id", "status", "created_dt", "vehicle_id", "model", 
                           "system", "failure_mode", "workshop", "assigned_to", 
                           "labor_hours", "parts_cost", "total_cost"]
            
            # Filter to existing columns
            display_cols = [col for col in display_cols if col in wos.columns]
            
            st.dataframe(
                wos[display_cols],
                use_container_width=True,
                height=500,
                hide_index=True
            )
            
            st.divider()
            
            if st.button("📥 Export All to CSV"):
                csv = wos.to_csv(index=False)
                st.download_button(
                    label="Download CSV (All)",
                    data=csv,
                    file_name=f"all_work_orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("No work orders found.")
    
    with tab2:
        st.subheader("Search & Filter Work Orders")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.multiselect("Filter by Status", 
                                          ["Open", "In Progress", "Completed", "Closed"],
                                          default=[])
        with col2:
            vehicle_filter = st.text_input("Filter by Vehicle ID")
        with col3:
            system_filter = st.text_input("Filter by System")
        
        filters = {}
        if status_filter:
            filters["status"] = status_filter[0] if status_filter else None
        
        wos = get_work_orders(filters)
        
        if vehicle_filter:
            wos = wos[wos['vehicle_id'].str.contains(vehicle_filter, case=False, na=False)]
        
        if system_filter:
            wos = wos[wos['system'].str.contains(system_filter, case=False, na=False)]
        
        st.info(f"Found {len(wos):,} work orders")
        
        if len(wos) > 0:
            display_cols = ["wo_id", "status", "created_dt", "vehicle_id", "model", 
                           "system", "failure_mode", "workshop", "labor_hours", "parts_cost"]
            display_cols = [col for col in display_cols if col in wos.columns]
            
            st.dataframe(
                wos[display_cols],
                use_container_width=True,
                height=400,
                hide_index=True
            )
            
            if st.button("📥 Export Filtered Results to CSV"):
                csv = wos.to_csv(index=False)
                st.download_button(
                    label="Download CSV (Filtered)",
                    data=csv,
                    file_name=f"filtered_work_orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    
    with tab3:
        st.subheader("View Work Order Details")
        
        wos = get_work_orders()
        
        if len(wos) > 0:
            wo_ids = wos['wo_id'].tolist()
            selected_wo = st.selectbox("Select Work Order", wo_ids)
            
            if selected_wo:
                wo_data = wos[wos['wo_id'] == selected_wo].iloc[0]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    <div style='background-color: #F9FAFB; padding: 1.5rem; border-radius: 0.5rem; border: 1px solid #E5E7EB;'>
                        <h4 style='color: #111827; margin-top: 0;'>📋 Work Order: {wo_data['wo_id']}</h4>
                        <p><strong>Status:</strong> <span style='color: #3B82F6;'>{wo_data['status']}</span></p>
                        <p><strong>Created:</strong> {wo_data['created_dt']}</p>
                        <p><strong>Created By:</strong> {wo_data['created_by']}</p>
                        <p><strong>Assigned To:</strong> {wo_data['assigned_to']}</p>
                        <p><strong>Workshop:</strong> {wo_data['workshop']}</p>
                        <p><strong>Sector:</strong> {wo_data['sector']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div style='background-color: #F9FAFB; padding: 1.5rem; border-radius: 0.5rem; border: 1px solid #E5E7EB; margin-top: 1rem;'>
                        <h4 style='color: #111827; margin-top: 0;'>💰 Cost Information</h4>
                        <p><strong>Labor Hours:</strong> {wo_data['labor_hours']:.1f} hrs</p>
                        <p><strong>Parts Cost:</strong> ${wo_data['parts_cost']:,.2f}</p>
                        <p><strong>Total Cost:</strong> <span style='color: #10B981; font-size: 1.2em;'>${wo_data['total_cost']:,.2f}</span></p>
                        <p><strong>Downtime:</strong> {wo_data['downtime_hours']:.1f} hrs</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div style='background-color: #F9FAFB; padding: 1.5rem; border-radius: 0.5rem; border: 1px solid #E5E7EB;'>
                        <h4 style='color: #111827; margin-top: 0;'>🚗 Vehicle Information</h4>
                        <p><strong>Vehicle ID:</strong> {wo_data['vehicle_id']}</p>
                        <p><strong>VIN:</strong> {wo_data['vin']}</p>
                        <p><strong>Make/Model:</strong> {wo_data['make']} {wo_data['model']}</p>
                        <p><strong>Type:</strong> {wo_data['vehicle_type']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div style='background-color: #F9FAFB; padding: 1.5rem; border-radius: 0.5rem; border: 1px solid #E5E7EB; margin-top: 1rem;'>
                        <h4 style='color: #111827; margin-top: 0;'>🔧 Technical Details</h4>
                        <p><strong>System:</strong> {wo_data['system']}</p>
                        <p><strong>Subsystem:</strong> {wo_data['subsystem']}</p>
                        <p><strong>Component:</strong> {wo_data['component']}</p>
                        <p><strong>Failure Mode:</strong> {wo_data['failure_mode']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.divider()
                
                st.markdown(f"""
                <div style='background-color: #FEF3C7; padding: 1.5rem; border-radius: 0.5rem; border-left: 4px solid #F59E0B;'>
                    <h4 style='color: #78350F; margin-top: 0;'>📝 Failure Description</h4>
                    <p style='color: #78350F;'>{wo_data['failure_description']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if wo_data['notes']:
                    st.markdown(f"""
                    <div style='background-color: #DBEAFE; padding: 1.5rem; border-radius: 0.5rem; border-left: 4px solid #3B82F6; margin-top: 1rem;'>
                        <h4 style='color: #1E40AF; margin-top: 0;'>📌 Notes</h4>
                        <p style='color: #1E40AF;'>{wo_data['notes']}</p>
                    </div>
                    """, unsafe_allow_html=True)

# ============================================================================
# PAGE: ABOUT
# ============================================================================
def page_about():
    """About page."""
    st.header("ℹ️ About AMIC FRACAS System")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### AMIC Work Order Management & FRACAS System
        **Version 4.0 - Complete with Work Order Creation** ✨
        
        #### 🎨 Features
        - ✅ Clean white theme
        - ✅ Advanced analytics dashboards
        - ✅ Executive summary with KPIs
        - ✅ System health & reliability metrics
        - ✅ Vehicle health scoring
        - ✅ Technician performance analytics
        - ✅ Cost analysis & trends
        - ✅ **Create new work orders**
        - ✅ Search & filter capabilities
        - ✅ Detailed work order views
        - ✅ CSV export functions
        """)
    
    with col2:
        wos = get_work_orders()
        st.info(f"""
        ### 📊 System Status
        
        **Total Work Orders:** {len(wos):,}
        
        **Status Distribution:**
        - Completed: {len(wos[wos['status'] == 'Completed']):,}
        - Open: {len(wos[wos['status'] == 'Open']):,}
        - In Progress: {len(wos[wos['status'] == 'In Progress']):,}
        - Closed: {len(wos[wos['status'] == 'Closed']):,}
        """)
    
    st.divider()
    
    st.markdown("""
    #### 🚀 How to Use
    
    **1. View Dashboards**
    - Navigate to "📊 Enhanced Dashboards" to see analytics
    - Explore executive summary, system health, vehicle analysis, technician performance, and cost trends
    
    **2. Create Work Orders**
    - Click on "➕ Create Work Order" in the sidebar
    - Fill out the comprehensive form with vehicle, issue, and cost details
    - Submit to add new work orders to the system
    
    **3. Manage Work Orders**
    - View all work orders in "📋 Work Orders"
    - Search and filter to find specific work orders
    - View detailed information for each work order
    - Export data to CSV for external analysis
    
    #### 💡 Tips
    - All required fields are marked with *
    - The system automatically calculates total cost based on labor hours ($50/hr) and parts cost
    - Use filters to narrow down work orders by status, vehicle, or system
    - Charts update automatically as you add new work orders
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
    
    st.markdown("<div class='header-text'>🚗 AMIC FRACAS System v4.0</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle-text'>Complete Work Order Management System with Advanced Analytics</div>", unsafe_allow_html=True)
    
    st.sidebar.title("🚗 Navigation")
    
    engine = get_engine()
    with engine.connect() as conn:
        wo_count = conn.execute(text("SELECT COUNT(*) FROM work_orders")).scalar()
    
    st.sidebar.success(f"✅ System Ready\n📦 {wo_count:,} Work Orders\n📊 Full Features Active")
    
    page = st.sidebar.radio("Select Page", [
        "📊 Enhanced Dashboards",
        "➕ Create Work Order",
        "📋 Work Orders",
        "ℹ️ About"
    ])
    
    if page == "📊 Enhanced Dashboards":
        page_enhanced_dashboards()
    elif page == "➕ Create Work Order":
        page_create_work_order()
    elif page == "📋 Work Orders":
        page_work_orders()
    elif page == "ℹ️ About":
        page_about()

if __name__ == "__main__":
    main()
