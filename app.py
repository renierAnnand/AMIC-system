"""
AMIC Maintenance Management System (MMS) - Enhanced Version
✅ Complete 427 Failure Mode Catalogue from Excel
✅ Bill of Materials (BOM) Generation
✅ Full Procurement Integration
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
    page_title="AMIC MMS - Enhanced",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# STYLING
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

/* Sidebar - Light Gray with better visibility */
[data-testid="stSidebar"] {
    background-color: #F9FAFB !important;
    color: #111827 !important;
    min-width: 280px !important;
}

[data-testid="stSidebar"] > div:first-child {
    background-color: #F9FAFB !important;
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

/* CRITICAL FIX: Dropdown menus visibility */
[data-baseweb="select"] {
    background-color: #FFFFFF !important;
}

[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    color: #111827 !important;
}

[data-baseweb="popover"] {
    background-color: #FFFFFF !important;
}

[data-baseweb="menu"] {
    background-color: #FFFFFF !important;
}

[data-baseweb="menu"] ul {
    background-color: #FFFFFF !important;
}

[role="option"] {
    background-color: #FFFFFF !important;
    color: #111827 !important;
}

[role="option"]:hover {
    background-color: #F3F4F6 !important;
    color: #111827 !important;
}

[aria-selected="true"] {
    background-color: #DBEAFE !important;
    color: #1E40AF !important;
}

.stSelectbox label {
    color: #111827 !important;
}

.stSelectbox div[data-baseweb="select"] > div {
    color: #111827 !important;
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

/* Info boxes */
.stInfo {
    background-color: #DBEAFE !important;
    color: #1E40AF !important;
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

def load_failure_catalogue_from_excel():
    """Load the complete 427-entry failure catalogue from Excel"""
    try:
        file_path = '/mnt/user-data/uploads/FRACAS_FailureMode_Catalogue_v5_WithCodes.xlsx'
        df = pd.read_excel(file_path, sheet_name='FRACAS_FailureMode_Catalogue')
        
        # Clean up column names and data
        df.columns = df.columns.str.strip()
        
        # Handle any NaN values in codes
        df['Failure Code'] = df['Failure Code'].fillna('UNKNOWN')
        df['Cause Code'] = df['Cause Code'].fillna('UNKNOWN')
        df['Resolution Code'] = df['Resolution Code'].fillna('UNKNOWN')
        
        print(f"✓ Loaded {len(df)} failure modes from Excel")
        print(f"✓ Systems: {df['System'].nunique()}")
        print(f"✓ Subsystems: {df['Subsystem'].nunique()}")
        print(f"✓ Components: {df['Component'].nunique()}")
        
        return df
    except Exception as e:
        print(f"Error loading Excel: {e}")
        # Return empty dataframe with correct structure if file can't be loaded
        return pd.DataFrame(columns=[
            'System', 'Subsystem', 'Component', 'Failure Mode', 
            'Recommended Action', 'Failure Code', 'Cause Code', 'Resolution Code'
        ])

def generate_bom_for_failure(failure_code, failure_mode, component, recommended_action):
    """Generate Bill of Materials based on failure mode"""
    # Parse the recommended action to extract parts needed
    bom_items = []
    
    # Common part mappings based on component and action keywords
    parts_database = {
        'Compressor': [
            {'Part_Number': 'PN-COMP-001', 'Description': 'A/C Compressor Assembly', 'Quantity': 1, 'Unit_Cost': 450.00},
            {'Part_Number': 'PN-COMP-002', 'Description': 'Compressor Clutch Kit', 'Quantity': 1, 'Unit_Cost': 120.00},
            {'Part_Number': 'PN-HVAC-001', 'Description': 'Filter/Drier', 'Quantity': 1, 'Unit_Cost': 35.00},
            {'Part_Number': 'PN-HVAC-002', 'Description': 'Refrigerant R134a (1kg)', 'Quantity': 2, 'Unit_Cost': 25.00}
        ],
        'Condenser': [
            {'Part_Number': 'PN-COND-001', 'Description': 'A/C Condenser', 'Quantity': 1, 'Unit_Cost': 280.00},
            {'Part_Number': 'PN-HVAC-002', 'Description': 'Refrigerant R134a (1kg)', 'Quantity': 2, 'Unit_Cost': 25.00}
        ],
        'Fuel Pump': [
            {'Part_Number': 'PN-FUEL-001', 'Description': 'Fuel Pump Assembly', 'Quantity': 1, 'Unit_Cost': 180.00},
            {'Part_Number': 'PN-FUEL-002', 'Description': 'Fuel Filter', 'Quantity': 1, 'Unit_Cost': 25.00},
            {'Part_Number': 'PN-FUEL-003', 'Description': 'Fuel Line Gasket Kit', 'Quantity': 1, 'Unit_Cost': 15.00}
        ],
        'Fuel Injector': [
            {'Part_Number': 'PN-INJ-001', 'Description': 'Fuel Injector', 'Quantity': 4, 'Unit_Cost': 85.00},
            {'Part_Number': 'PN-INJ-002', 'Description': 'Injector O-Ring Kit', 'Quantity': 1, 'Unit_Cost': 12.00}
        ],
        'Spark Plug': [
            {'Part_Number': 'PN-IGN-001', 'Description': 'Spark Plug Set (4pcs)', 'Quantity': 1, 'Unit_Cost': 45.00}
        ],
        'Ignition Coil': [
            {'Part_Number': 'PN-IGN-010', 'Description': 'Ignition Coil', 'Quantity': 1, 'Unit_Cost': 95.00}
        ],
        'Radiator': [
            {'Part_Number': 'PN-COOL-001', 'Description': 'Radiator Assembly', 'Quantity': 1, 'Unit_Cost': 320.00},
            {'Part_Number': 'PN-COOL-002', 'Description': 'Radiator Cap', 'Quantity': 1, 'Unit_Cost': 18.00},
            {'Part_Number': 'PN-COOL-003', 'Description': 'Coolant (5L)', 'Quantity': 2, 'Unit_Cost': 22.00}
        ],
        'Water Pump': [
            {'Part_Number': 'PN-COOL-010', 'Description': 'Water Pump', 'Quantity': 1, 'Unit_Cost': 125.00},
            {'Part_Number': 'PN-COOL-011', 'Description': 'Water Pump Gasket', 'Quantity': 1, 'Unit_Cost': 8.00}
        ],
        'Master Cylinder': [
            {'Part_Number': 'PN-BRK-001', 'Description': 'Master Cylinder', 'Quantity': 1, 'Unit_Cost': 210.00},
            {'Part_Number': 'PN-BRK-002', 'Description': 'Brake Fluid DOT4 (1L)', 'Quantity': 2, 'Unit_Cost': 12.00}
        ],
        'Brake Pad': [
            {'Part_Number': 'PN-BRK-010', 'Description': 'Brake Pad Set Front', 'Quantity': 1, 'Unit_Cost': 85.00},
            {'Part_Number': 'PN-BRK-011', 'Description': 'Brake Pad Set Rear', 'Quantity': 1, 'Unit_Cost': 75.00},
            {'Part_Number': 'PN-BRK-012', 'Description': 'Brake Cleaner', 'Quantity': 1, 'Unit_Cost': 8.00}
        ],
        'Brake Rotor': [
            {'Part_Number': 'PN-BRK-020', 'Description': 'Brake Rotor Front (2pcs)', 'Quantity': 1, 'Unit_Cost': 150.00},
            {'Part_Number': 'PN-BRK-021', 'Description': 'Brake Rotor Rear (2pcs)', 'Quantity': 1, 'Unit_Cost': 130.00}
        ],
        'Strut': [
            {'Part_Number': 'PN-SUSP-001', 'Description': 'Strut Assembly', 'Quantity': 2, 'Unit_Cost': 185.00},
            {'Part_Number': 'PN-SUSP-002', 'Description': 'Strut Mount', 'Quantity': 2, 'Unit_Cost': 45.00}
        ],
        'Shock Absorber': [
            {'Part_Number': 'PN-SUSP-010', 'Description': 'Shock Absorber', 'Quantity': 2, 'Unit_Cost': 95.00}
        ],
        'Control Arm': [
            {'Part_Number': 'PN-SUSP-020', 'Description': 'Control Arm Bushing Kit', 'Quantity': 1, 'Unit_Cost': 65.00}
        ],
        'Battery': [
            {'Part_Number': 'PN-ELEC-001', 'Description': 'Battery 12V 70Ah', 'Quantity': 1, 'Unit_Cost': 145.00}
        ],
        'Alternator': [
            {'Part_Number': 'PN-ELEC-010', 'Description': 'Alternator', 'Quantity': 1, 'Unit_Cost': 285.00},
            {'Part_Number': 'PN-ELEC-011', 'Description': 'Drive Belt', 'Quantity': 1, 'Unit_Cost': 35.00}
        ],
        'Tire': [
            {'Part_Number': 'PN-TIRE-001', 'Description': 'Tire 255/70R16', 'Quantity': 1, 'Unit_Cost': 175.00}
        ]
    }
    
    # Find matching parts based on component
    for key, parts in parts_database.items():
        if key.lower() in component.lower():
            bom_items.extend(parts)
            break
    
    # If no specific match, add generic items
    if not bom_items:
        bom_items = [
            {'Part_Number': 'PN-GEN-001', 'Description': f'{component} Component', 'Quantity': 1, 'Unit_Cost': 150.00},
            {'Part_Number': 'PN-GEN-002', 'Description': 'Hardware Kit', 'Quantity': 1, 'Unit_Cost': 25.00}
        ]
    
    # Add labor estimate
    labor_hours = 2.0
    if 'replace' in recommended_action.lower():
        if 'engine' in component.lower():
            labor_hours = 8.0
        elif 'transmission' in component.lower():
            labor_hours = 12.0
        elif any(word in component.lower() for word in ['pump', 'compressor', 'alternator']):
            labor_hours = 3.0
        else:
            labor_hours = 2.0
    
    # Create BOM DataFrame
    bom_df = pd.DataFrame(bom_items)
    bom_df['Line_Total'] = bom_df['Quantity'] * bom_df['Unit_Cost']
    
    # Calculate totals
    parts_total = bom_df['Line_Total'].sum()
    labor_cost = labor_hours * 85.00  # $85/hour labor rate
    total_cost = parts_total + labor_cost
    
    bom_summary = {
        'bom_items': bom_df,
        'labor_hours': labor_hours,
        'labor_cost': labor_cost,
        'parts_total': parts_total,
        'total_cost': total_cost,
        'failure_code': failure_code
    }
    
    return bom_summary

def init_data():
    """Initialize all data tables"""
    
    if 'data_initialized' in st.session_state and st.session_state.data_initialized:
        return
    
    # Load complete failure catalogue from Excel
    st.session_state.df_failure_catalogue = load_failure_catalogue_from_excel()
    
    # Show loading info
    if len(st.session_state.df_failure_catalogue) > 0:
        print(f"✅ Catalogue loaded successfully!")
        print(f"   - Total entries: {len(st.session_state.df_failure_catalogue)}")
        print(f"   - Sample systems: {st.session_state.df_failure_catalogue['System'].unique()[:5].tolist()}")
    else:
        print("⚠️ Warning: Catalogue is empty!")
    
    # Reference tables
    st.session_state.df_region = pd.DataFrame({
        'Region': ['Central', 'Eastern', 'Western', 'Northern', 'Southern']
    })
    
    st.session_state.df_workshop = pd.DataFrame({
        'Workshop_Name': ['Workshop Alpha', 'Workshop Beta', 'Workshop Gamma', 'Workshop Delta', 'Workshop Epsilon'],
        'Region': ['Central', 'Eastern', 'Western', 'Northern', 'Southern']
    })
    
    st.session_state.df_vehicle = pd.DataFrame({
        'Vehicle_Number': [f'VEH-{i:03d}' for i in range(1, 21)],
        'Vehicle_Type': (['MRAP', 'APC', 'Transport'] * 6 + ['MRAP', 'APC'])[:20],
        'Unit_Name': (['Unit 101'] * 5 + ['Unit 102'] * 5 + ['Unit 103'] * 5 + ['Unit 104'] * 5)[:20]
    })
    
    # Users
    st.session_state.users = {
        'Technician': {'name': 'Ali Al-Saud', 'workshop': 'Workshop Alpha', 'employee_id': 1},
        'Supervisor': {'name': 'Omar Al-Harbi', 'workshop': 'Workshop Alpha', 'employee_id': 2},
        'Manager': {'name': 'Nora Al-Dosari', 'workshop': None, 'employee_id': 6},
        'Inventory': {'name': 'Layla Al-Otaibi', 'workshop': None, 'employee_id': 4},
        'Procurement': {'name': 'Hassan Al-Shammari', 'workshop': None, 'employee_id': 5},
        'Admin': {'name': 'Admin User', 'workshop': None, 'employee_id': 8}
    }
    
    # Work orders
    st.session_state.df_work_orders = pd.DataFrame(columns=[
        'ID', 'Vehicle_Number', 'Workshop_Name', 'Malfunction_Date', 'Work_Order_Date',
        'System', 'Subsystem', 'Component', 'Failure_Mode', 'Failure_Code',
        'Cause_Code', 'Resolution_Code', 'Recommended_Action',
        'Status', 'Technician_Name', 'BOM_Generated', 'Comments'
    ])
    
    # Bill of Materials
    st.session_state.df_bom = pd.DataFrame(columns=[
        'BOM_ID', 'Work_Order_ID', 'Failure_Code', 'Part_Number', 'Description',
        'Quantity', 'Unit_Cost', 'Line_Total', 'Status', 'Created_Date'
    ])
    
    # Parts inventory
    st.session_state.df_parts = pd.DataFrame({
        'Part_Number': [f'PN-{i:05d}' for i in range(1, 101)],
        'Description': [f'Part Description {i}' for i in range(1, 101)],
        'Quantity_Available': np.random.randint(5, 100, 100),
        'Unit_Cost': np.random.uniform(10, 500, 100).round(2),
        'Location': [f'Rack-{chr(65 + i%5)}{i%10}' for i in range(100)]
    })
    
    # Counters
    st.session_state.wo_counter = 1
    st.session_state.bom_counter = 1
    
    st.session_state.data_initialized = True

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_cascading_options(system=None, subsystem=None, component=None):
    """Get cascading dropdown options"""
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
    return sorted(df['Failure Mode'].unique().tolist())

def get_failure_details(system, subsystem, component, failure_mode):
    """Get failure details from catalogue"""
    df = st.session_state.df_failure_catalogue
    result = df[
        (df['System'] == system) & 
        (df['Subsystem'] == subsystem) & 
        (df['Component'] == component) & 
        (df['Failure Mode'] == failure_mode)
    ]
    
    if not result.empty:
        row = result.iloc[0]
        return {
            'System': row['System'],
            'Subsystem': row['Subsystem'],
            'Component': row['Component'],
            'Failure Mode': row['Failure Mode'],
            'Recommended Action': row['Recommended Action'],
            'Failure Code': row['Failure Code'],
            'Cause Code': row['Cause Code'],
            'Resolution Code': row['Resolution Code']
        }
    return None

# ============================================================================
# ROLE SELECTION
# ============================================================================

def role_selection_page():
    """Role selection for demo"""
    st.title("🔧 AMIC MMS - Enhanced Demo")
    st.markdown("### Select Your Role")
    
    # Show catalogue loading status
    try:
        df_test = pd.read_excel('/mnt/user-data/uploads/FRACAS_FailureMode_Catalogue_v5_WithCodes.xlsx', 
                               sheet_name='FRACAS_FailureMode_Catalogue')
        st.success(f"✅ Excel File Found: {len(df_test)} failure modes ready to load")
    except Exception as e:
        st.error(f"⚠️ Could not read Excel file: {e}")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.info("""
        **✨ Enhanced Features:**
        - ✅ Complete 427 Failure Mode Catalogue
        - ✅ Automatic Bill of Materials Generation
        - ✅ Procurement Integration
        - ✅ All Systems & Components
        """)
        
        role = st.selectbox(
            "Select Role",
            ['Technician', 'Supervisor', 'Manager', 'Inventory', 'Procurement', 'Admin'],
            format_func=lambda x: f"{x} - {st.session_state.users[x]['name']}"
        )
        
        if st.button("🚀 Start Demo", use_container_width=True, type="primary"):
            user_info = st.session_state.users[role]
            st.session_state.logged_in = True
            st.session_state.current_user = {
                'Role': role,
                'Employee_First_Name': user_info['name'].split()[0],
                'Employee_Last_Name': user_info['name'].split()[1] if len(user_info['name'].split()) > 1 else '',
                'Employee_ID': user_info['employee_id'],
                'Workshop_Name': user_info['workshop']
            }
            st.rerun()

def change_role():
    """Change role"""
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.rerun()

# ============================================================================
# PAGES
# ============================================================================

def page_create_work_order():
    """Create work order with BOM generation"""
    st.title("➕ Create Work Order with BOM")
    
    # Show catalogue status
    catalogue = st.session_state.df_failure_catalogue
    if len(catalogue) == 0:
        st.error("⚠️ Failure catalogue is empty! Please check Excel file.")
        return
    
    st.success(f"✅ Failure Catalogue Loaded: {len(catalogue)} entries | {catalogue['System'].nunique()} systems | {catalogue['Subsystem'].nunique()} subsystems | {catalogue['Component'].nunique()} components")
    
    user = st.session_state.current_user
    
    with st.form("create_wo_form"):
        st.subheader("📋 Basic Information")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if user.get('Workshop_Name'):
                workshop = st.text_input("Workshop", value=user['Workshop_Name'], disabled=True)
            else:
                workshop = st.selectbox("Workshop *", st.session_state.df_workshop['Workshop_Name'].tolist())
        
        with col2:
            vehicle = st.selectbox("Vehicle *", st.session_state.df_vehicle['Vehicle_Number'].tolist())
        
        with col3:
            malfunction_date = st.date_input("Malfunction Date *", datetime.now())
        
        # Cascading dropdowns
        st.markdown("---")
        st.subheader("🔧 Fault Classification")
        st.caption(f"**Total Failure Modes Available: {len(st.session_state.df_failure_catalogue)}**")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            systems = get_cascading_options()
            selected_system = st.selectbox(f"System * ({len(systems)} options)", [''] + systems)
        
        with col2:
            subsystems = get_cascading_options(selected_system) if selected_system else []
            selected_subsystem = st.selectbox(f"Subsystem * ({len(subsystems)} options)", [''] + subsystems)
        
        with col3:
            components = get_cascading_options(selected_system, selected_subsystem) if selected_subsystem else []
            selected_component = st.selectbox(f"Component * ({len(components)} options)", [''] + components)
        
        with col4:
            failure_modes = get_cascading_options(selected_system, selected_subsystem, selected_component) if selected_component else []
            selected_failure = st.selectbox(f"Failure Mode * ({len(failure_modes)} options)", [''] + failure_modes)
        
        # Auto-populated codes
        failure_details = None
        bom_preview = None
        
        if selected_system and selected_subsystem and selected_component and selected_failure:
            failure_details = get_failure_details(selected_system, selected_subsystem, selected_component, selected_failure)
            
            if failure_details:
                st.markdown("---")
                st.subheader("✨ Auto-Generated Information")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.text_input("Failure Code", value=failure_details['Failure Code'], disabled=True)
                with col2:
                    st.text_input("Cause Code", value=failure_details['Cause Code'], disabled=True)
                with col3:
                    st.text_input("Resolution Code", value=failure_details['Resolution Code'], disabled=True)
                
                st.markdown("**📝 Recommended Action:**")
                st.info(failure_details['Recommended Action'])
                
                # Generate BOM preview
                st.markdown("---")
                st.subheader("🔩 Bill of Materials Preview")
                bom_preview = generate_bom_for_failure(
                    failure_details['Failure Code'],
                    failure_details['Failure Mode'],
                    selected_component,
                    failure_details['Recommended Action']
                )
                
                st.dataframe(
                    bom_preview['bom_items'],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        'Unit_Cost': st.column_config.NumberColumn('Unit Cost', format='$%.2f'),
                        'Line_Total': st.column_config.NumberColumn('Line Total', format='$%.2f')
                    }
                )
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Parts Total", f"${bom_preview['parts_total']:,.2f}")
                with col2:
                    st.metric("Labor Hours", f"{bom_preview['labor_hours']:.1f} hrs")
                with col3:
                    st.metric("Labor Cost", f"${bom_preview['labor_cost']:,.2f}")
                with col4:
                    st.metric("Total Estimate", f"${bom_preview['total_cost']:,.2f}", 
                             delta="Parts + Labor")
        
        # Additional details
        st.markdown("---")
        comments = st.text_area("Comments", height=100)
        
        # Submit
        submitted = st.form_submit_button("🚀 Create Work Order & Generate BOM", 
                                         use_container_width=True, type="primary")
        
        if submitted:
            if not vehicle or not selected_system or not selected_subsystem or not selected_component or not selected_failure:
                st.error("❌ Please complete all required fields")
            elif not failure_details:
                st.error("❌ Invalid fault classification")
            else:
                # Create work order
                wo_id = st.session_state.wo_counter
                
                new_wo = pd.DataFrame([{
                    'ID': wo_id,
                    'Vehicle_Number': vehicle,
                    'Workshop_Name': workshop,
                    'Malfunction_Date': malfunction_date.strftime('%Y-%m-%d'),
                    'Work_Order_Date': datetime.now().strftime('%Y-%m-%d'),
                    'System': selected_system,
                    'Subsystem': selected_subsystem,
                    'Component': selected_component,
                    'Failure_Mode': selected_failure,
                    'Failure_Code': failure_details['Failure Code'],
                    'Cause_Code': failure_details['Cause Code'],
                    'Resolution_Code': failure_details['Resolution Code'],
                    'Recommended_Action': failure_details['Recommended Action'],
                    'Status': 'Open',
                    'Technician_Name': f"{user['Employee_First_Name']} {user['Employee_Last_Name']}",
                    'BOM_Generated': True,
                    'Comments': comments
                }])
                
                st.session_state.df_work_orders = pd.concat([
                    st.session_state.df_work_orders, new_wo
                ], ignore_index=True)
                
                # Save BOM
                bom_id = st.session_state.bom_counter
                for idx, item in bom_preview['bom_items'].iterrows():
                    new_bom = pd.DataFrame([{
                        'BOM_ID': bom_id,
                        'Work_Order_ID': wo_id,
                        'Failure_Code': failure_details['Failure Code'],
                        'Part_Number': item['Part_Number'],
                        'Description': item['Description'],
                        'Quantity': item['Quantity'],
                        'Unit_Cost': item['Unit_Cost'],
                        'Line_Total': item['Line_Total'],
                        'Status': 'Pending',
                        'Created_Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }])
                    
                    st.session_state.df_bom = pd.concat([
                        st.session_state.df_bom, new_bom
                    ], ignore_index=True)
                    
                    bom_id += 1
                
                st.session_state.wo_counter += 1
                st.session_state.bom_counter = bom_id
                
                st.success(f"✅ Work Order **WO-{wo_id:05d}** created with Bill of Materials!")
                st.balloons()
                
                # Summary
                with st.expander("📋 Summary", expanded=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Work Order:** WO-{wo_id:05d}")
                        st.markdown(f"**Vehicle:** {vehicle}")
                        st.markdown(f"**System:** {selected_system}")
                        st.markdown(f"**Component:** {selected_component}")
                        st.markdown(f"**Failure Code:** {failure_details['Failure Code']}")
                    with col2:
                        st.markdown(f"**BOM Items:** {len(bom_preview['bom_items'])}")
                        st.markdown(f"**Parts Cost:** ${bom_preview['parts_total']:,.2f}")
                        st.markdown(f"**Labor Cost:** ${bom_preview['labor_cost']:,.2f}")
                        st.markdown(f"**Total:** ${bom_preview['total_cost']:,.2f}")
                        st.markdown("**Status:** BOM Sent to Procurement")

def page_dashboard():
    """Dashboard"""
    st.title("📊 Dashboard")
    
    # Catalogue stats
    catalogue_stats = st.session_state.df_failure_catalogue
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Failure Modes", len(catalogue_stats))
    with col2:
        st.metric("Systems", catalogue_stats['System'].nunique())
    with col3:
        st.metric("Subsystems", catalogue_stats['Subsystem'].nunique())
    with col4:
        st.metric("Components", catalogue_stats['Component'].nunique())
    
    st.markdown("---")
    
    # Work orders
    df_wo = st.session_state.df_work_orders
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Work Orders", len(df_wo))
    with col2:
        st.metric("Open", len(df_wo[df_wo['Status'] == 'Open']))
    with col3:
        st.metric("With BOM", len(df_wo[df_wo['BOM_Generated'] == True]))
    with col4:
        total_bom_value = st.session_state.df_bom['Line_Total'].sum()
        st.metric("BOM Total Value", f"${total_bom_value:,.2f}")
    
    # System breakdown
    if not catalogue_stats.empty:
        st.markdown("---")
        st.subheader("Failure Modes by System")
        system_counts = catalogue_stats['System'].value_counts()
        st.bar_chart(system_counts)
    
    # Recent work orders
    if not df_wo.empty:
        st.markdown("---")
        st.subheader("Recent Work Orders")
        st.dataframe(
            df_wo[['ID', 'Vehicle_Number', 'System', 'Component', 'Failure_Code', 'Status', 'BOM_Generated']].tail(10),
            use_container_width=True,
            hide_index=True
        )

def page_procurement():
    """Procurement page with BOMs"""
    st.title("💼 Procurement - Bill of Materials")
    
    df_bom = st.session_state.df_bom
    
    if df_bom.empty:
        st.info("No Bills of Materials generated yet. Create a work order to generate BOM.")
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total BOMs", df_bom['BOM_ID'].nunique())
    with col2:
        st.metric("Total Items", len(df_bom))
    with col3:
        st.metric("Total Value", f"${df_bom['Line_Total'].sum():,.2f}")
    with col4:
        pending = len(df_bom[df_bom['Status'] == 'Pending'])
        st.metric("Pending Items", pending)
    
    st.markdown("---")
    
    # Group by BOM
    st.subheader("Bills of Materials")
    
    for bom_id in df_bom['BOM_ID'].unique():
        bom_items = df_bom[df_bom['BOM_ID'] == bom_id]
        wo_id = bom_items.iloc[0]['Work_Order_ID']
        total = bom_items['Line_Total'].sum()
        
        with st.expander(f"BOM-{bom_id:05d} - Work Order {wo_id} - Total: ${total:,.2f}"):
            st.dataframe(
                bom_items[['Part_Number', 'Description', 'Quantity', 'Unit_Cost', 'Line_Total', 'Status']],
                use_container_width=True,
                hide_index=True,
                column_config={
                    'Unit_Cost': st.column_config.NumberColumn('Unit Cost', format='$%.2f'),
                    'Line_Total': st.column_config.NumberColumn('Line Total', format='$%.2f')
                }
            )
            
            if st.button(f"✅ Approve BOM-{bom_id:05d}", key=f"approve_{bom_id}"):
                st.session_state.df_bom.loc[
                    st.session_state.df_bom['BOM_ID'] == bom_id, 'Status'
                ] = 'Approved'
                st.success("BOM Approved!")
                st.rerun()

def page_catalogue():
    """View complete catalogue"""
    st.title("📚 Failure Mode Catalogue")
    
    df = st.session_state.df_failure_catalogue
    
    st.info(f"**Total Entries:** {len(df)} failure modes across {df['System'].nunique()} systems")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        system_filter = st.selectbox("Filter by System", ['All'] + sorted(df['System'].unique().tolist()))
    with col2:
        if system_filter != 'All':
            subsystems = sorted(df[df['System'] == system_filter]['Subsystem'].unique().tolist())
            subsystem_filter = st.selectbox("Filter by Subsystem", ['All'] + subsystems)
        else:
            subsystem_filter = 'All'
    
    # Apply filters
    filtered = df.copy()
    if system_filter != 'All':
        filtered = filtered[filtered['System'] == system_filter]
    if subsystem_filter != 'All':
        filtered = filtered[filtered['Subsystem'] == subsystem_filter]
    
    st.markdown(f"**Showing:** {len(filtered)} entries")
    
    # Display
    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True
    )

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application"""
    
    init_data()
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        role_selection_page()
        return
    
    user = st.session_state.current_user
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🔧 AMIC MMS - Enhanced")
        st.caption(f"**{user['Employee_First_Name']} {user['Employee_Last_Name']}** - {user['Role']}")
    with col2:
        if st.button("🔄 Change Role", use_container_width=True):
            change_role()
    
    st.markdown("---")
    
    # Navigation
    if user['Role'] in ['Technician', 'Supervisor']:
        selected = st.radio(
            "Navigation",
            ['📊 Dashboard', '➕ Create Work Order'],
            horizontal=True
        )
        
        if '📊 Dashboard' in selected:
            page_dashboard()
        else:
            page_create_work_order()
    
    elif user['Role'] == 'Procurement':
        selected = st.radio(
            "Navigation",
            ['📊 Dashboard', '💼 Procurement BOMs'],
            horizontal=True
        )
        
        if '💼 Procurement' in selected:
            page_procurement()
        else:
            page_dashboard()
    
    elif user['Role'] == 'Admin':
        selected = st.radio(
            "Navigation",
            ['📊 Dashboard', '📚 Failure Catalogue'],
            horizontal=True
        )
        
        if '📚 Failure' in selected:
            page_catalogue()
        else:
            page_dashboard()
    
    else:
        page_dashboard()

if __name__ == "__main__":
    main()
