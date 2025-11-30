"""
AMIC Maintenance Management System (MMS) - Phase 1 Work Order Module
Complete Demo Application with Full ERD Implementation
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import hashlib

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="AMIC MMS - Work Order Management",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# STYLING - WHITE THEME
# ============================================================================
st.markdown("""
<style>
/* Main background - WHITE */
[data-testid="stAppViewContainer"] {
    background-color: #FFFFFF !important;
    color: #111827 !important;
}

[data-testid="stMain"] {
    background-color: #FFFFFF !important;
}

/* Sidebar - Light Gray */
[data-testid="stSidebar"] {
    background-color: #F9FAFB !important;
    color: #111827 !important;
}

/* Text and headers */
h1, h2, h3, h4, h5, h6, p, span, div, label {
    color: #111827 !important;
}

/* Input fields - WHITE background with dark text */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stNumberInput > div > div > input,
.stDateInput > div > div > input,
.stTextArea > div > div > textarea {
    background-color: #FFFFFF !important;
    color: #111827 !important;
    border: 1px solid #D1D5DB !important;
}

/* Buttons */
.stButton > button {
    background-color: #3B82F6 !important;
    color: white !important;
    border-radius: 6px;
    font-weight: 500;
    border: none;
}

.stButton > button:hover {
    background-color: #2563EB !important;
}

/* Metrics */
.stMetric {
    background-color: #F9FAFB !important;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 1.5rem;
}

/* Dataframe/tables */
[data-testid="stDataFrame"] {
    background-color: #FFFFFF !important;
}

/* Info boxes */
.stInfo {
    background-color: #DBEAFE !important;
    color: #1E40AF !important;
    border: 1px solid #BFDBFE !important;
}

.stSuccess {
    background-color: #D1FAE5 !important;
    color: #065F46 !important;
}

