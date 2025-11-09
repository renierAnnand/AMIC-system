"""
AMIC FRACAS System - ENHANCED DEMO VERSION
✅ Full cascading dropdowns with detailed catalogue
✅ Automatic code generation
✅ Complete dashboards and analytics
✅ Ready for professional demonstration
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
import random

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="AMIC FRACAS System - Demo Enhanced",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# SESSION STATE
# ============================================================================
if "app_initialized" not in st.session_state:
    st.session_state.app_initialized = False
if "current_user" not in st.session_state:
    st.session_state.current_user = "tech_001"
if "db_engine" not in st.session_state:
    st.session_state.db_engine = None

# ============================================================================
# STYLING - WHITE THEME
# ============================================================================
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #FFFFFF;
    color: #111827;
}
[data-testid="stSidebar"] {
    background-color: #F9FAFB;
}
.stButton > button {
    background-color: #3B82F6;
    color: white;
    border-radius: 6px;
    font-weight: 500;
}
.stButton > button:hover {
    background-color: #2563EB;
}
.stMetric {
    background-color: #F9FAFB;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 1.5rem;
}
h1, h2, h3 {
    color: #111827;
}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# ENHANCED CATALOGUE HIERARCHY - DETAILED STRUCTURE
# This is a subset showing the pattern - expandable to all 427 entries
# ============================================================================
CATALOGUE_HIERARCHY = {
    "HVAC": {
        "Air Conditioning": {
            "Compressor": {
                "Mechanical seizure": {
                    "failure_code": "HVAC-AC-001",
                    "cause_code": "HVAC-AC-C001",
                    "resolution_code": "HVAC-AC-R001",
                    "recommended_action": "Replace compressor; Replace clutch; Flush circuit; Replace filter/drier; Vacuum & recharge"
                },
                "Shaft seal leak": {
                    "failure_code": "HVAC-AC-002",
                    "cause_code": "HVAC-AC-C002",
                    "resolution_code": "HVAC-AC-R002",
                    "recommended_action": "Replace shaft seal; Check refrigerant level; Pressure test system"
                },
                "Clutch failure": {
                    "failure_code": "HVAC-AC-003",
                    "cause_code": "HVAC-AC-C003",
                    "resolution_code": "HVAC-AC-R003",
                    "recommended_action": "Replace clutch assembly; Check electrical connections; Test operation"
                }
            },
            "Condenser": {
                "Leak at tubes": {
                    "failure_code": "HVAC-AC-010",
                    "cause_code": "HVAC-AC-C010",
                    "resolution_code": "HVAC-AC-R010",
                    "recommended_action": "Replace condenser; Clean fins; Leak test; Vacuum & recharge"
                },
                "Fin blockage": {
                    "failure_code": "HVAC-AC-011",
                    "cause_code": "HVAC-AC-C011",
                    "resolution_code": "HVAC-AC-R011",
                    "recommended_action": "Clean condenser fins; Check airflow; Verify fan operation"
                }
            },
            "Blower Motor": {
                "Motor burnt": {
                    "failure_code": "HVAC-AC-020",
                    "cause_code": "HVAC-AC-C020",
                    "resolution_code": "HVAC-AC-R020",
                    "recommended_action": "Replace blower motor; Inspect resistor; Verify airflow"
                },
                "Bearing noise": {
                    "failure_code": "HVAC-AC-021",
                    "cause_code": "HVAC-AC-C021",
                    "resolution_code": "HVAC-AC-R021",
                    "recommended_action": "Replace blower motor; Lubricate bearings; Check mounting"
                }
            }
        },
        "Heating": {
            "Heater Core": {
                "Core leak": {
                    "failure_code": "HVAC-HT-001",
                    "cause_code": "HVAC-HT-C001",
                    "resolution_code": "HVAC-HT-R001",
                    "recommended_action": "Replace heater core; Flush circuit; Bleed system"
                },
                "Blockage": {
                    "failure_code": "HVAC-HT-002",
                    "cause_code": "HVAC-HT-C002",
                    "resolution_code": "HVAC-HT-R002",
                    "recommended_action": "Flush heater core; Check coolant flow; Replace if needed"
                }
            }
        }
    },
    "Engine": {
        "Fuel System": {
            "Fuel Pump": {
                "Pump failure": {
                    "failure_code": "ENG-FUEL-001",
                    "cause_code": "ENG-FUEL-C001",
                    "resolution_code": "ENG-FUEL-R001",
                    "recommended_action": "Replace fuel pump; Check electrical; Verify fuel quality"
                },
                "Low pressure": {
                    "failure_code": "ENG-FUEL-002",
                    "cause_code": "ENG-FUEL-C002",
                    "resolution_code": "ENG-FUEL-R002",
                    "recommended_action": "Replace pump; Check filter; Test pressure"
                }
            },
            "Fuel Injectors": {
                "Injector clogged": {
                    "failure_code": "ENG-FUEL-010",
                    "cause_code": "ENG-FUEL-C010",
                    "resolution_code": "ENG-FUEL-R010",
                    "recommended_action": "Clean injectors; Replace if needed; Check fuel quality"
                },
                "Injector leak": {
                    "failure_code": "ENG-FUEL-011",
                    "cause_code": "ENG-FUEL-C011",
                    "resolution_code": "ENG-FUEL-R011",
                    "recommended_action": "Replace injector; Replace seals; Test spray pattern"
                }
            }
        },
        "Ignition": {
            "Spark Plugs": {
                "Fouled plugs": {
                    "failure_code": "ENG-IGN-001",
                    "cause_code": "ENG-IGN-C001",
                    "resolution_code": "ENG-IGN-R001",
                    "recommended_action": "Replace spark plugs; Check gap; Verify ignition timing"
                },
                "Worn electrodes": {
                    "failure_code": "ENG-IGN-002",
                    "cause_code": "ENG-IGN-C002",
                    "resolution_code": "ENG-IGN-R002",
                    "recommended_action": "Replace spark plugs; Adjust gap to spec"
                }
            },
            "Ignition Coils": {
                "Coil failure": {
                    "failure_code": "ENG-IGN-010",
                    "cause_code": "ENG-IGN-C010",
                    "resolution_code": "ENG-IGN-R010",
                    "recommended_action": "Replace ignition coil; Check connections; Test resistance"
                }
            }
        },
        "Cooling": {
            "Radiator": {
                "Radiator leak": {
                    "failure_code": "ENG-COOL-001",
                    "cause_code": "ENG-COOL-C001",
                    "resolution_code": "ENG-COOL-R001",
                    "recommended_action": "Replace radiator; Pressure test; Check coolant level"
                },
                "Clogged radiator": {
                    "failure_code": "ENG-COOL-002",
                    "cause_code": "ENG-COOL-C002",
                    "resolution_code": "ENG-COOL-R002",
                    "recommended_action": "Flush radiator; Clean fins; Check thermostat"
                }
            },
            "Water Pump": {
                "Pump leak": {
                    "failure_code": "ENG-COOL-010",
                    "cause_code": "ENG-COOL-C010",
                    "resolution_code": "ENG-COOL-R010",
                    "recommended_action": "Replace water pump; Replace gasket; Check belt tension"
                },
                "Bearing failure": {
                    "failure_code": "ENG-COOL-011",
                    "cause_code": "ENG-COOL-C011",
                    "resolution_code": "ENG-COOL-R011",
                    "recommended_action": "Replace water pump; Inspect drive belt"
                }
            }
        }
    },
    "Transmission": {
        "Automatic": {
            "Transmission Fluid": {
                "Low fluid": {
                    "failure_code": "TRANS-AT-001",
                    "cause_code": "TRANS-AT-C001",
                    "resolution_code": "TRANS-AT-R001",
                    "recommended_action": "Check for leaks; Add fluid to proper level; Replace filter"
                },
                "Contaminated fluid": {
                    "failure_code": "TRANS-AT-002",
                    "cause_code": "TRANS-AT-C002",
                    "resolution_code": "TRANS-AT-R002",
                    "recommended_action": "Flush transmission; Replace fluid; Replace filter"
                }
            },
            "Torque Converter": {
                "Converter failure": {
                    "failure_code": "TRANS-AT-010",
                    "cause_code": "TRANS-AT-C010",
                    "resolution_code": "TRANS-AT-R010",
                    "recommended_action": "Replace torque converter; Flush system; Check fluid"
                }
            }
        }
    },
    "Brakes": {
        "Hydraulic": {
            "Master Cylinder": {
                "Internal leak": {
                    "failure_code": "BRK-HYD-001",
                    "cause_code": "BRK-HYD-C001",
                    "resolution_code": "BRK-HYD-R001",
                    "recommended_action": "Replace master cylinder; Bleed brake system"
                },
                "External leak": {
                    "failure_code": "BRK-HYD-002",
                    "cause_code": "BRK-HYD-C002",
                    "resolution_code": "BRK-HYD-R002",
                    "recommended_action": "Replace master cylinder; Check brake lines"
                }
            },
            "Brake Lines": {
                "Line rupture": {
                    "failure_code": "BRK-HYD-010",
                    "cause_code": "BRK-HYD-C010",
                    "resolution_code": "BRK-HYD-R010",
                    "recommended_action": "Replace brake line; Bleed system; Pressure test"
                }
            }
        },
        "Friction": {
            "Brake Pads": {
                "Worn pads": {
                    "failure_code": "BRK-FRIC-001",
                    "cause_code": "BRK-FRIC-C001",
                    "resolution_code": "BRK-FRIC-R001",
                    "recommended_action": "Replace brake pads; Resurface rotors; Lubricate slides"
                },
                "Glazed pads": {
                    "failure_code": "BRK-FRIC-002",
                    "cause_code": "BRK-FRIC-C002",
                    "resolution_code": "BRK-FRIC-R002",
                    "recommended_action": "Replace brake pads; Check rotor condition"
                }
            },
            "Rotors": {
                "Warped rotor": {
                    "failure_code": "BRK-FRIC-010",
                    "cause_code": "BRK-FRIC-C010",
                    "resolution_code": "BRK-FRIC-R010",
                    "recommended_action": "Replace or resurface rotor; Replace pads"
                }
            }
        }
    },
    "Electrical": {
        "Battery": {
            "12V Battery": {
                "Dead battery": {
                    "failure_code": "ELEC-BAT-001",
                    "cause_code": "ELEC-BAT-C001",
                    "resolution_code": "ELEC-BAT-R001",
                    "recommended_action": "Test battery; Replace if failed; Check charging system"
                },
                "Low charge": {
                    "failure_code": "ELEC-BAT-002",
                    "cause_code": "ELEC-BAT-C002",
                    "resolution_code": "ELEC-BAT-R002",
                    "recommended_action": "Charge battery; Test alternator; Check for parasitic draw"
                }
            }
        },
        "Charging": {
            "Alternator": {
                "No charge": {
                    "failure_code": "ELEC-CHG-001",
                    "cause_code": "ELEC-CHG-C001",
                    "resolution_code": "ELEC-CHG-R001",
                    "recommended_action": "Replace alternator; Check belt; Test output"
                },
                "Noisy bearing": {
                    "failure_code": "ELEC-CHG-002",
                    "cause_code": "ELEC-CHG-C002",
                    "resolution_code": "ELEC-CHG-R002",
                    "recommended_action": "Replace alternator; Check belt tension"
                }
            }
        }
    },
    "Suspension": {
        "Front": {
            "Struts": {
                "Leaking strut": {
                    "failure_code": "SUSP-FRT-001",
                    "cause_code": "SUSP-FRT-C001",
                    "resolution_code": "SUSP-FRT-R001",
                    "recommended_action": "Replace strut assembly; Perform alignment"
                },
                "Worn mount": {
                    "failure_code": "SUSP-FRT-002",
                    "cause_code": "SUSP-FRT-C002",
                    "resolution_code": "SUSP-FRT-R002",
                    "recommended_action": "Replace strut mount; Check strut condition"
                }
            },
            "Control Arms": {
                "Worn bushings": {
                    "failure_code": "SUSP-FRT-010",
                    "cause_code": "SUSP-FRT-C010",
                    "resolution_code": "SUSP-FRT-R010",
                    "recommended_action": "Replace control arm bushings; Perform alignment"
                }
            }
        }
    },
    "Tires/Wheels": {
        "Tires": {
            "Tire Condition": {
                "Worn tread": {
                    "failure_code": "TIRE-COND-001",
                    "cause_code": "TIRE-COND-C001",
                    "resolution_code": "TIRE-COND-R001",
                    "recommended_action": "Replace tire; Check alignment; Rotate remaining tires"
                },
                "Puncture": {
                    "failure_code": "TIRE-COND-002",
                    "cause_code": "TIRE-COND-C002",
                    "resolution_code": "TIRE-COND-R002",
                    "recommended_action": "Repair or replace tire; Check for debris"
                }
            }
        }
    }
}

# ============================================================================
# HELPER FUNCTIONS FOR CATALOGUE
# ============================================================================

def get_systems():
    """Get list of all systems"""
    return list(CATALOGUE_HIERARCHY.keys())

def get_subsystems(system):
    """Get subsystems for a given system"""
    if system in CATALOGUE_HIERARCHY:
        return list(CATALOGUE_HIERARCHY[system].keys())
    return []

def get_components(system, subsystem):
    """Get components for a given system and subsystem"""
    if system in CATALOGUE_HIERARCHY:
        if subsystem in CATALOGUE_HIERARCHY[system]:
            return list(CATALOGUE_HIERARCHY[system][subsystem].keys())
    return []

def get_failure_modes(system, subsystem, component):
    """Get failure modes for a given system, subsystem, and component"""
    if system in CATALOGUE_HIERARCHY:
        if subsystem in CATALOGUE_HIERARCHY[system]:
            if component in CATALOGUE_HIERARCHY[system][subsystem]:
                return list(CATALOGUE_HIERARCHY[system][subsystem][component].keys())
    return []

def get_fault_details(system, subsystem, component, failure_mode):
    """Get fault details for a specific failure"""
    try:
        details = CATALOGUE_HIERARCHY[system][subsystem][component][failure_mode]
        return details
    except:
        return None

# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================

def get_db_engine():
    """Create or return existing database engine"""
    if st.session_state.db_engine is None:
        st.session_state.db_engine = create_engine(
            "sqlite:///",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
        init_database()
    return st.session_state.db_engine

def init_database():
    """Initialize database tables"""
    engine = st.session_state.db_engine
    
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS work_orders (
                wo_id TEXT PRIMARY KEY,
                vehicle_id TEXT,
                system TEXT,
                subsystem TEXT,
                component TEXT,
                failure_mode TEXT,
                failure_code TEXT,
                cause_code TEXT,
                resolution_code TEXT,
                recommended_action TEXT,
                failure_date TEXT,
                reported_by TEXT,
                status TEXT,
                priority TEXT,
                labor_hours REAL,
                parts_cost REAL,
                description TEXT,
                resolution_notes TEXT,
                created_at TEXT,
                completed_at TEXT
            )
        """))
    
    st.session_state.app_initialized = True