.stWarning {
    background-color: #FEF3C7 !important;
    color: #78350F !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA INITIALIZATION
# ============================================================================

def hash_password(password):
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_data():
    """Initialize all data tables in session state"""
    
    if 'data_initialized' in st.session_state and st.session_state.data_initialized:
        return
    
    # ========================================================================
    # REFERENCE TABLES
    # ========================================================================
    
    # Department
    st.session_state.df_department = pd.DataFrame({
        'Department_Code': ['TECH', 'INV', 'PROC', 'OPS', 'ADMIN'],
        'Department_Name': ['Technical Services', 'Inventory Management', 'Procurement', 'Operations', 'Administration'],
        'Department_Supervisor': ['Ahmed Al-Rashid', 'Fatima Al-Qasim', 'Mohammed Al-Harbi', 'Khalid Al-Mansour', 'Sara Al-Fahad']
    })
    
    # Region
    st.session_state.df_region = pd.DataFrame({
        'Region_ID': [1, 2, 3, 4, 5],
        'Region_Name': ['Central', 'Eastern', 'Western', 'Northern', 'Southern']
    })
    
    # Workshop
    st.session_state.df_workshop = pd.DataFrame({
        'Workshop_Name': ['Workshop Alpha', 'Workshop Beta', 'Workshop Gamma', 'Workshop Delta', 'Workshop Epsilon'],
        'Region': ['Central', 'Eastern', 'Western', 'Northern', 'Southern'],
        'Unit_Name': ['Unit 101', 'Unit 102', 'Unit 103', 'Unit 104', 'Unit 105']
    })
    
    # Unit
    st.session_state.df_unit = pd.DataFrame({
        'Unit_Name': ['Unit 101', 'Unit 102', 'Unit 103', 'Unit 104', 'Unit 105'],
        'Workshop_Name': ['Workshop Alpha', 'Workshop Beta', 'Workshop Gamma', 'Workshop Delta', 'Workshop Epsilon'],
        'Region': ['Central', 'Eastern', 'Western', 'Northern', 'Southern']
    })
    
    # Battalion
    st.session_state.df_battalion = pd.DataFrame({
        'Battalion_Name': ['Battalion 1A', 'Battalion 1B', 'Battalion 2A', 'Battalion 2B', 'Battalion 3A'],
        'Unit_Name': ['Unit 101', 'Unit 101', 'Unit 102', 'Unit 102', 'Unit 103'],
        'Vehicle_Number': ['VEH-001', 'VEH-002', 'VEH-003', 'VEH-004', 'VEH-005']
    })
    
    # ========================================================================
    # USERS
    # ========================================================================
    
    st.session_state.df_user = pd.DataFrame({
        'Employee_ID': [1, 2, 3, 4, 5, 6, 7, 8],
        'Department_Code': ['TECH', 'TECH', 'TECH', 'INV', 'PROC', 'OPS', 'OPS', 'ADMIN'],
        'Employee_First_Name': ['Ali', 'Omar', 'Yousef', 'Layla', 'Hassan', 'Nora', 'Tariq', 'Admin'],
        'Employee_Last_Name': ['Al-Saud', 'Al-Harbi', 'Al-Qahtani', 'Al-Otaibi', 'Al-Shammari', 'Al-Dosari', 'Al-Mutairi', 'User'],
        'Job_Title': ['Technician', 'Supervisor', 'Technician', 'Inventory Specialist', 'Procurement Officer', 'Manager', 'Supervisor', 'System Admin'],
        'Resource_ID': ['RES001', 'RES002', 'RES003', 'RES004', 'RES005', 'RES006', 'RES007', 'RES008'],
        'Username': ['ali.tech', 'omar.super', 'yousef.tech', 'layla.inv', 'hassan.proc', 'nora.mgr', 'tariq.super', 'admin'],
        'Password': [hash_password('tech123'), hash_password('super123'), hash_password('tech123'), 
                    hash_password('inv123'), hash_password('proc123'), hash_password('mgr123'), 
                    hash_password('super123'), hash_password('admin123')],
        'Role': ['Technician', 'Supervisor', 'Technician', 'Inventory', 'Procurement', 'Manager', 'Supervisor', 'Admin'],
        'Workshop_Name': ['Workshop Alpha', 'Workshop Alpha', 'Workshop Beta', None, None, None, 'Workshop Beta', None],
        'Region': ['Central', 'Central', 'Eastern', None, None, None, 'Eastern', None]
    })
    
    # ========================================================================
    # VEHICLES
    # ========================================================================
    
    st.session_state.df_vehicle = pd.DataFrame({
        'Vehicle_Number': ['VEH-001', 'VEH-002', 'VEH-003', 'VEH-004', 'VEH-005', 
                          'VEH-006', 'VEH-007', 'VEH-008', 'VEH-009', 'VEH-010'],
        'Unit_Name': ['Unit 101', 'Unit 101', 'Unit 102', 'Unit 102', 'Unit 103', 
                     'Unit 103', 'Unit 104', 'Unit 104', 'Unit 105', 'Unit 105'],
        'Battalion_Name': ['Battalion 1A', 'Battalion 1B', 'Battalion 2A', 'Battalion 2B', 'Battalion 3A',
                          'Battalion 1A', 'Battalion 2A', 'Battalion 2B', 'Battalion 3A', 'Battalion 1B'],
        'Vehicle_Type': ['MRAP', 'APC', 'Transport', 'MRAP', 'APC', 
                        'Transport', 'MRAP', 'APC', 'Transport', 'MRAP'],
        'Vehicle_Brand': ['Oshkosh', 'BAE Systems', 'Mercedes', 'Oshkosh', 'BAE Systems',
                         'Mercedes', 'Oshkosh', 'BAE Systems', 'Mercedes', 'Oshkosh'],
        'Vehicle_Chassis_Number': [f'CHAS{i:06d}' for i in range(1, 11)]
    })
    
    # ========================================================================
    # FAILURE CATALOGUE
    # ========================================================================
    
    st.session_state.df_failure_catalogue = pd.DataFrame({
        'System': [
            'HVAC', 'HVAC', 'HVAC', 'HVAC', 'HVAC',
            'Engine', 'Engine', 'Engine', 'Engine', 'Engine',
            'Brakes', 'Brakes', 'Brakes', 'Brakes',
            'Suspension', 'Suspension', 'Suspension',
            'Electrical', 'Electrical', 'Electrical'
        ],
        'Subsystem': [
            'Air Conditioning', 'Air Conditioning', 'Air Conditioning', 'Heating', 'Heating',
            'Fuel System', 'Fuel System', 'Ignition', 'Ignition', 'Cooling',
            'Hydraulic', 'Hydraulic', 'Friction', 'Friction',
            'Front', 'Front', 'Rear',
            'Battery', 'Charging', 'Charging'
        ],
        'Component': [
            'Compressor', 'Condenser', 'Blower Motor', 'Heater Core', 'Heater Core',
            'Fuel Pump', 'Fuel Injectors', 'Spark Plugs', 'Ignition Coils', 'Radiator',
            'Master Cylinder', 'Brake Lines', 'Brake Pads', 'Rotors',
            'Struts', 'Control Arms', 'Shock Absorbers',
            '12V Battery', 'Alternator', 'Alternator'
        ],
        'Failure_Mode': [
            'Mechanical seizure', 'Leak at tubes', 'Motor burnt', 'Core leak', 'Blockage',
            'Pump failure', 'Injector clogged', 'Fouled plugs', 'Coil failure', 'Radiator leak',
            'Internal leak', 'Line rupture', 'Worn pads', 'Warped rotor',
            'Leaking strut', 'Worn bushings', 'Shock failure',
            'Dead battery', 'No charge', 'Noisy bearing'
        ],
        'Failure_Code': [
            'HVAC-AC-001', 'HVAC-AC-010', 'HVAC-AC-020', 'HVAC-HT-001', 'HVAC-HT-002',
            'ENG-FUEL-001', 'ENG-FUEL-010', 'ENG-IGN-001', 'ENG-IGN-010', 'ENG-COOL-001',
            'BRK-HYD-001', 'BRK-HYD-010', 'BRK-FRIC-001', 'BRK-FRIC-010',
            'SUSP-FRT-001', 'SUSP-FRT-010', 'SUSP-REAR-001',
            'ELEC-BAT-001', 'ELEC-CHG-001', 'ELEC-CHG-002'
        ],
        'Cause_Code': [
            'HVAC-AC-C001', 'HVAC-AC-C010', 'HVAC-AC-C020', 'HVAC-HT-C001', 'HVAC-HT-C002',
            'ENG-FUEL-C001', 'ENG-FUEL-C010', 'ENG-IGN-C001', 'ENG-IGN-C010', 'ENG-COOL-C001',
            'BRK-HYD-C001', 'BRK-HYD-C010', 'BRK-FRIC-C001', 'BRK-FRIC-C010',
            'SUSP-FRT-C001', 'SUSP-FRT-C010', 'SUSP-REAR-C001',
            'ELEC-BAT-C001', 'ELEC-CHG-C001', 'ELEC-CHG-C002'
        ],
        'Resolution_Code': [
            'HVAC-AC-R001', 'HVAC-AC-R010', 'HVAC-AC-R020', 'HVAC-HT-R001', 'HVAC-HT-R002',
            'ENG-FUEL-R001', 'ENG-FUEL-R010', 'ENG-IGN-R001', 'ENG-IGN-R010', 'ENG-COOL-R001',
            'BRK-HYD-R001', 'BRK-HYD-R010', 'BRK-FRIC-R001', 'BRK-FRIC-R010',
            'SUSP-FRT-R001', 'SUSP-FRT-R010', 'SUSP-REAR-R001',
            'ELEC-BAT-R001', 'ELEC-CHG-R001', 'ELEC-CHG-R002'
        ],
        'Recommended_Action': [
            'Replace compressor; Replace clutch; Flush circuit; Replace filter/drier; Vacuum & recharge',
            'Replace condenser; Clean fins; Leak test; Vacuum & recharge',
            'Replace blower motor; Inspect resistor; Verify airflow',
            'Replace heater core; Flush circuit; Bleed system',
            'Flush heater core; Check coolant flow; Replace if needed',
            'Replace fuel pump; Check electrical; Verify fuel quality',
            'Clean injectors; Replace if needed; Check fuel quality',
            'Replace spark plugs; Check gap; Verify ignition timing',
            'Replace ignition coil; Check connections; Test resistance',
            'Replace radiator; Pressure test; Check coolant level',
            'Replace master cylinder; Bleed brake system',
            'Replace brake line; Bleed system; Pressure test',
            'Replace brake pads; Resurface rotors; Lubricate slides',
            'Replace or resurface rotor; Replace pads',
            'Replace strut assembly; Perform alignment',
            'Replace control arm bushings; Perform alignment',
            'Replace shock absorbers; Check mounting points',
            'Test battery; Replace if failed; Check charging system',
            'Replace alternator; Check belt; Test output',
            'Replace alternator; Check belt tension'
        ]
    })
    
    # ========================================================================
    # WORK ORDERS & MALFUNCTIONS
    # ========================================================================
    
    # Generate sample work orders
    work_orders = []
    malfunctions = []
    wo_id_counter = 1
    mal_id_counter = 1
    
    for i in range(20):
        # Random selections
        vehicle = st.session_state.df_vehicle.sample(1).iloc[0]
        workshop = st.session_state.df_workshop.sample(1).iloc[0]
        failure = st.session_state.df_failure_catalogue.sample(1).iloc[0]
        technician = st.session_state.df_user[st.session_state.df_user['Role'] == 'Technician'].sample(1).iloc[0]
        
        malfunction_date = datetime.now() - timedelta(days=np.random.randint(1, 180))
        wo_date = malfunction_date + timedelta(days=np.random.randint(0, 3))
        
        status = np.random.choice(['Open', 'In Progress', 'Completed'], p=[0.3, 0.4, 0.3])
        require_parts = np.random.choice([True, False], p=[0.6, 0.4])
        
        completion_date = None
        if status == 'Completed':
            completion_date = wo_date + timedelta(days=np.random.randint(1, 30))
        
        work_order = {
            'Work_Order_ID': wo_id_counter,
            'Employee_ID': technician['Employee_ID'],
            'Workshop_Name': workshop['Workshop_Name'],
            'Vehicle_Number': vehicle['Vehicle_Number'],
            'A_Received_Date': wo_date.strftime('%Y-%m-%d'),
            'Equipment_Owning_Unit': vehicle['Unit_Name'],
            'Vehicle_Type': vehicle['Vehicle_Type'],
            'Malfunction_Date': malfunction_date.strftime('%Y-%m-%d'),
            'Work_Order_Date': wo_date.strftime('%Y-%m-%d'),
            'Technician_Name': f"{technician['Employee_First_Name']} {technician['Employee_Last_Name']}",
            'Work_Order_Status': status,
            'Require_Spare_Parts': require_parts,
            'Work_Order_Completion_Date': completion_date.strftime('%Y-%m-%d') if completion_date else None,
            'Comments': f"Work order for {failure['System']} - {failure['Subsystem']} issue"
        }
        
        malfunction = {
            'Malfunction_ID': mal_id_counter,
            'Vehicle_Number': vehicle['Vehicle_Number'],
            'Work_Order_ID': wo_id_counter,
            'Malfunction_Code': failure['Failure_Code'],
            'Resolution_Description_English': failure['Recommended_Action'],
            'Resolution_Description_Arabic': 'إجراء موصى به',
            'Root_Cause': failure['Failure_Mode'],
            'Cause_Code': failure['Cause_Code'],
            'Cause_Description_English': failure['Failure_Mode'],
            'Cause_Description_Arabic': 'وصف السبب',
            'Fault_Code': failure['Failure_Code']
        }
        
        work_orders.append(work_order)
        malfunctions.append(malfunction)
        wo_id_counter += 1
        mal_id_counter += 1
    
    st.session_state.df_work_orders = pd.DataFrame(work_orders)
    st.session_state.df_malfunction = pd.DataFrame(malfunctions)
    
    # ========================================================================
    # WAREHOUSE & PARTS
    # ========================================================================
    
    st.session_state.df_warehouse = pd.DataFrame({
        'Warehouse_ID': [1, 2, 3, 4, 5],
        'Warehouse_Name': ['Central Warehouse', 'Eastern Warehouse', 'Western Warehouse', 'Northern Warehouse', 'Southern Warehouse'],
        'Region': ['Central', 'Eastern', 'Western', 'Northern', 'Southern'],
        'Unit': ['Unit 101', 'Unit 102', 'Unit 103', 'Unit 104', 'Unit 105']
    })
    
    st.session_state.df_part = pd.DataFrame({
        'Part_ID': range(1, 21),
        'Warehouse_Code': ['WH-C', 'WH-E', 'WH-W', 'WH-N', 'WH-S'] * 4,
        'Part_Number': [f'PN-{i:05d}' for i in range(1, 21)],
        'OEM_Number': [f'OEM-{i:05d}' for i in range(1, 21)],
        'English_Description': ['Compressor Assembly', 'Fuel Pump Kit', 'Brake Pad Set', 'Alternator', 'Strut Assembly',
                               'Ignition Coil', 'Radiator', 'Battery 12V', 'Fuel Injector', 'Heater Core',
                               'Master Cylinder', 'Shock Absorber', 'Spark Plug Set', 'Brake Rotor', 'Control Arm',
                               'Condenser', 'Blower Motor', 'Water Pump', 'Thermostat', 'Belt Tensioner'],
        'Arabic_Description': ['مجموعة الضاغط', 'طقم مضخة الوقود', 'طقم فرامل', 'مولد', 'مجموعة دعامة',
                              'ملف الإشعال', 'المبرد', 'بطارية 12 فولت', 'حاقن الوقود', 'نواة السخان',
                              'اسطوانة رئيسية', 'ممتص الصدمات', 'طقم شمعة إشعال', 'قرص الفرامل', 'ذراع التحكم',
                              'المكثف', 'محرك النفخ', 'مضخة الماء', 'منظم الحرارة', 'شد الحزام'],
        'Part_Location': [f'A-{i:02d}' for i in range(1, 21)],
        'Part_Quantity': np.random.randint(5, 100, 20)
    })
    
    st.session_state.df_supply_request = pd.DataFrame({
        'Supply_Request_ID': [1, 2, 3],
        'Work_Order_ID': [1, 2, 5],
        'Part_ID': [1, 2, 3],
        'Quantity_Requested': [2, 1, 4],
        'Status': ['Pending', 'Approved', 'Issued']
    })
    
    st.session_state.df_purchase_request = pd.DataFrame({
        'PR_ID': [1, 2],
        'Supply_Request_ID': [1, 2],
        'Employee_ID': [5, 5],
        'PR_Date': [(datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d'),
                    (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')],
        'Status': ['Pending', 'Approved']
    })
    
    st.session_state.df_orders = pd.DataFrame({
        'PO_ID': [1],
        'Order_Status': ['In Transit'],
        'Order_Date': [(datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d')],
        'Delivery_Date': [(datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')],
        'Warehouse_Status': ['Pending Receipt']
    })
    
    # Counter for new IDs
    st.session_state.work_order_id_counter = wo_id_counter
    st.session_state.malfunction_id_counter = mal_id_counter
    st.session_state.supply_request_id_counter = 4
    st.session_state.purchase_request_id_counter = 3
    st.session_state.order_id_counter = 2
    
    st.session_state.data_initialized = True

# ============================================================================
# AUTHENTICATION
# ============================================================================

def login_page():
    """Display login page"""
    st.title("🔧 AMIC MMS - Work Order Management")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("🔐 Login")
        
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", use_container_width=True, type="primary"):
            if username and password:
                hashed_pw = hash_password(password)
                user = st.session_state.df_user[
                    (st.session_state.df_user['Username'] == username) & 
                    (st.session_state.df_user['Password'] == hashed_pw)
                ]
                
                if not user.empty:
                    st.session_state.logged_in = True
                    st.session_state.current_user = user.iloc[0].to_dict()
                    st.success(f"Welcome, {user.iloc[0]['Employee_First_Name']}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.warning("Please enter both username and password")
        
        st.markdown("---")
        st.info("""
        **Demo Accounts:**
        - Technician: `ali.tech` / `tech123`
        - Supervisor: `omar.super` / `super123`
        - Manager: `nora.mgr` / `mgr123`
        - Inventory: `layla.inv` / `inv123`
        - Procurement: `hassan.proc` / `proc123`
        - Admin: `admin` / `admin123`
        """)

def logout():
    """Handle logout"""
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.rerun()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_cascading_options(system=None, subsystem=None, component=None):
    """Get cascading dropdown options from failure catalogue"""
    df = st.session_state.df_failure_catalogue
    
    if system is None:
        return sorted(df['System'].unique().tolist())
    
    df = df[df['System'] == system]
    if subsystem is None:
        return sorted(df['Subsystem'].unique().tolist())
    
    df = df[df['Subsystem'] == subsystem]
    if component is None:
        return sorted(df['Component'].unique().tolist())
    
    df = df[df['Component'] == component]
    return sorted(df['Failure_Mode'].unique().tolist())

def get_failure_details(system, subsystem, component, failure_mode):
    """Get failure details from catalogue"""
    df = st.session_state.df_failure_catalogue
    result = df[
        (df['System'] == system) & 
        (df['Subsystem'] == subsystem) & 
        (df['Component'] == component) & 
        (df['Failure_Mode'] == failure_mode)
    ]
    
    if not result.empty:
        return result.iloc[0].to_dict()
    return None

# ============================================================================
# PAGES
# ============================================================================

def page_dashboard():
    """Home dashboard for all users"""
    st.title("📊 Dashboard")
    
    user = st.session_state.current_user
    st.write(f"Welcome, **{user['Employee_First_Name']} {user['Employee_Last_Name']}** ({user['Role']})")
    
    st.markdown("---")
    
    # Filter work orders based on role
    df_wo = st.session_state.df_work_orders.copy()
    
    if user['Role'] in ['Technician', 'Supervisor']:
        # Filter by workshop
        df_wo = df_wo[df_wo['Workshop_Name'] == user['Workshop_Name']]
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Work Orders", len(df_wo))
    
    with col2:
        open_count = len(df_wo[df_wo['Work_Order_Status'] == 'Open'])
        st.metric("Open", open_count)
    
    with col3:
        in_progress = len(df_wo[df_wo['Work_Order_Status'] == 'In Progress'])
        st.metric("In Progress", in_progress)
    
    with col4:
        completed = len(df_wo[df_wo['Work_Order_Status'] == 'Completed'])
        st.metric("Completed", completed)
    
    # Charts
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Work Orders by Status")
        status_counts = df_wo['Work_Order_Status'].value_counts()
        st.bar_chart(status_counts)
    
    with col2:
        st.subheader("Work Orders by Workshop")
        workshop_counts = df_wo['Workshop_Name'].value_counts()
        st.bar_chart(workshop_counts)
    
    # Recent work orders
    st.markdown("---")
    st.subheader("Recent Work Orders")
    
    display_cols = ['Work_Order_ID', 'Vehicle_Number', 'Workshop_Name', 'Work_Order_Status', 
                   'Malfunction_Date', 'Technician_Name']
    
    st.dataframe(
        df_wo[display_cols].head(10),
        use_container_width=True,
        hide_index=True
    )

def page_create_work_order():
    """Page for technicians to create work orders"""
    st.title("➕ Create Work Order")
    
    user = st.session_state.current_user
    
    with st.form("create_wo_form", clear_on_submit=True):
        st.subheader("📋 Basic Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Workshop selection (filtered by user's workshop if technician)
            if user['Role'] == 'Technician':
                workshop = st.text_input("Workshop", value=user['Workshop_Name'], disabled=True)
            else:
                workshops = st.session_state.df_workshop['Workshop_Name'].tolist()
                workshop = st.selectbox("Workshop *", workshops)
        
        with col2:
            # Vehicle selection
            vehicles = st.session_state.df_vehicle['Vehicle_Number'].tolist()
            vehicle_number = st.selectbox("Vehicle Number *", vehicles)
        
        col1, col2 = st.columns(2)
        
        with col1:
            received_date = st.date_input("Received Date *", datetime.now())
        
        with col2:
            malfunction_date = st.date_input("Malfunction Date *", datetime.now())
        
        # Cascading failure selection
        st.markdown("---")
        st.subheader("🔧 Fault Classification")
        st.caption("Select System → Subsystem → Component → Failure Mode")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            systems = get_cascading_options()
            selected_system = st.selectbox("System *", [''] + systems)
        
        with col2:
            subsystems = get_cascading_options(selected_system) if selected_system else []
            selected_subsystem = st.selectbox("Subsystem *", [''] + subsystems)
        
        with col3:
            components = get_cascading_options(selected_system, selected_subsystem) if selected_subsystem else []
            selected_component = st.selectbox("Component *", [''] + components)
        
        with col4:
            failure_modes = get_cascading_options(selected_system, selected_subsystem, selected_component) if selected_component else []
            selected_failure = st.selectbox("Failure Mode *", [''] + failure_modes)
        
        # Auto-populated fields
        failure_details = None
        if selected_system and selected_subsystem and selected_component and selected_failure:
            failure_details = get_failure_details(selected_system, selected_subsystem, selected_component, selected_failure)
            
            if failure_details:
                st.markdown("---")
                st.subheader("✨ Auto-Generated Codes")
                st.success("Codes automatically generated from catalogue")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.text_input("Failure Code", value=failure_details['Failure_Code'], disabled=True)
                with col2:
                    st.text_input("Cause Code", value=failure_details['Cause_Code'], disabled=True)
                with col3:
                    st.text_input("Resolution Code", value=failure_details['Resolution_Code'], disabled=True)
                
                st.markdown("**Recommended Action:**")
                st.info(failure_details['Recommended_Action'])
        
        # Additional details
        st.markdown("---")
        st.subheader("📄 Additional Details")
        
        require_parts = st.checkbox("Require Spare Parts")
        comments = st.text_area("Comments", height=100)
        
        # Submit
        st.markdown("")
        submitted = st.form_submit_button("🚀 Create Work Order", use_container_width=True, type="primary")
        
        if submitted:
            if not vehicle_number or not selected_system or not selected_subsystem or not selected_component or not selected_failure:
                st.error("Please complete all required fields")
            elif not failure_details:
                st.error("Invalid fault classification")
            else:
                # Get vehicle details
                vehicle = st.session_state.df_vehicle[
                    st.session_state.df_vehicle['Vehicle_Number'] == vehicle_number
                ].iloc[0]
                
                # Create work order
                wo_id = st.session_state.work_order_id_counter
                mal_id = st.session_state.malfunction_id_counter
                
                new_wo = {
                    'Work_Order_ID': wo_id,
                    'Employee_ID': user['Employee_ID'],
                    'Workshop_Name': workshop if user['Role'] != 'Technician' else user['Workshop_Name'],
                    'Vehicle_Number': vehicle_number,
                    'A_Received_Date': received_date.strftime('%Y-%m-%d'),
                    'Equipment_Owning_Unit': vehicle['Unit_Name'],
                    'Vehicle_Type': vehicle['Vehicle_Type'],
                    'Malfunction_Date': malfunction_date.strftime('%Y-%m-%d'),
                    'Work_Order_Date': datetime.now().strftime('%Y-%m-%d'),
                    'Technician_Name': f"{user['Employee_First_Name']} {user['Employee_Last_Name']}",
                    'Work_Order_Status': 'Open',
                    'Require_Spare_Parts': require_parts,
                    'Work_Order_Completion_Date': None,
                    'Comments': comments
                }
                
                new_malfunction = {
                    'Malfunction_ID': mal_id,
                    'Vehicle_Number': vehicle_number,
                    'Work_Order_ID': wo_id,
                    'Malfunction_Code': failure_details['Failure_Code'],
                    'Resolution_Description_English': failure_details['Recommended_Action'],
                    'Resolution_Description_Arabic': 'إجراء موصى به',
                    'Root_Cause': failure_details['Failure_Mode'],
                    'Cause_Code': failure_details['Cause_Code'],
                    'Cause_Description_English': failure_details['Failure_Mode'],
                    'Cause_Description_Arabic': 'وصف السبب',
                    'Fault_Code': failure_details['Failure_Code']
                }
                
                # Add to dataframes
                st.session_state.df_work_orders = pd.concat([
                    st.session_state.df_work_orders,
                    pd.DataFrame([new_wo])
                ], ignore_index=True)
                
                st.session_state.df_malfunction = pd.concat([
                    st.session_state.df_malfunction,
                    pd.DataFrame([new_malfunction])
                ], ignore_index=True)
                
                # Increment counters
                st.session_state.work_order_id_counter += 1
                st.session_state.malfunction_id_counter += 1
                
                st.success(f"✅ Work Order **WO-{wo_id:05d}** created successfully!")
                st.balloons()

def page_my_work_orders():
    """Page for technicians to view their work orders"""
    st.title("📋 My Work Orders")
    
    user = st.session_state.current_user
    
    # Filter work orders by technician
    df_wo = st.session_state.df_work_orders[
        st.session_state.df_work_orders['Employee_ID'] == user['Employee_ID']
    ].copy()
    
    # Filters
    col1, col2 = st.columns(2)
    
    with col1:
        status_filter = st.selectbox("Filter by Status", ['All'] + ['Open', 'In Progress', 'Completed'])
    
    with col2:
        vehicle_filter = st.selectbox("Filter by Vehicle", ['All'] + sorted(df_wo['Vehicle_Number'].unique().tolist()))
    
    # Apply filters
    if status_filter != 'All':
        df_wo = df_wo[df_wo['Work_Order_Status'] == status_filter]
    
    if vehicle_filter != 'All':
        df_wo = df_wo[df_wo['Vehicle_Number'] == vehicle_filter]
    
    st.info(f"Showing {len(df_wo)} work orders")
    
    # Display work orders
    for idx, wo in df_wo.iterrows():
        with st.expander(f"WO-{wo['Work_Order_ID']:05d} - {wo['Vehicle_Number']} - {wo['Work_Order_Status']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Work Order ID:** WO-{wo['Work_Order_ID']:05d}")
                st.markdown(f"**Vehicle:** {wo['Vehicle_Number']}")
                st.markdown(f"**Workshop:** {wo['Workshop_Name']}")
                st.markdown(f"**Status:** {wo['Work_Order_Status']}")
            
            with col2:
                st.markdown(f"**Malfunction Date:** {wo['Malfunction_Date']}")
                st.markdown(f"**WO Date:** {wo['Work_Order_Date']}")
                st.markdown(f"**Require Parts:** {'Yes' if wo['Require_Spare_Parts'] else 'No'}")
                if wo['Work_Order_Completion_Date']:
                    st.markdown(f"**Completion Date:** {wo['Work_Order_Completion_Date']}")
            
            if wo['Comments']:
                st.markdown("**Comments:**")
                st.info(wo['Comments'])

def page_supervisor_work_orders():
    """Page for supervisors to manage work orders"""
    st.title("📋 Workshop Work Orders")
    
    user = st.session_state.current_user
    
    # Filter by supervisor's workshop
    df_wo = st.session_state.df_work_orders[
        st.session_state.df_work_orders['Workshop_Name'] == user['Workshop_Name']
    ].copy()
    
    # Filters
    col1, col2 = st.columns(2)
    
    with col1:
        status_filter = st.selectbox("Filter by Status", ['All'] + ['Open', 'In Progress', 'Completed'])
    
    with col2:
        vehicle_filter = st.selectbox("Filter by Vehicle", ['All'] + sorted(df_wo['Vehicle_Number'].unique().tolist()))
    
    # Apply filters
    if status_filter != 'All':
        df_wo = df_wo[df_wo['Work_Order_Status'] == status_filter]
    
    if vehicle_filter != 'All':
        df_wo = df_wo[df_wo['Vehicle_Number'] == vehicle_filter]
    
    st.info(f"Showing {len(df_wo)} work orders for {user['Workshop_Name']}")
    
    # Display work orders with edit capability
    for idx, wo in df_wo.iterrows():
        with st.expander(f"WO-{wo['Work_Order_ID']:05d} - {wo['Vehicle_Number']} - {wo['Work_Order_Status']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Work Order ID:** WO-{wo['Work_Order_ID']:05d}")
                st.markdown(f"**Vehicle:** {wo['Vehicle_Number']}")
                st.markdown(f"**Technician:** {wo['Technician_Name']}")
                st.markdown(f"**Malfunction Date:** {wo['Malfunction_Date']}")
            
            with col2:
                # Editable status
                new_status = st.selectbox(
                    "Status",
                    ['Open', 'In Progress', 'Completed'],
                    index=['Open', 'In Progress', 'Completed'].index(wo['Work_Order_Status']),
                    key=f"status_{wo['Work_Order_ID']}"
                )
                
                if new_status == 'Completed':
                    completion_date = st.date_input(
                        "Completion Date",
                        value=datetime.strptime(wo['Work_Order_Completion_Date'], '%Y-%m-%d') if wo['Work_Order_Completion_Date'] else datetime.now(),
                        key=f"completion_{wo['Work_Order_ID']}"
                    )
                
                new_comments = st.text_area(
                    "Comments",
                    value=wo['Comments'] if wo['Comments'] else '',
                    key=f"comments_{wo['Work_Order_ID']}"
                )
            
            # Update button
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("💾 Update", key=f"update_{wo['Work_Order_ID']}", use_container_width=True):
                    # Update work order
                    st.session_state.df_work_orders.loc[
                        st.session_state.df_work_orders['Work_Order_ID'] == wo['Work_Order_ID'],
                        'Work_Order_Status'
                    ] = new_status
                    
                    st.session_state.df_work_orders.loc[
                        st.session_state.df_work_orders['Work_Order_ID'] == wo['Work_Order_ID'],
                        'Comments'
                    ] = new_comments
                    
                    if new_status == 'Completed':
                        st.session_state.df_work_orders.loc[
                            st.session_state.df_work_orders['Work_Order_ID'] == wo['Work_Order_ID'],
                            'Work_Order_Completion_Date'
                        ] = completion_date.strftime('%Y-%m-%d')
                    
                    st.success("Work order updated!")
                    st.rerun()
            
            with col2:
                if wo['Require_Spare_Parts'] and st.button("📦 Create Supply Request", key=f"supply_{wo['Work_Order_ID']}", use_container_width=True):
                    st.session_state.selected_wo_for_supply = wo['Work_Order_ID']
                    st.session_state.show_supply_form = True

def page_manager_dashboard():
    """Page for managers to view all sites"""
    st.title("📊 Manager Dashboard - All Sites")
    
    df_wo = st.session_state.df_work_orders.copy()
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        regions = ['All'] + sorted(st.session_state.df_region['Region_Name'].tolist())
        region_filter = st.selectbox("Region", regions)
    
    with col2:
        workshops = ['All'] + sorted(st.session_state.df_workshop['Workshop_Name'].tolist())
        workshop_filter = st.selectbox("Workshop", workshops)
    
    with col3:
        status_filter = st.selectbox("Status", ['All'] + ['Open', 'In Progress', 'Completed'])
    
    with col4:
        systems = ['All'] + sorted(st.session_state.df_failure_catalogue['System'].unique().tolist())
        system_filter = st.selectbox("System", systems)
    
    # Apply filters
    if workshop_filter != 'All':
        df_wo = df_wo[df_wo['Workshop_Name'] == workshop_filter]
    elif region_filter != 'All':
        workshops_in_region = st.session_state.df_workshop[
            st.session_state.df_workshop['Region'] == region_filter
        ]['Workshop_Name'].tolist()
        df_wo = df_wo[df_wo['Workshop_Name'].isin(workshops_in_region)]
    
    if status_filter != 'All':
        df_wo = df_wo[df_wo['Work_Order_Status'] == status_filter]
    
    if system_filter != 'All':
        # Get WO IDs with this system
        mal_df = st.session_state.df_malfunction.merge(
            st.session_state.df_failure_catalogue[['Failure_Code', 'System']],
            left_on='Malfunction_Code',
            right_on='Failure_Code',
            how='left'
        )
        wo_ids = mal_df[mal_df['System'] == system_filter]['Work_Order_ID'].unique()
        df_wo = df_wo[df_wo['Work_Order_ID'].isin(wo_ids)]
    
    # KPIs
    st.markdown("---")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total WOs", len(df_wo))
    
    with col2:
        st.metric("Open", len(df_wo[df_wo['Work_Order_Status'] == 'Open']))
    
    with col3:
        st.metric("In Progress", len(df_wo[df_wo['Work_Order_Status'] == 'In Progress']))
    
    with col4:
        st.metric("Completed", len(df_wo[df_wo['Work_Order_Status'] == 'Completed']))
    
    with col5:
        # Average completion time
        completed = df_wo[df_wo['Work_Order_Status'] == 'Completed'].copy()
        if not completed.empty and completed['Work_Order_Completion_Date'].notna().any():
            completed['wo_date'] = pd.to_datetime(completed['Work_Order_Date'])
            completed['completion_date'] = pd.to_datetime(completed['Work_Order_Completion_Date'])
            completed['days'] = (completed['completion_date'] - completed['wo_date']).dt.days
            avg_days = completed['days'].mean()
            st.metric("Avg Days to Complete", f"{avg_days:.1f}")
        else:
            st.metric("Avg Days to Complete", "N/A")
    
    # Top failure modes
    st.markdown("---")
    st.subheader("Top 5 Failure Modes")
    
    mal_df = st.session_state.df_malfunction[
        st.session_state.df_malfunction['Work_Order_ID'].isin(df_wo['Work_Order_ID'])
    ]
    
    if not mal_df.empty:
        top_failures = mal_df['Root_Cause'].value_counts().head(5)
        st.bar_chart(top_failures)
    else:
        st.info("No data available")
    
    # Work orders table
    st.markdown("---")
    st.subheader("Work Orders")
    
    display_cols = ['Work_Order_ID', 'Vehicle_Number', 'Workshop_Name', 'Work_Order_Status',
                   'Malfunction_Date', 'Technician_Name', 'Require_Spare_Parts']
    
    st.dataframe(
        df_wo[display_cols],
        use_container_width=True,
        hide_index=True,
        column_config={
            'Work_Order_ID': 'WO ID',
            'Vehicle_Number': 'Vehicle',
            'Workshop_Name': 'Workshop',
            'Work_Order_Status': 'Status',
            'Malfunction_Date': 'Malfunction Date',
            'Technician_Name': 'Technician',
            'Require_Spare_Parts': 'Needs Parts'
        }
    )

def page_inventory():
    """Page for inventory users"""
    st.title("📦 Inventory Management")
    
    tab1, tab2, tab3 = st.tabs(["Supply Requests", "Parts Inventory", "Update Quantity"])
    
    with tab1:
        st.subheader("Supply Requests")
        
        df_sr = st.session_state.df_supply_request.copy()
        
        # Merge with work orders and parts
        df_sr = df_sr.merge(
            st.session_state.df_work_orders[['Work_Order_ID', 'Vehicle_Number', 'Workshop_Name']],
            on='Work_Order_ID',
            how='left'
        )
        
        df_sr = df_sr.merge(
            st.session_state.df_part[['Part_ID', 'Part_Number', 'English_Description']],
            on='Part_ID',
            how='left'
        )
        
        st.dataframe(
            df_sr,
            use_container_width=True,
            hide_index=True,
            column_config={
                'Supply_Request_ID': 'SR ID',
                'Work_Order_ID': 'WO ID',
                'Vehicle_Number': 'Vehicle',
                'Workshop_Name': 'Workshop',
                'Part_Number': 'Part Number',
                'English_Description': 'Description',
                'Quantity_Requested': 'Qty',
                'Status': 'Status'
            }
        )
        
        # Update status
        st.markdown("---")
        st.subheader("Update Supply Request Status")
        
        sr_id = st.number_input("Supply Request ID", min_value=1, step=1)
        new_status = st.selectbox("New Status", ['Pending', 'Approved', 'Issued', 'Cancelled'])
        
        if st.button("Update Status", type="primary"):
            if sr_id in st.session_state.df_supply_request['Supply_Request_ID'].values:
                st.session_state.df_supply_request.loc[
                    st.session_state.df_supply_request['Supply_Request_ID'] == sr_id,
                    'Status'
                ] = new_status
                st.success(f"Supply Request {sr_id} updated to {new_status}")
                st.rerun()
            else:
                st.error("Supply Request ID not found")
    
    with tab2:
        st.subheader("Parts Inventory")
        
        st.dataframe(
            st.session_state.df_part,
            use_container_width=True,
            hide_index=True,
            column_config={
                'Part_Quantity': st.column_config.NumberColumn('Quantity', format="%d")
            }
        )
    
    with tab3:
        st.subheader("Update Part Quantity")
        
        col1, col2 = st.columns(2)
        
        with col1:
            part_id = st.selectbox(
                "Select Part",
                st.session_state.df_part['Part_ID'].tolist(),
                format_func=lambda x: f"{st.session_state.df_part[st.session_state.df_part['Part_ID']==x]['Part_Number'].iloc[0]} - {st.session_state.df_part[st.session_state.df_part['Part_ID']==x]['English_Description'].iloc[0]}"
            )
        
        with col2:
            current_qty = st.session_state.df_part[st.session_state.df_part['Part_ID']==part_id]['Part_Quantity'].iloc[0]
            st.metric("Current Quantity", current_qty)
        
        new_qty = st.number_input("New Quantity", min_value=0, value=int(current_qty))
        
        if st.button("Update Quantity", type="primary"):
            st.session_state.df_part.loc[
                st.session_state.df_part['Part_ID'] == part_id,
                'Part_Quantity'
            ] = new_qty
            st.success(f"Part {part_id} quantity updated to {new_qty}")
            st.rerun()

def page_procurement():
    """Page for procurement users"""
    st.title("💼 Procurement")
    
    tab1, tab2, tab3 = st.tabs(["Supply Requests", "Create PR", "Orders"])
    
    with tab1:
        st.subheader("Supply Requests Requiring Purchase")
        
        df_sr = st.session_state.df_supply_request[
            st.session_state.df_supply_request['Status'] == 'Approved'
        ].copy()
        
        # Merge with parts
        df_sr = df_sr.merge(
            st.session_state.df_part[['Part_ID', 'Part_Number', 'English_Description', 'Part_Quantity']],
            on='Part_ID',
            how='left'
        )
        
        # Show only those needing purchase (quantity < requested)
        df_sr['Needs_Purchase'] = df_sr['Part_Quantity'] < df_sr['Quantity_Requested']
        df_sr = df_sr[df_sr['Needs_Purchase']]
        
        st.dataframe(
            df_sr[['Supply_Request_ID', 'Part_Number', 'English_Description', 
                  'Quantity_Requested', 'Part_Quantity']],
            use_container_width=True,
            hide_index=True,
            column_config={
                'Supply_Request_ID': 'SR ID',
                'Part_Number': 'Part Number',
                'English_Description': 'Description',
                'Quantity_Requested': 'Qty Needed',
                'Part_Quantity': 'In Stock'
            }
        )
    
    with tab2:
        st.subheader("Create Purchase Request")
        
        user = st.session_state.current_user
        
        with st.form("create_pr_form"):
            supply_request_id = st.number_input("Supply Request ID", min_value=1, step=1)
            
            submitted = st.form_submit_button("Create PR", type="primary")
            
            if submitted:
                if supply_request_id in st.session_state.df_supply_request['Supply_Request_ID'].values:
                    pr_id = st.session_state.purchase_request_id_counter
                    
                    new_pr = {
                        'PR_ID': pr_id,
                        'Supply_Request_ID': supply_request_id,
                        'Employee_ID': user['Employee_ID'],
                        'PR_Date': datetime.now().strftime('%Y-%m-%d'),
                        'Status': 'Pending'
                    }
                    
                    st.session_state.df_purchase_request = pd.concat([
                        st.session_state.df_purchase_request,
                        pd.DataFrame([new_pr])
                    ], ignore_index=True)
                    
                    st.session_state.purchase_request_id_counter += 1
                    
                    st.success(f"Purchase Request PR-{pr_id:05d} created!")
                else:
                    st.error("Supply Request ID not found")
    
    with tab3:
        st.subheader("Purchase Orders")
        
        st.dataframe(
            st.session_state.df_orders,
            use_container_width=True,
            hide_index=True,
            column_config={
                'PO_ID': 'PO ID',
                'Order_Status': 'Status',
                'Order_Date': 'Order Date',
                'Delivery_Date': 'Delivery Date',
                'Warehouse_Status': 'Warehouse Status'
            }
        )

def page_admin_catalogue():
    """Page for admin to manage failure catalogue"""
    st.title("⚙️ Failure Catalogue Management")
    
    tab1, tab2 = st.tabs(["View Catalogue", "Add Entry"])
    
    with tab1:
        st.subheader("Current Failure Catalogue")
        
        st.dataframe(
            st.session_state.df_failure_catalogue,
            use_container_width=True,
            hide_index=True
        )
    
    with tab2:
        st.subheader("Add New Catalogue Entry")
        
        with st.form("add_catalogue_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                system = st.text_input("System *")
                subsystem = st.text_input("Subsystem *")
                component = st.text_input("Component *")
                failure_mode = st.text_input("Failure Mode *")
            
            with col2:
                failure_code = st.text_input("Failure Code *")
                cause_code = st.text_input("Cause Code *")
                resolution_code = st.text_input("Resolution Code *")
            
            recommended_action = st.text_area("Recommended Action *", height=100)
            
            submitted = st.form_submit_button("Add to Catalogue", type="primary")
            
            if submitted:
                if all([system, subsystem, component, failure_mode, failure_code, 
                       cause_code, resolution_code, recommended_action]):
                    
                    new_entry = {
                        'System': system,
                        'Subsystem': subsystem,
                        'Component': component,
                        'Failure_Mode': failure_mode,
                        'Failure_Code': failure_code,
                        'Cause_Code': cause_code,
                        'Resolution_Code': resolution_code,
                        'Recommended_Action': recommended_action
                    }
                    
                    st.session_state.df_failure_catalogue = pd.concat([
                        st.session_state.df_failure_catalogue,
                        pd.DataFrame([new_entry])
                    ], ignore_index=True)
                    
                    st.success("✅ Catalogue entry added successfully!")
                    st.balloons()
                else:
                    st.error("Please fill in all required fields")

def page_admin_users():
    """Page for admin to view users"""
    st.title("👥 User Management")
    
    st.dataframe(
        st.session_state.df_user[['Employee_ID', 'Employee_First_Name', 'Employee_Last_Name', 
                                  'Job_Title', 'Department_Code', 'Role', 'Username']],
        use_container_width=True,
        hide_index=True
    )

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

def render_sidebar():
    """Render sidebar navigation based on user role"""
    
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        return None
    
    user = st.session_state.current_user
    
    with st.sidebar:
        st.title("🔧 AMIC MMS")
        st.caption("Work Order Management")
        
        st.markdown("---")
        
        st.write(f"**{user['Employee_First_Name']} {user['Employee_Last_Name']}**")
        st.caption(f"Role: {user['Role']}")
        if user['Workshop_Name']:
            st.caption(f"Workshop: {user['Workshop_Name']}")
        
        st.markdown("---")
        
        # Role-based navigation
        pages = {
            'Dashboard': 'dashboard'
        }
        
        if user['Role'] == 'Technician':
            pages['Create Work Order'] = 'create_wo'
            pages['My Work Orders'] = 'my_wo'
        
        elif user['Role'] == 'Supervisor':
            pages['Create Work Order'] = 'create_wo'
            pages['Workshop Work Orders'] = 'supervisor_wo'
        
        elif user['Role'] == 'Manager':
            pages['Manager Dashboard'] = 'manager'
        
        elif user['Role'] == 'Inventory':
            pages['Inventory'] = 'inventory'
        
        elif user['Role'] == 'Procurement':
            pages['Procurement'] = 'procurement'
        
        elif user['Role'] == 'Admin':
            pages['Failure Catalogue'] = 'catalogue'
            pages['Users'] = 'users'
        
        selected = st.radio("Navigation", list(pages.keys()))
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            logout()
        
        return pages[selected]

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point"""
    
    # Initialize data
    init_data()
    
    # Check if logged in
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        login_page()
        return
    
    # Render sidebar and get selected page
    page = render_sidebar()
    
    # Route to appropriate page
    if page == 'dashboard':
        page_dashboard()
    elif page == 'create_wo':
        page_create_work_order()
    elif page == 'my_wo':
        page_my_work_orders()
    elif page == 'supervisor_wo':
        page_supervisor_work_orders()
    elif page == 'manager':
        page_manager_dashboard()
    elif page == 'inventory':
        page_inventory()
    elif page == 'procurement':
        page_procurement()
    elif page == 'catalogue':
        page_admin_catalogue()
    elif page == 'users':
        page_admin_users()

if __name__ == "__main__":
    main()