def load_work_orders():
    """Load all work orders"""
    engine = get_db_engine()
    try:
        df = pd.read_sql("SELECT * FROM work_orders", engine)
        if not df.empty:
            df['labor_hours'] = pd.to_numeric(df['labor_hours'], errors='coerce')
            df['parts_cost'] = pd.to_numeric(df['parts_cost'], errors='coerce')
            df['failure_date'] = pd.to_datetime(df['failure_date'], errors='coerce')
        return df
    except:
        return pd.DataFrame()

def save_work_order(wo_data):
    """Save work order to database"""
    engine = get_db_engine()
    df = pd.DataFrame([wo_data])
    df.to_sql('work_orders', engine, if_exists='append', index=False)
    return True

def generate_demo_data(n_records=100):
    """Generate demonstration data"""
    records = []
    statuses = ["Open", "In Progress", "Completed", "On Hold"]
    priorities = ["Low", "Medium", "High", "Critical"]
    vehicles = [f"VEH-{i:04d}" for i in range(1, 51)]
    techs = [f"tech_{i:03d}" for i in range(1, 11)]
    
    for i in range(n_records):
        # Randomly select from catalogue
        system = random.choice(get_systems())
        subsystems = get_subsystems(system)
        if not subsystems:
            continue
        subsystem = random.choice(subsystems)
        
        components = get_components(system, subsystem)
        if not components:
            continue
        component = random.choice(components)
        
        failure_modes = get_failure_modes(system, subsystem, component)
        if not failure_modes:
            continue
        failure_mode = random.choice(failure_modes)
        
        # Get fault details
        details = get_fault_details(system, subsystem, component, failure_mode)
        
        failure_date = datetime.now() - timedelta(days=random.randint(0, 365))
        status = random.choice(statuses)
        
        record = {
            'wo_id': f"WO-{datetime.now().year}-{i+1:05d}",
            'vehicle_id': random.choice(vehicles),
            'system': system,
            'subsystem': subsystem,
            'component': component,
            'failure_mode': failure_mode,
            'failure_code': details.get('failure_code', '') if details else '',
            'cause_code': details.get('cause_code', '') if details else '',
            'resolution_code': details.get('resolution_code', '') if details else '',
            'recommended_action': details.get('recommended_action', '') if details else '',
            'failure_date': failure_date.strftime('%Y-%m-%d'),
            'reported_by': random.choice(techs),
            'status': status,
            'priority': random.choice(priorities),
            'labor_hours': round(random.uniform(0.5, 24.0), 2),
            'parts_cost': round(random.uniform(50, 5000), 2),
            'description': f"Failure detected in {system} - {subsystem} - {component}",
            'resolution_notes': "Completed as per recommended action" if status == "Completed" else "",
            'created_at': failure_date.strftime('%Y-%m-%d %H:%M:%S'),
            'completed_at': (failure_date + timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d') if status == "Completed" else None
        }
        records.append(record)
    
    # Save to database
    engine = get_db_engine()
    df = pd.DataFrame(records)
    df.to_sql('work_orders', engine, if_exists='replace', index=False)
    
    return len(records)

# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_sidebar():
    """Render sidebar navigation"""
    with st.sidebar:
        st.title("🚗 AMIC FRACAS")
        st.caption("Enhanced Demo Version")
        st.markdown("---")
        
        menu = st.radio(
            "Navigation",
            ["📊 Dashboard", "📋 Work Orders", "➕ New Work Order", "📈 Analytics", "⚙️ Data Management"],
            index=0
        )
        
        st.markdown("---")
        
        # Quick stats
        df = load_work_orders()
        if not df.empty:
            st.caption("**Quick Stats**")
            st.caption(f"Total WOs: {len(df)}")
            st.caption(f"Open: {len(df[df['status']=='Open'])}")
            st.caption(f"Completed: {len(df[df['status']=='Completed'])}")
        
        st.markdown("---")
        st.caption(f"👤 {st.session_state.current_user}")
        st.caption(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        return menu.split(" ", 1)[1]  # Remove emoji

def render_dashboard():
    """Render main dashboard"""
    st.title("📊 FRACAS Dashboard")
    
    df = load_work_orders()
    
    if df.empty:
        st.warning("⚠️ No work orders found in database")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Generate 100 Demo Records", use_container_width=True):
                n = generate_demo_data(100)
                st.success(f"✓ Generated {n} work orders!")
                st.rerun()
        with col2:
            if st.button("Generate 500 Demo Records", use_container_width=True):
                n = generate_demo_data(500)
                st.success(f"✓ Generated {n} work orders!")
                st.rerun()
        return
    
    # KPI Metrics Row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Work Orders", f"{len(df):,}")
    with col2:
        open_count = len(df[df['status'].isin(['Open', 'In Progress'])])
        st.metric("Open/In Progress", open_count)
    with col3:
        completed = len(df[df['status'] == 'Completed'])
        completion_rate = (completed / len(df) * 100) if len(df) > 0 else 0
        st.metric("Completed", f"{completed} ({completion_rate:.0f}%)")
    with col4:
        total_cost = df['parts_cost'].sum()
        st.metric("Parts Cost", f"${total_cost:,.0f}")
    with col5:
        labor_cost = df['labor_hours'].sum() * 85
        st.metric("Labor Cost", f"${labor_cost:,.0f}")
    
    st.markdown("---")
    
    # Charts Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Work Orders by System")
        system_counts = df['system'].value_counts().reset_index()
        system_counts.columns = ['System', 'Count']
        
        chart = alt.Chart(system_counts).mark_bar().encode(
            x=alt.X('Count:Q', title='Number of Work Orders'),
            y=alt.Y('System:N', sort='-x', title='System'),
            color=alt.Color('System:N', legend=None),
            tooltip=['System', 'Count']
        ).properties(height=400)
        
        st.altair_chart(chart, use_container_width=True)
    
    with col2:
        st.subheader("Work Orders by Status")
        status_counts = df['status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        
        chart = alt.Chart(status_counts).mark_arc(innerRadius=50).encode(
            theta=alt.Theta('Count:Q'),
            color=alt.Color('Status:N', scale=alt.Scale(scheme='category10')),
            tooltip=['Status', 'Count']
        ).properties(height=400)
        
        st.altair_chart(chart, use_container_width=True)
    
    # Charts Row 2
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Work Orders by Priority")
        priority_counts = df['priority'].value_counts().reset_index()
        priority_counts.columns = ['Priority', 'Count']
        
        # Define priority order and colors
        priority_order = ['Critical', 'High', 'Medium', 'Low']
        colors = {'Critical': '#DC2626', 'High': '#F59E0B', 'Medium': '#3B82F6', 'Low': '#10B981'}
        
        chart = alt.Chart(priority_counts).mark_bar().encode(
            x=alt.X('Count:Q'),
            y=alt.Y('Priority:N', sort=priority_order),
            color=alt.Color('Priority:N', scale=alt.Scale(domain=list(colors.keys()), range=list(colors.values())), legend=None),
            tooltip=['Priority', 'Count']
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)
    
    with col2:
        st.subheader("Cost Analysis")
        cost_data = pd.DataFrame({
            'Category': ['Parts', 'Labor'],
            'Cost': [df['parts_cost'].sum(), df['labor_hours'].sum() * 85]
        })
        
        chart = alt.Chart(cost_data).mark_arc(innerRadius=50).encode(
            theta=alt.Theta('Cost:Q'),
            color=alt.Color('Category:N', scale=alt.Scale(scheme='tableau10')),
            tooltip=[alt.Tooltip('Category:N'), alt.Tooltip('Cost:Q', format='$,.0f')]
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)
    
    # Recent Work Orders Table
    st.markdown("---")
    st.subheader("Recent Work Orders")
    
    recent = df.sort_values('created_at', ascending=False).head(15)
    display_cols = ['wo_id', 'vehicle_id', 'system', 'subsystem', 'failure_mode', 'status', 'priority', 'failure_code', 'created_at']
    
    st.dataframe(
        recent[display_cols],
        use_container_width=True,
        hide_index=True,
        column_config={
            'wo_id': 'Work Order ID',
            'vehicle_id': 'Vehicle',
            'system': 'System',
            'subsystem': 'Subsystem',
            'failure_mode': 'Failure Mode',
            'status': 'Status',
            'priority': 'Priority',
            'failure_code': 'Fault Code',
            'created_at': 'Created'
        }
    )

def render_work_orders():
    """Render work orders list with filtering"""
    st.title("📋 Work Orders")
    
    df = load_work_orders()
    
    if df.empty:
        st.info("No work orders found. Generate demo data to get started.")
        return
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        systems = ['All'] + sorted(df['system'].unique().tolist())
        selected_system = st.selectbox("System", systems)
    
    with col2:
        statuses = ['All'] + sorted(df['status'].unique().tolist())
        selected_status = st.selectbox("Status", statuses)
    
    with col3:
        priorities = ['All'] + sorted(df['priority'].unique().tolist())
        selected_priority = st.selectbox("Priority", priorities)
    
    with col4:
        vehicles = ['All'] + sorted(df['vehicle_id'].unique().tolist())
        selected_vehicle = st.selectbox("Vehicle", vehicles)
    
    # Apply filters
    filtered_df = df.copy()
    if selected_system != 'All':
        filtered_df = filtered_df[filtered_df['system'] == selected_system]
    if selected_status != 'All':
        filtered_df = filtered_df[filtered_df['status'] == selected_status]
    if selected_priority != 'All':
        filtered_df = filtered_df[filtered_df['priority'] == selected_priority]
    if selected_vehicle != 'All':
        filtered_df = filtered_df[filtered_df['vehicle_id'] == selected_vehicle]
    
    st.info(f"Showing {len(filtered_df):,} of {len(df):,} work orders")
    
    # Display work orders
    display_cols = ['wo_id', 'vehicle_id', 'system', 'subsystem', 'component', 'failure_mode', 
                    'failure_code', 'status', 'priority', 'labor_hours', 'parts_cost', 'created_at']
    
    st.dataframe(
        filtered_df[display_cols].sort_values('created_at', ascending=False),
        use_container_width=True,
        hide_index=True,
        column_config={
            'labor_hours': st.column_config.NumberColumn('Labor (hrs)', format="%.1f"),
            'parts_cost': st.column_config.NumberColumn('Parts ($)', format="$%.0f")
        }
    )

def render_new_work_order():
    """Render new work order creation form"""
    st.title("➕ Create New Work Order")
    
    st.info("💡 Use the cascading dropdowns to select the failure. Fault codes and recommended actions will be auto-populated.")
    
    with st.form("new_wo_form", clear_on_submit=True):
        # Basic Info
        st.subheader("Basic Information")
        col1, col2 = st.columns(2)
        
        with col1:
            vehicle_id = st.text_input("Vehicle ID *", placeholder="VEH-0001")
            failure_date = st.date_input("Failure Date *", datetime.now())
        
        with col2:
            priority = st.selectbox("Priority *", ["Low", "Medium", "High", "Critical"], index=2)
            status = st.selectbox("Status *", ["Open", "In Progress"], index=0)
        
        # Cascading Dropdowns
        st.subheader("Fault Classification")
        st.caption("Select System → Subsystem → Component → Failure Mode")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            systems = get_systems()
            selected_system = st.selectbox("System *", systems, key="system_select")
        
        with col2:
            subsystems = get_subsystems(selected_system) if selected_system else []
            selected_subsystem = st.selectbox("Subsystem *", subsystems if subsystems else ["Select System first"], 
                                             disabled=not subsystems, key="subsystem_select")
        
        with col3:
            components = get_components(selected_system, selected_subsystem) if selected_system and selected_subsystem else []
            selected_component = st.selectbox("Component *", components if components else ["Select Subsystem first"],
                                             disabled=not components, key="component_select")
        
        with col4:
            failure_modes = get_failure_modes(selected_system, selected_subsystem, selected_component) if selected_component else []
            selected_failure = st.selectbox("Failure Mode *", failure_modes if failure_modes else ["Select Component first"],
                                           disabled=not failure_modes, key="failure_select")
        
        # Get fault details
        fault_details = None
        if selected_system and selected_subsystem and selected_component and selected_failure:
            fault_details = get_fault_details(selected_system, selected_subsystem, selected_component, selected_failure)
        
        # Auto-populated fields
        if fault_details:
            st.subheader("Auto-Generated Codes")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.text_input("Failure Code", value=fault_details.get('failure_code', ''), disabled=True)
            with col2:
                st.text_input("Cause Code", value=fault_details.get('cause_code', ''), disabled=True)
            with col3:
                st.text_input("Resolution Code", value=fault_details.get('resolution_code', ''), disabled=True)
            
            st.text_area("Recommended Action", value=fault_details.get('recommended_action', ''), 
                        height=100, disabled=True)
        
        # Additional Details
        st.subheader("Additional Details")
        description = st.text_area("Description", placeholder="Describe the failure in detail...")
        
        col1, col2 = st.columns(2)
        with col1:
            labor_hours = st.number_input("Estimated Labor Hours", min_value=0.0, step=0.5, value=2.0)
        with col2:
            parts_cost = st.number_input("Estimated Parts Cost ($)", min_value=0.0, step=50.0, value=500.0)
        
        # Submit
        submitted = st.form_submit_button("🚀 Create Work Order", use_container_width=True, type="primary")
        
        if submitted:
            # Validation
            if not vehicle_id:
                st.error("❌ Vehicle ID is required")
            elif not selected_system or not selected_subsystem or not selected_component or not selected_failure:
                st.error("❌ Please complete all fault classification fields")
            elif not fault_details:
                st.error("❌ Invalid fault classification selection")
            else:
                # Generate WO ID
                wo_id = f"WO-{datetime.now().year}-{random.randint(10000, 99999)}"
                
                # Create work order data
                wo_data = {
                    'wo_id': wo_id,
                    'vehicle_id': vehicle_id,
                    'system': selected_system,
                    'subsystem': selected_subsystem,
                    'component': selected_component,
                    'failure_mode': selected_failure,
                    'failure_code': fault_details.get('failure_code', ''),
                    'cause_code': fault_details.get('cause_code', ''),
                    'resolution_code': fault_details.get('resolution_code', ''),
                    'recommended_action': fault_details.get('recommended_action', ''),
                    'failure_date': failure_date.strftime('%Y-%m-%d'),
                    'reported_by': st.session_state.current_user,
                    'status': status,
                    'priority': priority,
                    'labor_hours': labor_hours,
                    'parts_cost': parts_cost,
                    'description': description,
                    'resolution_notes': '',
                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'completed_at': None
                }
                
                # Save to database
                if save_work_order(wo_data):
                    st.success(f"✅ Work Order {wo_id} created successfully!")
                    st.balloons()
                    
                    # Show summary
                    with st.expander("📋 Work Order Summary", expanded=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Work Order ID:** {wo_id}")
                            st.write(f"**Vehicle:** {vehicle_id}")
                            st.write(f"**System:** {selected_system}")
                            st.write(f"**Subsystem:** {selected_subsystem}")
                            st.write(f"**Component:** {selected_component}")
                        with col2:
                            st.write(f"**Failure Mode:** {selected_failure}")
                            st.write(f"**Failure Code:** {fault_details.get('failure_code', '')}")
                            st.write(f"**Priority:** {priority}")
                            st.write(f"**Status:** {status}")
                            st.write(f"**Est. Labor:** {labor_hours} hrs")
                            st.write(f"**Est. Parts:** ${parts_cost:,.2f}")
                else:
                    st.error("❌ Failed to create work order")

def render_analytics():
    """Render advanced analytics"""
    st.title("📈 Analytics & Insights")
    
    df = load_work_orders()
    
    if df.empty:
        st.info("No data available for analytics. Generate demo data first.")
        return
    
    # Tabs for different analytics
    tab1, tab2, tab3, tab4 = st.tabs(["System Analysis", "Cost Analysis", "Performance Metrics", "Trends"])
    
    with tab1:
        st.subheader("System Reliability Analysis")
        
        system_stats = df.groupby('system').agg({
            'wo_id': 'count',
            'labor_hours': 'sum',
            'parts_cost': 'sum'
        }).reset_index()
        system_stats.columns = ['System', 'Failure Count', 'Total Labor Hours', 'Total Parts Cost']
        system_stats['Total Cost'] = system_stats['Total Labor Hours'] * 85 + system_stats['Total Parts Cost']
        system_stats = system_stats.sort_values('Failure Count', ascending=False)
        
        st.dataframe(
            system_stats,
            use_container_width=True,
            hide_index=True,
            column_config={
                'Total Labor Hours': st.column_config.NumberColumn(format="%.1f hrs"),
                'Total Parts Cost': st.column_config.NumberColumn(format="$%.0f"),
                'Total Cost': st.column_config.NumberColumn(format="$%.0f")
            }
        )
        
        # Chart
        chart = alt.Chart(system_stats.head(10)).mark_bar().encode(
            x=alt.X('Failure Count:Q'),
            y=alt.Y('System:N', sort='-x'),
            color=alt.value('#3B82F6'),
            tooltip=['System', 'Failure Count', alt.Tooltip('Total Cost:Q', format='$,.0f')]
        ).properties(height=400)
        
        st.altair_chart(chart, use_container_width=True)
    
    with tab2:
        st.subheader("Cost Breakdown")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_parts = df['parts_cost'].sum()
        total_labor = df['labor_hours'].sum() * 85
        total_cost = total_parts + total_labor
        avg_cost_per_wo = total_cost / len(df) if len(df) > 0 else 0
        
        with col1:
            st.metric("Total Parts Cost", f"${total_parts:,.0f}")
        with col2:
            st.metric("Total Labor Cost", f"${total_labor:,.0f}")
        with col3:
            st.metric("Total Cost", f"${total_cost:,.0f}")
        with col4:
            st.metric("Avg Cost/WO", f"${avg_cost_per_wo:,.0f}")
        
        # Cost by system
        st.markdown("---")
        st.subheader("Cost by System")
        
        cost_by_system = df.groupby('system').agg({
            'parts_cost': 'sum',
            'labor_hours': 'sum'
        }).reset_index()
        cost_by_system['labor_cost'] = cost_by_system['labor_hours'] * 85
        cost_by_system['total_cost'] = cost_by_system['parts_cost'] + cost_by_system['labor_cost']
        cost_by_system = cost_by_system.sort_values('total_cost', ascending=False).head(10)
        
        chart = alt.Chart(cost_by_system).mark_bar().encode(
            x=alt.X('total_cost:Q', title='Total Cost ($)'),
            y=alt.Y('system:N', sort='-x', title='System'),
            color=alt.value('#10B981'),
            tooltip=[
                'system',
                alt.Tooltip('total_cost:Q', format='$,.0f', title='Total Cost'),
                alt.Tooltip('parts_cost:Q', format='$,.0f', title='Parts'),
                alt.Tooltip('labor_cost:Q', format='$,.0f', title='Labor')
            ]
        ).properties(height=400)
        
        st.altair_chart(chart, use_container_width=True)
    
    with tab3:
        st.subheader("Performance Metrics")
        
        # MTTR calculation
        completed_df = df[df['status'] == 'Completed'].copy()
        if not completed_df.empty and 'completed_at' in completed_df.columns:
            completed_df['failure_date'] = pd.to_datetime(completed_df['failure_date'])
            completed_df['completed_at'] = pd.to_datetime(completed_df['completed_at'])
            completed_df['repair_time'] = (completed_df['completed_at'] - completed_df['failure_date']).dt.days
            
            avg_mttr = completed_df['repair_time'].mean()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Avg MTTR (Days)", f"{avg_mttr:.1f}")
            with col2:
                completion_rate = (len(completed_df) / len(df) * 100) if len(df) > 0 else 0
                st.metric("Completion Rate", f"{completion_rate:.1f}%")
            with col3:
                open_wos = len(df[df['status'].isin(['Open', 'In Progress'])])
                st.metric("Open Work Orders", open_wos)
        
        # Top failure modes
        st.markdown("---")
        st.subheader("Top 10 Failure Modes")
        
        failure_counts = df['failure_mode'].value_counts().head(10).reset_index()
        failure_counts.columns = ['Failure Mode', 'Count']
        
        chart = alt.Chart(failure_counts).mark_bar().encode(
            x=alt.X('Count:Q'),
            y=alt.Y('Failure Mode:N', sort='-x'),
            color=alt.value('#F59E0B'),
            tooltip=['Failure Mode', 'Count']
        ).properties(height=400)
        
        st.altair_chart(chart, use_container_width=True)
    
    with tab4:
        st.subheader("Trends Over Time")
        st.info("📊 Time-based trend analysis requires date filtering - coming in full version")
        
        # Monthly trend
        df_trend = df.copy()
        df_trend['failure_date'] = pd.to_datetime(df_trend['failure_date'])
        df_trend['month'] = df_trend['failure_date'].dt.to_period('M').astype(str)
        
        monthly = df_trend.groupby('month').size().reset_index(name='count')
        
        if len(monthly) > 1:
            chart = alt.Chart(monthly).mark_line(point=True).encode(
                x=alt.X('month:N', title='Month'),
                y=alt.Y('count:Q', title='Work Orders'),
                tooltip=['month', 'count']
            ).properties(height=300)
            
            st.altair_chart(chart, use_container_width=True)

def render_data_management():
    """Render data management tools"""
    st.title("⚙️ Data Management")
    
    tab1, tab2, tab3 = st.tabs(["Export Data", "Generate Demo Data", "Database Info"])
    
    with tab1:
        st.subheader("Export Data")
        df = load_work_orders()
        
        if not df.empty:
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Work Orders (CSV)",
                data=csv,
                file_name=f"work_orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            st.info(f"Ready to export {len(df)} work orders")
        else:
            st.warning("No data to export")
    
    with tab2:
        st.subheader("Generate Demo Data")
        st.write("Generate realistic demo work orders for testing and demonstration.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            n_records = st.number_input("Number of Records", min_value=10, max_value=5000, value=100, step=10)
        
        with col2:
            st.write("")  # Spacing
            st.write("")  # Spacing
            if st.button("🎲 Generate Demo Data", use_container_width=True, type="primary"):
                with st.spinner(f"Generating {n_records} work orders..."):
                    n = generate_demo_data(n_records)
                    st.success(f"✅ Successfully generated {n} work orders!")
                    st.balloons()
        
        st.info("💡 Demo data includes realistic vehicle IDs, failure modes from the catalogue, and varied statuses/priorities.")
    
    with tab3:
        st.subheader("Database Information")
        df = load_work_orders()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Records", f"{len(df):,}")
        
        with col2:
            if not df.empty:
                size_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
                st.metric("Data Size", f"{size_mb:.2f} MB")
        
        with col3:
            systems_count = len(df['system'].unique()) if not df.empty else 0
            st.metric("Systems Tracked", systems_count)
        
        if not df.empty:
            st.markdown("---")
            st.subheader("Data Quality Metrics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                complete = df[['failure_code', 'cause_code', 'resolution_code']].notna().all(axis=1).sum()
                completeness = (complete / len(df) * 100) if len(df) > 0 else 0
                st.metric("Data Completeness", f"{completeness:.1f}%")
            
            with col2:
                has_action = df['recommended_action'].notna().sum()
                action_rate = (has_action / len(df) * 100) if len(df) > 0 else 0
                st.metric("Has Rec. Action", f"{action_rate:.1f}%")
            
            with col3:
                vehicles = df['vehicle_id'].nunique()
                st.metric("Unique Vehicles", vehicles)
            
            with col4:
                techs = df['reported_by'].nunique()
                st.metric("Technicians", techs)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point"""
    
    # Initialize database
    if not st.session_state.app_initialized:
        get_db_engine()
    
    # Render sidebar and get menu selection
    menu = render_sidebar()
    
    # Route to appropriate page
    if menu == "Dashboard":
        render_dashboard()
    elif menu == "Work Orders":
        render_work_orders()
    elif menu == "New Work Order":
        render_new_work_order()
    elif menu == "Analytics":
        render_analytics()
    elif menu == "Data Management":
        render_data_management()

if __name__ == "__main__":
    main()
