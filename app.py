"""
AMIC Work Order Management & FRACAS System - ENHANCED VERSION (WHITE THEME)
Advanced dashboards, analytics, KPIs, and insights
✅ COMPLETE CATALOGUE - All 427 fault classifications from Excel imported
Light/White background theme
FIXED VERSION - Corrected Altair chart syntax
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
    page_title="AMIC FRACAS System Enhanced - Full Catalogue",
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
# HARD-CODED CATALOGUE HIERARCHY - COMPLETE FROM EXCEL (427 ENTRIES)
# ============================================================================

CATALOGUE_HIERARCHY = {
    "HVAC": {
        "Air Conditioning": {
            "Compressor": {
                "Mechanical seizure": {
                    "failure_code": "HVAC-AC-001",
                    "cause_code": "HVAC-AC-C001",
                    "resolution_code": "HVAC-AC-R001",
                    "recommended_action": "Replace compressor; Replace clutch; Flush circuit; Replace filter/drier; Vacuum & recharge to spec; Verify oil quantity; Performance test"
                },
                "Insufficient displacement": {
                    "failure_code": "NAN-NAN-001",
                    "cause_code": "NAN-NAN-C001",
                    "resolution_code": "NAN-NAN-R001",
                    "recommended_action": "Replace compressor; Replace clutch; Flush circuit; Replace filter/drier; Vacuum & recharge to spec; Verify oil quantity; Performance test"
                },
                "Internal wear/contamination": {
                    "failure_code": "NAN-NAN-002",
                    "cause_code": "NAN-NAN-C002",
                    "resolution_code": "NAN-NAN-R002",
                    "recommended_action": "Replace compressor; Replace clutch; Flush circuit; Replace filter/drier; Vacuum & recharge to spec; Verify oil quantity; Performance test"
                },
                "Shaft seal leak": {
                    "failure_code": "NAN-NAN-003",
                    "cause_code": "NAN-NAN-C003",
                    "resolution_code": "NAN-NAN-R003",
                    "recommended_action": "Replace compressor; Replace clutch; Flush circuit; Replace filter/drier; Vacuum & recharge to spec; Verify oil quantity; Performance test"
                },
                "Clutch coil open": {
                    "failure_code": "NAN-NAN-004",
                    "cause_code": "NAN-NAN-C004",
                    "resolution_code": "NAN-NAN-R004",
                    "recommended_action": "Replace compressor; Replace clutch; Flush circuit; Replace filter/drier; Vacuum & recharge to spec; Verify oil quantity; Performance test"
                },
                "Clutch slipping": {
                    "failure_code": "NAN-NAN-005",
                    "cause_code": "NAN-NAN-C005",
                    "resolution_code": "NAN-NAN-R005",
                    "recommended_action": "Replace compressor; Replace clutch; Flush circuit; Replace filter/drier; Vacuum & recharge to spec; Verify oil quantity; Performance test"
                },
                "Overheat due to low refrigerant": {
                    "failure_code": "NAN-NAN-006",
                    "cause_code": "NAN-NAN-C006",
                    "resolution_code": "NAN-NAN-R006",
                    "recommended_action": "Replace compressor; Replace clutch; Flush circuit; Replace filter/drier; Vacuum & recharge to spec; Verify oil quantity; Performance test"
                },
                "Overcharge condition": {
                    "failure_code": "NAN-NAN-007",
                    "cause_code": "NAN-NAN-C007",
                    "resolution_code": "NAN-NAN-R007",
                    "recommended_action": "Replace compressor; Replace clutch; Flush circuit; Replace filter/drier; Vacuum & recharge to spec; Verify oil quantity; Performance test"
                },
                "Oil starvation": {
                    "failure_code": "NAN-NAN-008",
                    "cause_code": "NAN-NAN-C008",
                    "resolution_code": "NAN-NAN-R008",
                    "recommended_action": "Replace compressor; Replace clutch; Flush circuit; Replace filter/drier; Vacuum & recharge to spec; Verify oil quantity; Performance test"
                }
            },
            "Condenser": {
                "Leak at tubes": {
                    "failure_code": "NAN-NAN-009",
                    "cause_code": "NAN-NAN-C009",
                    "resolution_code": "NAN-NAN-R009",
                    "recommended_action": "Replace condenser; Clean fins; Leak test; Vacuum & recharge"
                },
                "Leak at header": {
                    "failure_code": "NAN-NAN-010",
                    "cause_code": "NAN-NAN-C010",
                    "resolution_code": "NAN-NAN-R010",
                    "recommended_action": "Replace condenser; Clean fins; Leak test; Vacuum & recharge"
                },
                "Fin blockage (debris)": {
                    "failure_code": "NAN-NAN-011",
                    "cause_code": "NAN-NAN-C011",
                    "resolution_code": "NAN-NAN-R011",
                    "recommended_action": "Replace condenser; Clean fins; Leak test; Vacuum & recharge"
                },
                "Impact damage": {
                    "failure_code": "NAN-NAN-012",
                    "cause_code": "NAN-NAN-C012",
                    "resolution_code": "NAN-NAN-R012",
                    "recommended_action": "Replace condenser; Clean fins; Leak test; Vacuum & recharge"
                },
                "Internal restriction": {
                    "failure_code": "NAN-NAN-013",
                    "cause_code": "NAN-NAN-C013",
                    "resolution_code": "NAN-NAN-R013",
                    "recommended_action": "Replace condenser; Clean fins; Leak test; Vacuum & recharge"
                }
            },
            "Evaporator": {
                "Leak (core corrosion)": {
                    "failure_code": "NAN-NAN-014",
                    "cause_code": "NAN-NAN-C014",
                    "resolution_code": "NAN-NAN-R014",
                    "recommended_action": "Replace evaporator; Clear drain; Verify TXV operation; Recharge"
                },
                "Freeze-up": {
                    "failure_code": "NAN-NAN-015",
                    "cause_code": "NAN-NAN-C015",
                    "resolution_code": "NAN-NAN-R015",
                    "recommended_action": "Replace evaporator; Clear drain; Verify TXV operation; Recharge"
                },
                "Internal blockage": {
                    "failure_code": "NAN-NAN-016",
                    "cause_code": "NAN-NAN-C016",
                    "resolution_code": "NAN-NAN-R016",
                    "recommended_action": "Replace evaporator; Clear drain; Verify TXV operation; Recharge"
                },
                "Sensor misplacement": {
                    "failure_code": "NAN-NAN-017",
                    "cause_code": "NAN-NAN-C017",
                    "resolution_code": "NAN-NAN-R017",
                    "recommended_action": "Replace evaporator; Clear drain; Verify TXV operation; Recharge"
                },
                "Drain blocked": {
                    "failure_code": "NAN-NAN-018",
                    "cause_code": "NAN-NAN-C018",
                    "resolution_code": "NAN-NAN-R018",
                    "recommended_action": "Replace evaporator; Clear drain; Verify TXV operation; Recharge"
                }
            },
            "TXV/Orifice": {
                "Stuck closed": {
                    "failure_code": "NAN-NAN-019",
                    "cause_code": "NAN-NAN-C019",
                    "resolution_code": "NAN-NAN-R019",
                    "recommended_action": "Replace TXV/orifice; Flush system; Replace drier; Recharge"
                },
                "Stuck open": {
                    "failure_code": "NAN-NAN-020",
                    "cause_code": "NAN-NAN-C020",
                    "resolution_code": "NAN-NAN-R020",
                    "recommended_action": "Replace TXV/orifice; Flush system; Replace drier; Recharge"
                },
                "Debris blockage": {
                    "failure_code": "NAN-NAN-021",
                    "cause_code": "NAN-NAN-C021",
                    "resolution_code": "NAN-NAN-R021",
                    "recommended_action": "Replace TXV/orifice; Flush system; Replace drier; Recharge"
                },
                "Incorrect size": {
                    "failure_code": "NAN-NAN-022",
                    "cause_code": "NAN-NAN-C022",
                    "resolution_code": "NAN-NAN-R022",
                    "recommended_action": "Replace TXV/orifice; Flush system; Replace drier; Recharge"
                }
            },
            "Hoses/Pipes": {
                "Leak at crimp": {
                    "failure_code": "NAN-NAN-023",
                    "cause_code": "NAN-NAN-C023",
                    "resolution_code": "NAN-NAN-R023",
                    "recommended_action": "Replace hose/pipe; Replace O-rings; Leak test; Recharge"
                },
                "Service port leak": {
                    "failure_code": "NAN-NAN-024",
                    "cause_code": "NAN-NAN-C024",
                    "resolution_code": "NAN-NAN-R024",
                    "recommended_action": "Replace hose/pipe; Replace O-rings; Leak test; Recharge"
                },
                "O-ring damage": {
                    "failure_code": "NAN-NAN-025",
                    "cause_code": "NAN-NAN-C025",
                    "resolution_code": "NAN-NAN-R025",
                    "recommended_action": "Replace hose/pipe; Replace O-rings; Leak test; Recharge"
                },
                "Chafing wear-through": {
                    "failure_code": "NAN-NAN-026",
                    "cause_code": "NAN-NAN-C026",
                    "resolution_code": "NAN-NAN-R026",
                    "recommended_action": "Replace hose/pipe; Replace O-rings; Leak test; Recharge"
                }
            },
            "Blower Motor": {
                "Motor burnt": {
                    "failure_code": "NAN-NAN-027",
                    "cause_code": "NAN-NAN-C027",
                    "resolution_code": "NAN-NAN-R027",
                    "recommended_action": "Replace blower motor; Inspect resistor/driver; Verify airflow"
                },
                "Brush wear": {
                    "failure_code": "NAN-NAN-028",
                    "cause_code": "NAN-NAN-C028",
                    "resolution_code": "NAN-NAN-R028",
                    "recommended_action": "Replace blower motor; Inspect resistor/driver; Verify airflow"
                },
                "Bearing noise": {
                    "failure_code": "NAN-NAN-029",
                    "cause_code": "NAN-NAN-C029",
                    "resolution_code": "NAN-NAN-R029",
                    "recommended_action": "Replace blower motor; Inspect resistor/driver; Verify airflow"
                },
                "Open circuit": {
                    "failure_code": "NAN-NAN-030",
                    "cause_code": "NAN-NAN-C030",
                    "resolution_code": "NAN-NAN-R030",
                    "recommended_action": "Replace blower motor; Inspect resistor/driver; Verify airflow"
                }
            },
            "Blower Resistor/Driver": {
                "Open resistor": {
                    "failure_code": "NAN-NAN-031",
                    "cause_code": "NAN-NAN-C031",
                    "resolution_code": "NAN-NAN-R031",
                    "recommended_action": "Replace resistor/driver; Inspect blower current"
                },
                "Thermal fuse open": {
                    "failure_code": "NAN-NAN-032",
                    "cause_code": "NAN-NAN-C032",
                    "resolution_code": "NAN-NAN-R032",
                    "recommended_action": "Replace resistor/driver; Inspect blower current"
                },
                "Driver short": {
                    "failure_code": "NAN-NAN-033",
                    "cause_code": "NAN-NAN-C033",
                    "resolution_code": "NAN-NAN-R033",
                    "recommended_action": "Replace resistor/driver; Inspect blower current"
                }
            },
            "Controls/Actuators": {
                "Blend door actuator faulty": {
                    "failure_code": "NAN-NAN-034",
                    "cause_code": "NAN-NAN-C034",
                    "resolution_code": "NAN-NAN-R034",
                    "recommended_action": "Replace actuator; Repair/replace control panel; Relearn calibration"
                },
                "Mode actuator stuck": {
                    "failure_code": "NAN-NAN-035",
                    "cause_code": "NAN-NAN-C035",
                    "resolution_code": "NAN-NAN-R035",
                    "recommended_action": "Replace actuator; Repair/replace control panel; Relearn calibration"
                },
                "Panel control fault": {
                    "failure_code": "NAN-NAN-036",
                    "cause_code": "NAN-NAN-C036",
                    "resolution_code": "NAN-NAN-R036",
                    "recommended_action": "Replace actuator; Repair/replace control panel; Relearn calibration"
                },
                "Temp sensor fault": {
                    "failure_code": "NAN-NAN-037",
                    "cause_code": "NAN-NAN-C037",
                    "resolution_code": "NAN-NAN-R037",
                    "recommended_action": "Replace actuator; Repair/replace control panel; Relearn calibration"
                }
            },
            "Cabin Filter": {
                "Clogged": {
                    "failure_code": "NAN-NAN-038",
                    "cause_code": "NAN-NAN-C038",
                    "resolution_code": "NAN-NAN-R038",
                    "recommended_action": "Replace filter; Verify orientation"
                },
                "Incorrect fitment": {
                    "failure_code": "NAN-NAN-039",
                    "cause_code": "NAN-NAN-C039",
                    "resolution_code": "NAN-NAN-R039",
                    "recommended_action": "Replace filter; Verify orientation"
                }
            }
        },
        "Heating": {
            "Heater Core": {
                "Leak (core)": {
                    "failure_code": "NAN-HEAT-001",
                    "cause_code": "NAN-HEAT-C001",
                    "resolution_code": "NAN-HEAT-R001",
                    "recommended_action": "Replace heater core; Flush circuit; Bleed system"
                },
                "Internal blockage": {
                    "failure_code": "NAN-NAN-040",
                    "cause_code": "NAN-NAN-C040",
                    "resolution_code": "NAN-NAN-R040",
                    "recommended_action": "Replace heater core; Flush circuit; Bleed system"
                },
                "Airlock": {
                    "failure_code": "NAN-NAN-041",
                    "cause_code": "NAN-NAN-C041",
                    "resolution_code": "NAN-NAN-R041",
                    "recommended_action": "Replace heater core; Flush circuit; Bleed system"
                }
            },
            "Heater Valve": {
                "Valve stuck closed": {
                    "failure_code": "NAN-NAN-042",
                    "cause_code": "NAN-NAN-C042",
                    "resolution_code": "NAN-NAN-R042",
                    "recommended_action": "Replace/repair valve; Repair control"
                },
                "Valve stuck open": {
                    "failure_code": "NAN-NAN-043",
                    "cause_code": "NAN-NAN-C043",
                    "resolution_code": "NAN-NAN-R043",
                    "recommended_action": "Replace/repair valve; Repair control"
                },
                "Vacuum/electrical fault": {
                    "failure_code": "NAN-NAN-044",
                    "cause_code": "NAN-NAN-C044",
                    "resolution_code": "NAN-NAN-R044",
                    "recommended_action": "Replace/repair valve; Repair control"
                }
            }
        }
    },
    "Engine": {
        "Air Intake System": {
            "Air Filter/Box": {
                "Filter clogged": {
                    "failure_code": "ENG-AIR-001",
                    "cause_code": "ENG-AIR-C001",
                    "resolution_code": "ENG-AIR-R001",
                    "recommended_action": "Replace filter; Repair/replace airbox; Clean/replace MAF"
                },
                "Box cracked/leaking": {
                    "failure_code": "NAN-NAN-045",
                    "cause_code": "NAN-NAN-C045",
                    "resolution_code": "NAN-NAN-R045",
                    "recommended_action": "Replace filter; Repair/replace airbox; Clean/replace MAF"
                },
                "MAF contamination": {
                    "failure_code": "NAN-NAN-046",
                    "cause_code": "NAN-NAN-C046",
                    "resolution_code": "NAN-NAN-R046",
                    "recommended_action": "Replace filter; Repair/replace airbox; Clean/replace MAF"
                }
            },
            "Throttle Body": {
                "Carbon buildup": {
                    "failure_code": "NAN-NAN-047",
                    "cause_code": "NAN-NAN-C047",
                    "resolution_code": "NAN-NAN-R047",
                    "recommended_action": "Clean throttle body; Replace throttle body; Relearn idle"
                },
                "Actuator failure": {
                    "failure_code": "NAN-NAN-048",
                    "cause_code": "NAN-NAN-C048",
                    "resolution_code": "NAN-NAN-R048",
                    "recommended_action": "Clean throttle body; Replace throttle body; Relearn idle"
                },
                "TPS sensor fault": {
                    "failure_code": "NAN-NAN-049",
                    "cause_code": "NAN-NAN-C049",
                    "resolution_code": "NAN-NAN-R049",
                    "recommended_action": "Clean throttle body; Replace throttle body; Relearn idle"
                }
            },
            "Intake Manifold": {
                "Gasket leak": {
                    "failure_code": "NAN-NAN-050",
                    "cause_code": "NAN-NAN-C050",
                    "resolution_code": "NAN-NAN-R050",
                    "recommended_action": "Replace gasket; Replace manifold; Torque to spec"
                },
                "Cracked manifold": {
                    "failure_code": "NAN-NAN-051",
                    "cause_code": "NAN-NAN-C051",
                    "resolution_code": "NAN-NAN-R051",
                    "recommended_action": "Replace gasket; Replace manifold; Torque to spec"
                },
                "Loose bolts": {
                    "failure_code": "NAN-NAN-052",
                    "cause_code": "NAN-NAN-C052",
                    "resolution_code": "NAN-NAN-R052",
                    "recommended_action": "Replace gasket; Replace manifold; Torque to spec"
                }
            }
        },
        "Fuel System": {
            "Fuel Pump": {
                "Pump worn": {
                    "failure_code": "NAN-FUEL-001",
                    "cause_code": "NAN-FUEL-C001",
                    "resolution_code": "NAN-FUEL-R001",
                    "recommended_action": "Replace pump module; Repair wiring/connector; Check pickup; Verify fuel quality"
                },
                "Electrical connection fault": {
                    "failure_code": "NAN-NAN-053",
                    "cause_code": "NAN-NAN-C053",
                    "resolution_code": "NAN-NAN-R053",
                    "recommended_action": "Replace pump module; Repair wiring/connector; Check pickup; Verify fuel quality"
                },
                "Fuel starvation": {
                    "failure_code": "NAN-NAN-054",
                    "cause_code": "NAN-NAN-C054",
                    "resolution_code": "NAN-NAN-R054",
                    "recommended_action": "Replace pump module; Repair wiring/connector; Check pickup; Verify fuel quality"
                },
                "Overheat": {
                    "failure_code": "NAN-NAN-055",
                    "cause_code": "NAN-NAN-C055",
                    "resolution_code": "NAN-NAN-R055",
                    "recommended_action": "Replace pump module; Repair wiring/connector; Check pickup; Verify fuel quality"
                }
            },
            "Injectors": {
                "Stuck closed": {
                    "failure_code": "NAN-NAN-056",
                    "cause_code": "NAN-NAN-C056",
                    "resolution_code": "NAN-NAN-R056",
                    "recommended_action": "Clean injectors; Replace injector(s); Replace seals"
                },
                "Leaking": {
                    "failure_code": "NAN-NAN-057",
                    "cause_code": "NAN-NAN-C057",
                    "resolution_code": "NAN-NAN-R057",
                    "recommended_action": "Clean injectors; Replace injector(s); Replace seals"
                },
                "Poor spray": {
                    "failure_code": "NAN-NAN-058",
                    "cause_code": "NAN-NAN-C058",
                    "resolution_code": "NAN-NAN-R058",
                    "recommended_action": "Clean injectors; Replace injector(s); Replace seals"
                },
                "O-ring leak": {
                    "failure_code": "NAN-NAN-059",
                    "cause_code": "NAN-NAN-C059",
                    "resolution_code": "NAN-NAN-R059",
                    "recommended_action": "Clean injectors; Replace injector(s); Replace seals"
                }
            },
            "Fuel Rail/Lines": {
                "Leak at connection": {
                    "failure_code": "NAN-NAN-060",
                    "cause_code": "NAN-NAN-C060",
                    "resolution_code": "NAN-NAN-R060",
                    "recommended_action": "Repair/replace line; Replace regulator; Replace filter"
                },
                "Regulator fault": {
                    "failure_code": "NAN-NAN-061",
                    "cause_code": "NAN-NAN-C061",
                    "resolution_code": "NAN-NAN-R061",
                    "recommended_action": "Repair/replace line; Replace regulator; Replace filter"
                },
                "Line restriction": {
                    "failure_code": "NAN-NAN-062",
                    "cause_code": "NAN-NAN-C062",
                    "resolution_code": "NAN-NAN-R062",
                    "recommended_action": "Repair/replace line; Replace regulator; Replace filter"
                },
                "Corrosion": {
                    "failure_code": "NAN-NAN-063",
                    "cause_code": "NAN-NAN-C063",
                    "resolution_code": "NAN-NAN-R063",
                    "recommended_action": "Repair/replace line; Replace regulator; Replace filter"
                }
            },
            "Fuel Tank": {
                "Leak": {
                    "failure_code": "NAN-NAN-064",
                    "cause_code": "NAN-NAN-C064",
                    "resolution_code": "NAN-NAN-R064",
                    "recommended_action": "Repair/replace tank; Clean/flush; Replace cap/vent"
                },
                "Vent blockage": {
                    "failure_code": "NAN-NAN-065",
                    "cause_code": "NAN-NAN-C065",
                    "resolution_code": "NAN-NAN-R065",
                    "recommended_action": "Repair/replace tank; Clean/flush; Replace cap/vent"
                },
                "Deformation": {
                    "failure_code": "NAN-NAN-066",
                    "cause_code": "NAN-NAN-C066",
                    "resolution_code": "NAN-NAN-R066",
                    "recommended_action": "Repair/replace tank; Clean/flush; Replace cap/vent"
                },
                "Contamination": {
                    "failure_code": "NAN-NAN-067",
                    "cause_code": "NAN-NAN-C067",
                    "resolution_code": "NAN-NAN-R067",
                    "recommended_action": "Repair/replace tank; Clean/flush; Replace cap/vent"
                }
            }
        },
        "Ignition": {
            "Coils": {
                "Internal short": {
                    "failure_code": "NAN-IGN-001",
                    "cause_code": "NAN-IGN-C001",
                    "resolution_code": "NAN-IGN-R001",
                    "recommended_action": "Replace coil; Repair connector"
                },
                "Open circuit": {
                    "failure_code": "NAN-NAN-068",
                    "cause_code": "NAN-NAN-C068",
                    "resolution_code": "NAN-NAN-R068",
                    "recommended_action": "Replace coil; Repair connector"
                },
                "Connector corrosion": {
                    "failure_code": "NAN-NAN-069",
                    "cause_code": "NAN-NAN-C069",
                    "resolution_code": "NAN-NAN-R069",
                    "recommended_action": "Replace coil; Repair connector"
                }
            },
            "Spark Plugs": {
                "Excessive gap": {
                    "failure_code": "NAN-NAN-070",
                    "cause_code": "NAN-NAN-C070",
                    "resolution_code": "NAN-NAN-R070",
                    "recommended_action": "Replace plugs; Adjust gap"
                },
                "Fouled": {
                    "failure_code": "NAN-NAN-071",
                    "cause_code": "NAN-NAN-C071",
                    "resolution_code": "NAN-NAN-R071",
                    "recommended_action": "Replace plugs; Adjust gap"
                },
                "Cracked insulator": {
                    "failure_code": "NAN-NAN-072",
                    "cause_code": "NAN-NAN-C072",
                    "resolution_code": "NAN-NAN-R072",
                    "recommended_action": "Replace plugs; Adjust gap"
                }
            },
            "Crank/Cam Sensors": {
                "Signal dropout": {
                    "failure_code": "NAN-NAN-073",
                    "cause_code": "NAN-NAN-C073",
                    "resolution_code": "NAN-NAN-R073",
                    "recommended_action": "Replace sensor; Repair wiring; Realign"
                },
                "Wiring open": {
                    "failure_code": "NAN-NAN-074",
                    "cause_code": "NAN-NAN-C074",
                    "resolution_code": "NAN-NAN-R074",
                    "recommended_action": "Replace sensor; Repair wiring; Realign"
                },
                "Misaligned mount": {
                    "failure_code": "NAN-NAN-075",
                    "cause_code": "NAN-NAN-C075",
                    "resolution_code": "NAN-NAN-R075",
                    "recommended_action": "Replace sensor; Repair wiring; Realign"
                }
            }
        },
        "Lubrication": {
            "Oil Pump": {
                "Pump wear": {
                    "failure_code": "NAN-LUB-001",
                    "cause_code": "NAN-LUB-C001",
                    "resolution_code": "NAN-LUB-R001",
                    "recommended_action": "Replace pump; Clean pickup"
                },
                "Pickup clogged": {
                    "failure_code": "NAN-NAN-076",
                    "cause_code": "NAN-NAN-C076",
                    "resolution_code": "NAN-NAN-R076",
                    "recommended_action": "Replace pump; Clean pickup"
                },
                "Relief valve stuck": {
                    "failure_code": "NAN-NAN-077",
                    "cause_code": "NAN-NAN-C077",
                    "resolution_code": "NAN-NAN-R077",
                    "recommended_action": "Replace pump; Clean pickup"
                }
            },
            "Oil Filter": {
                "Bypass stuck open": {
                    "failure_code": "NAN-NAN-078",
                    "cause_code": "NAN-NAN-C078",
                    "resolution_code": "NAN-NAN-R078",
                    "recommended_action": "Replace filter; Inspect housing"
                },
                "Clogged element": {
                    "failure_code": "NAN-NAN-079",
                    "cause_code": "NAN-NAN-C079",
                    "resolution_code": "NAN-NAN-R079",
                    "recommended_action": "Replace filter; Inspect housing"
                },
                "Seal leak": {
                    "failure_code": "NAN-NAN-080",
                    "cause_code": "NAN-NAN-C080",
                    "resolution_code": "NAN-NAN-R080",
                    "recommended_action": "Replace filter; Inspect housing"
                }
            },
            "Seals/Gaskets": {
                "Crank seal leak": {
                    "failure_code": "NAN-NAN-081",
                    "cause_code": "NAN-NAN-C081",
                    "resolution_code": "NAN-NAN-R081",
                    "recommended_action": "Replace seal/gasket; Reseal to spec"
                },
                "Valve cover leak": {
                    "failure_code": "NAN-NAN-082",
                    "cause_code": "NAN-NAN-C082",
                    "resolution_code": "NAN-NAN-R082",
                    "recommended_action": "Replace seal/gasket; Reseal to spec"
                },
                "Oil pan leak": {
                    "failure_code": "NAN-NAN-083",
                    "cause_code": "NAN-NAN-C083",
                    "resolution_code": "NAN-NAN-R083",
                    "recommended_action": "Replace seal/gasket; Reseal to spec"
                }
            }
        },
        "Cooling": {
            "Radiator": {
                "Leak (core)": {
                    "failure_code": "NAN-COL-001",
                    "cause_code": "NAN-COL-C001",
                    "resolution_code": "NAN-COL-R001",
                    "recommended_action": "Replace radiator; Clean fins; Flush system; Replace cap"
                },
                "Fins blocked": {
                    "failure_code": "NAN-NAN-084",
                    "cause_code": "NAN-NAN-C084",
                    "resolution_code": "NAN-NAN-R084",
                    "recommended_action": "Replace radiator; Clean fins; Flush system; Replace cap"
                },
                "Internal restriction": {
                    "failure_code": "NAN-NAN-085",
                    "cause_code": "NAN-NAN-C085",
                    "resolution_code": "NAN-NAN-R085",
                    "recommended_action": "Replace radiator; Clean fins; Flush system; Replace cap"
                },
                "Cap failure": {
                    "failure_code": "NAN-NAN-086",
                    "cause_code": "NAN-NAN-C086",
                    "resolution_code": "NAN-NAN-R086",
                    "recommended_action": "Replace radiator; Clean fins; Flush system; Replace cap"
                }
            },
            "Water Pump": {
                "Seal failure": {
                    "failure_code": "NAN-NAN-087",
                    "cause_code": "NAN-NAN-C087",
                    "resolution_code": "NAN-NAN-R087",
                    "recommended_action": "Replace pump; Replace gasket/seal"
                },
                "Impeller erosion": {
                    "failure_code": "NAN-NAN-088",
                    "cause_code": "NAN-NAN-C088",
                    "resolution_code": "NAN-NAN-R088",
                    "recommended_action": "Replace pump; Replace gasket/seal"
                },
                "Bearing failure": {
                    "failure_code": "NAN-NAN-089",
                    "cause_code": "NAN-NAN-C089",
                    "resolution_code": "NAN-NAN-R089",
                    "recommended_action": "Replace pump; Replace gasket/seal"
                }
            },
            "Thermostat": {
                "Stuck open": {
                    "failure_code": "NAN-NAN-090",
                    "cause_code": "NAN-NAN-C090",
                    "resolution_code": "NAN-NAN-R090",
                    "recommended_action": "Replace thermostat; Bleed system"
                },
                "Stuck closed": {
                    "failure_code": "NAN-NAN-091",
                    "cause_code": "NAN-NAN-C091",
                    "resolution_code": "NAN-NAN-R091",
                    "recommended_action": "Replace thermostat; Bleed system"
                },
                "Bypass leak": {
                    "failure_code": "NAN-NAN-092",
                    "cause_code": "NAN-NAN-C092",
                    "resolution_code": "NAN-NAN-R092",
                    "recommended_action": "Replace thermostat; Bleed system"
                }
            },
            "Cooling Fans": {
                "Motor failure": {
                    "failure_code": "NAN-NAN-093",
                    "cause_code": "NAN-NAN-C093",
                    "resolution_code": "NAN-NAN-R093",
                    "recommended_action": "Replace fan/motor; Replace relay/driver; Replace viscous clutch"
                },
                "Relay/driver fault": {
                    "failure_code": "NAN-NAN-094",
                    "cause_code": "NAN-NAN-C094",
                    "resolution_code": "NAN-NAN-R094",
                    "recommended_action": "Replace fan/motor; Replace relay/driver; Replace viscous clutch"
                },
                "Viscous clutch worn": {
                    "failure_code": "NAN-NAN-095",
                    "cause_code": "NAN-NAN-C095",
                    "resolution_code": "NAN-NAN-R095",
                    "recommended_action": "Replace fan/motor; Replace relay/driver; Replace viscous clutch"
                }
            },
            "Hoses": {
                "Burst": {
                    "failure_code": "NAN-NAN-096",
                    "cause_code": "NAN-NAN-C096",
                    "resolution_code": "NAN-NAN-R096",
                    "recommended_action": "Replace hose; Replace clamp"
                },
                "Loose clamp": {
                    "failure_code": "NAN-NAN-097",
                    "cause_code": "NAN-NAN-C097",
                    "resolution_code": "NAN-NAN-R097",
                    "recommended_action": "Replace hose; Replace clamp"
                },
                "Aging/cracked": {
                    "failure_code": "NAN-NAN-098",
                    "cause_code": "NAN-NAN-C098",
                    "resolution_code": "NAN-NAN-R098",
                    "recommended_action": "Replace hose; Replace clamp"
                }
            }
        },
        "Exhaust/Emissions": {
            "Exhaust Manifold": {
                "Crack": {
                    "failure_code": "NAN-EXH-001",
                    "cause_code": "NAN-EXH-C001",
                    "resolution_code": "NAN-EXH-R001",
                    "recommended_action": "Replace manifold; Replace gasket; Replace stud"
                },
                "Gasket leak": {
                    "failure_code": "NAN-NAN-099",
                    "cause_code": "NAN-NAN-C099",
                    "resolution_code": "NAN-NAN-R099",
                    "recommended_action": "Replace manifold; Replace gasket; Replace stud"
                },
                "Broken stud": {
                    "failure_code": "NAN-NAN-100",
                    "cause_code": "NAN-NAN-C100",
                    "resolution_code": "NAN-NAN-R100",
                    "recommended_action": "Replace manifold; Replace gasket; Replace stud"
                }
            },
            "Catalytic Converter": {
                "Blocked substrate": {
                    "failure_code": "NAN-NAN-101",
                    "cause_code": "NAN-NAN-C101",
                    "resolution_code": "NAN-NAN-R101",
                    "recommended_action": "Replace converter; Correct fueling issues"
                },
                "Melted catalyst": {
                    "failure_code": "NAN-NAN-102",
                    "cause_code": "NAN-NAN-C102",
                    "resolution_code": "NAN-NAN-R102",
                    "recommended_action": "Replace converter; Correct fueling issues"
                },
                "Rattling core": {
                    "failure_code": "NAN-NAN-103",
                    "cause_code": "NAN-NAN-C103",
                    "resolution_code": "NAN-NAN-R103",
                    "recommended_action": "Replace converter; Correct fueling issues"
                }
            },
            "Oxygen Sensor": {
                "Contamination": {
                    "failure_code": "NAN-NAN-104",
                    "cause_code": "NAN-NAN-C104",
                    "resolution_code": "NAN-NAN-R104",
                    "recommended_action": "Replace sensor; Repair wiring"
                },
                "Signal stuck": {
                    "failure_code": "NAN-NAN-105",
                    "cause_code": "NAN-NAN-C105",
                    "resolution_code": "NAN-NAN-R105",
                    "recommended_action": "Replace sensor; Repair wiring"
                },
                "Wiring damage": {
                    "failure_code": "NAN-NAN-106",
                    "cause_code": "NAN-NAN-C106",
                    "resolution_code": "NAN-NAN-R106",
                    "recommended_action": "Replace sensor; Repair wiring"
                }
            },
            "EGR Valve": {
                "Stuck open": {
                    "failure_code": "NAN-NAN-107",
                    "cause_code": "NAN-NAN-C107",
                    "resolution_code": "NAN-NAN-R107",
                    "recommended_action": "Clean/replace EGR; Replace gasket"
                },
                "Stuck closed": {
                    "failure_code": "NAN-NAN-108",
                    "cause_code": "NAN-NAN-C108",
                    "resolution_code": "NAN-NAN-R108",
                    "recommended_action": "Clean/replace EGR; Replace gasket"
                },
                "Leak at seat": {
                    "failure_code": "NAN-NAN-109",
                    "cause_code": "NAN-NAN-C109",
                    "resolution_code": "NAN-NAN-R109",
                    "recommended_action": "Clean/replace EGR; Replace gasket"
                }
            }
        },
        "Long Block": {
            "Cylinder Head": {
                "Warped": {
                    "failure_code": "NAN-LGB-001",
                    "cause_code": "NAN-LGB-C001",
                    "resolution_code": "NAN-LGB-R001",
                    "recommended_action": "Resurface/replace head; Replace gasket; Torque to spec"
                },
                "Cracked": {
                    "failure_code": "NAN-NAN-110",
                    "cause_code": "NAN-NAN-C110",
                    "resolution_code": "NAN-NAN-R110",
                    "recommended_action": "Resurface/replace head; Replace gasket; Torque to spec"
                },
                "Gasket failure": {
                    "failure_code": "NAN-NAN-111",
                    "cause_code": "NAN-NAN-C111",
                    "resolution_code": "NAN-NAN-R111",
                    "recommended_action": "Resurface/replace head; Replace gasket; Torque to spec"
                }
            },
            "Valvetrain": {
                "Cam wear": {
                    "failure_code": "NAN-NAN-112",
                    "cause_code": "NAN-NAN-C112",
                    "resolution_code": "NAN-NAN-R112",
                    "recommended_action": "Replace worn parts; Adjust lash"
                },
                "Lifter collapse": {
                    "failure_code": "NAN-NAN-113",
                    "cause_code": "NAN-NAN-C113",
                    "resolution_code": "NAN-NAN-R113",
                    "recommended_action": "Replace worn parts; Adjust lash"
                },
                "Bent valve": {
                    "failure_code": "NAN-NAN-114",
                    "cause_code": "NAN-NAN-C114",
                    "resolution_code": "NAN-NAN-R114",
                    "recommended_action": "Replace worn parts; Adjust lash"
                }
            },
            "Timing System": {
                "Belt/chain stretch": {
                    "failure_code": "NAN-NAN-115",
                    "cause_code": "NAN-NAN-C115",
                    "resolution_code": "NAN-NAN-R115",
                    "recommended_action": "Replace belt/chain kit; Set timing"
                },
                "Tensioner failure": {
                    "failure_code": "NAN-NAN-116",
                    "cause_code": "NAN-NAN-C116",
                    "resolution_code": "NAN-NAN-R116",
                    "recommended_action": "Replace belt/chain kit; Set timing"
                },
                "Guide wear": {
                    "failure_code": "NAN-NAN-117",
                    "cause_code": "NAN-NAN-C117",
                    "resolution_code": "NAN-NAN-R117",
                    "recommended_action": "Replace belt/chain kit; Set timing"
                }
            },
            "Bottom End": {
                "Bearing wear": {
                    "failure_code": "NAN-NAN-118",
                    "cause_code": "NAN-NAN-C118",
                    "resolution_code": "NAN-NAN-R118",
                    "recommended_action": "Overhaul short block; Replace bearings"
                },
                "Rod knock": {
                    "failure_code": "NAN-NAN-119",
                    "cause_code": "NAN-NAN-C119",
                    "resolution_code": "NAN-NAN-R119",
                    "recommended_action": "Overhaul short block; Replace bearings"
                },
                "Piston ring wear": {
                    "failure_code": "NAN-NAN-120",
                    "cause_code": "NAN-NAN-C120",
                    "resolution_code": "NAN-NAN-R120",
                    "recommended_action": "Overhaul short block; Replace bearings"
                }
            }
        }
    },
    "Transmission/Drivetrain": {
        "Manual": {
            "Clutch": {
                "Disc wear": {
                    "failure_code": "TRN-MAN-001",
                    "cause_code": "TRN-MAN-C001",
                    "resolution_code": "TRN-MAN-R001",
                    "recommended_action": "Replace clutch kit; Bleed hydraulics"
                },
                "Pressure plate crack": {
                    "failure_code": "NAN-NAN-121",
                    "cause_code": "NAN-NAN-C121",
                    "resolution_code": "NAN-NAN-R121",
                    "recommended_action": "Replace clutch kit; Bleed hydraulics"
                },
                "Release bearing failure": {
                    "failure_code": "NAN-NAN-122",
                    "cause_code": "NAN-NAN-C122",
                    "resolution_code": "NAN-NAN-R122",
                    "recommended_action": "Replace clutch kit; Bleed hydraulics"
                },
                "Hydraulic leak": {
                    "failure_code": "NAN-NAN-123",
                    "cause_code": "NAN-NAN-C123",
                    "resolution_code": "NAN-NAN-R123",
                    "recommended_action": "Replace clutch kit; Bleed hydraulics"
                }
            },
            "Gearbox": {
                "Synchro wear": {
                    "failure_code": "NAN-NAN-124",
                    "cause_code": "NAN-NAN-C124",
                    "resolution_code": "NAN-NAN-R124",
                    "recommended_action": "Overhaul gearbox; Replace bearings/gears"
                },
                "Bearing failure": {
                    "failure_code": "NAN-NAN-125",
                    "cause_code": "NAN-NAN-C125",
                    "resolution_code": "NAN-NAN-R125",
                    "recommended_action": "Overhaul gearbox; Replace bearings/gears"
                },
                "Gear tooth damage": {
                    "failure_code": "NAN-NAN-126",
                    "cause_code": "NAN-NAN-C126",
                    "resolution_code": "NAN-NAN-R126",
                    "recommended_action": "Overhaul gearbox; Replace bearings/gears"
                },
                "Selector fork wear": {
                    "failure_code": "NAN-NAN-127",
                    "cause_code": "NAN-NAN-C127",
                    "resolution_code": "NAN-NAN-R127",
                    "recommended_action": "Overhaul gearbox; Replace bearings/gears"
                }
            }
        },
        "Automatic/CVT": {
            "AT/CVT Unit": {
                "Fluid overheat": {
                    "failure_code": "NAN-AT-001",
                    "cause_code": "NAN-AT-C001",
                    "resolution_code": "NAN-AT-R001",
                    "recommended_action": "Service fluid/filter; Replace solenoid pack; Overhaul/replace unit"
                },
                "Clutch pack wear": {
                    "failure_code": "NAN-NAN-128",
                    "cause_code": "NAN-NAN-C128",
                    "resolution_code": "NAN-NAN-R128",
                    "recommended_action": "Service fluid/filter; Replace solenoid pack; Overhaul/replace unit"
                },
                "Valve body fault": {
                    "failure_code": "NAN-NAN-129",
                    "cause_code": "NAN-NAN-C129",
                    "resolution_code": "NAN-NAN-R129",
                    "recommended_action": "Service fluid/filter; Replace solenoid pack; Overhaul/replace unit"
                },
                "Solenoid failure": {
                    "failure_code": "NAN-NAN-130",
                    "cause_code": "NAN-NAN-C130",
                    "resolution_code": "NAN-NAN-R130",
                    "recommended_action": "Service fluid/filter; Replace solenoid pack; Overhaul/replace unit"
                },
                "Belt/chain slip (CVT)": {
                    "failure_code": "NAN-NAN-131",
                    "cause_code": "NAN-NAN-C131",
                    "resolution_code": "NAN-NAN-R131",
                    "recommended_action": "Service fluid/filter; Replace solenoid pack; Overhaul/replace unit"
                }
            },
            "Torque Converter": {
                "Lockup clutch slip": {
                    "failure_code": "NAN-NAN-132",
                    "cause_code": "NAN-NAN-C132",
                    "resolution_code": "NAN-NAN-R132",
                    "recommended_action": "Replace converter; Reprogram TCM if applicable"
                },
                "Seal leak": {
                    "failure_code": "NAN-NAN-133",
                    "cause_code": "NAN-NAN-C133",
                    "resolution_code": "NAN-NAN-R133",
                    "recommended_action": "Replace converter; Reprogram TCM if applicable"
                },
                "Stator failure": {
                    "failure_code": "NAN-NAN-134",
                    "cause_code": "NAN-NAN-C134",
                    "resolution_code": "NAN-NAN-R134",
                    "recommended_action": "Replace converter; Reprogram TCM if applicable"
                }
            }
        },
        "Transfer Case/4x4": {
            "Transfer Case": {
                "Shift actuator fault": {
                    "failure_code": "NAN-TFC-001",
                    "cause_code": "NAN-TFC-C001",
                    "resolution_code": "NAN-TFC-R001",
                    "recommended_action": "Repair actuator; Overhaul case; Replace seals/bearings"
                }
            }
        },
        "Transfer Case/4x5": {
            "Transfer Case": {
                "Chain wear": {
                    "failure_code": "NAN-NAN-135",
                    "cause_code": "NAN-NAN-C135",
                    "resolution_code": "NAN-NAN-R135",
                    "recommended_action": "Repair actuator; Overhaul case; Replace seals/bearings"
                }
            }
        },
        "Transfer Case/4x6": {
            "Transfer Case": {
                "Seal leak": {
                    "failure_code": "NAN-NAN-136",
                    "cause_code": "NAN-NAN-C136",
                    "resolution_code": "NAN-NAN-R136",
                    "recommended_action": "Repair actuator; Overhaul case; Replace seals/bearings"
                }
            }
        },
        "Transfer Case/4x7": {
            "Transfer Case": {
                "Bearing noise": {
                    "failure_code": "NAN-NAN-137",
                    "cause_code": "NAN-NAN-C137",
                    "resolution_code": "NAN-NAN-R137",
                    "recommended_action": "Repair actuator; Overhaul case; Replace seals/bearings"
                }
            }
        },
        "Prop Shaft": {
            "Driveshaft": {
                "Bent tube": {
                    "failure_code": "NAN-PRP-001",
                    "cause_code": "NAN-PRP-C001",
                    "resolution_code": "NAN-PRP-R001",
                    "recommended_action": "Balance shaft; Replace U-joint; Replace center support"
                },
                "Imbalance": {
                    "failure_code": "NAN-NAN-138",
                    "cause_code": "NAN-NAN-C138",
                    "resolution_code": "NAN-NAN-R138",
                    "recommended_action": "Balance shaft; Replace U-joint; Replace center support"
                },
                "U-joint wear": {
                    "failure_code": "NAN-NAN-139",
                    "cause_code": "NAN-NAN-C139",
                    "resolution_code": "NAN-NAN-R139",
                    "recommended_action": "Balance shaft; Replace U-joint; Replace center support"
                },
                "Center bearing failure": {
                    "failure_code": "NAN-NAN-140",
                    "cause_code": "NAN-NAN-C140",
                    "resolution_code": "NAN-NAN-R140",
                    "recommended_action": "Balance shaft; Replace U-joint; Replace center support"
                }
            }
        },
        "Differential/Axle": {
            "Differential": {
                "Gear wear": {
                    "failure_code": "NAN-DIF-001",
                    "cause_code": "NAN-DIF-C001",
                    "resolution_code": "NAN-DIF-R001",
                    "recommended_action": "Overhaul differential; Adjust setup"
                },
                "Incorrect backlash": {
                    "failure_code": "NAN-NAN-141",
                    "cause_code": "NAN-NAN-C141",
                    "resolution_code": "NAN-NAN-R141",
                    "recommended_action": "Overhaul differential; Adjust setup"
                },
                "Bearing failure": {
                    "failure_code": "NAN-NAN-142",
                    "cause_code": "NAN-NAN-C142",
                    "resolution_code": "NAN-NAN-R142",
                    "recommended_action": "Overhaul differential; Adjust setup"
                }
            },
            "Axle Shafts": {
                "CV joint wear": {
                    "failure_code": "NAN-NAN-143",
                    "cause_code": "NAN-NAN-C143",
                    "resolution_code": "NAN-NAN-R143",
                    "recommended_action": "Replace half-shaft; Replace seal"
                },
                "Boot tear": {
                    "failure_code": "NAN-NAN-144",
                    "cause_code": "NAN-NAN-C144",
                    "resolution_code": "NAN-NAN-R144",
                    "recommended_action": "Replace half-shaft; Replace seal"
                },
                "Seal leak": {
                    "failure_code": "NAN-NAN-145",
                    "cause_code": "NAN-NAN-C145",
                    "resolution_code": "NAN-NAN-R145",
                    "recommended_action": "Replace half-shaft; Replace seal"
                }
            }
        }
    },
    "Suspension": {
        "Front": {
            "Control Arms": {
                "Bushing wear": {
                    "failure_code": "SUS-FRO-001",
                    "cause_code": "SUS-FRO-C001",
                    "resolution_code": "SUS-FRO-R001",
                    "recommended_action": "Replace bushings; Replace ball joint; Align vehicle"
                },
                "Ball joint play": {
                    "failure_code": "NAN-NAN-146",
                    "cause_code": "NAN-NAN-C146",
                    "resolution_code": "NAN-NAN-R146",
                    "recommended_action": "Replace bushings; Replace ball joint; Align vehicle"
                },
                "Bent arm": {
                    "failure_code": "NAN-NAN-147",
                    "cause_code": "NAN-NAN-C147",
                    "resolution_code": "NAN-NAN-R147",
                    "recommended_action": "Replace bushings; Replace ball joint; Align vehicle"
                }
            },
            "Struts/Shocks": {
                "Seal leak": {
                    "failure_code": "NAN-NAN-148",
                    "cause_code": "NAN-NAN-C148",
                    "resolution_code": "NAN-NAN-R148",
                    "recommended_action": "Replace strut/shock; Alignment"
                },
                "Gas loss": {
                    "failure_code": "NAN-NAN-149",
                    "cause_code": "NAN-NAN-C149",
                    "resolution_code": "NAN-NAN-R149",
                    "recommended_action": "Replace strut/shock; Alignment"
                },
                "Internal damage": {
                    "failure_code": "NAN-NAN-150",
                    "cause_code": "NAN-NAN-C150",
                    "resolution_code": "NAN-NAN-R150",
                    "recommended_action": "Replace strut/shock; Alignment"
                }
            },
            "Steering Knuckle": {
                "Bent/warped": {
                    "failure_code": "NAN-NAN-151",
                    "cause_code": "NAN-NAN-C151",
                    "resolution_code": "NAN-NAN-R151",
                    "recommended_action": "Replace knuckle"
                },
                "Bearing seat wear": {
                    "failure_code": "NAN-NAN-152",
                    "cause_code": "NAN-NAN-C152",
                    "resolution_code": "NAN-NAN-R152",
                    "recommended_action": "Replace knuckle"
                }
            }
        },
        "Rear": {
            "Springs": {
                "Cracked leaf": {
                    "failure_code": "NAN-REAR-001",
                    "cause_code": "NAN-REAR-C001",
                    "resolution_code": "NAN-REAR-R001",
                    "recommended_action": "Replace spring; Inspect mounts"
                },
                "Coil fatigue": {
                    "failure_code": "NAN-NAN-153",
                    "cause_code": "NAN-NAN-C153",
                    "resolution_code": "NAN-NAN-R153",
                    "recommended_action": "Replace spring; Inspect mounts"
                },
                "Sagging": {
                    "failure_code": "NAN-NAN-154",
                    "cause_code": "NAN-NAN-C154",
                    "resolution_code": "NAN-NAN-R154",
                    "recommended_action": "Replace spring; Inspect mounts"
                }
            },
            "Dampers": {
                "Seal leak": {
                    "failure_code": "NAN-NAN-155",
                    "cause_code": "NAN-NAN-C155",
                    "resolution_code": "NAN-NAN-R155",
                    "recommended_action": "Replace damper"
                },
                "Internal wear": {
                    "failure_code": "NAN-NAN-156",
                    "cause_code": "NAN-NAN-C156",
                    "resolution_code": "NAN-NAN-R156",
                    "recommended_action": "Replace damper"
                }
            }
        },
        "Stabilizer": {
            "Anti-roll Bar": {
                "Bushing wear": {
                    "failure_code": "NAN-STB-001",
                    "cause_code": "NAN-STB-C001",
                    "resolution_code": "NAN-STB-R001",
                    "recommended_action": "Replace bushings; Replace links; Repair mount"
                },
                "Link play": {
                    "failure_code": "NAN-NAN-157",
                    "cause_code": "NAN-NAN-C157",
                    "resolution_code": "NAN-NAN-R157",
                    "recommended_action": "Replace bushings; Replace links; Repair mount"
                },
                "Mount crack": {
                    "failure_code": "NAN-NAN-158",
                    "cause_code": "NAN-NAN-C158",
                    "resolution_code": "NAN-NAN-R158",
                    "recommended_action": "Replace bushings; Replace links; Repair mount"
                }
            }
        }
    },
    "Steering": {
        "Steering Gear": {
            "Rack and Pinion": {
                "Seal leak": {
                    "failure_code": "STE-GEAR-001",
                    "cause_code": "STE-GEAR-C001",
                    "resolution_code": "STE-GEAR-R001",
                    "recommended_action": "Replace rack; Replace seals; Torque mounts"
                },
                "Internal wear": {
                    "failure_code": "NAN-NAN-159",
                    "cause_code": "NAN-NAN-C159",
                    "resolution_code": "NAN-NAN-R159",
                    "recommended_action": "Replace rack; Replace seals; Torque mounts"
                },
                "Play": {
                    "failure_code": "NAN-NAN-160",
                    "cause_code": "NAN-NAN-C160",
                    "resolution_code": "NAN-NAN-R160",
                    "recommended_action": "Replace rack; Replace seals; Torque mounts"
                }
            }
        },
        "Power Steering": {
            "Pump": {
                "Pump wear": {
                    "failure_code": "NAN-PSTR-001",
                    "cause_code": "NAN-PSTR-C001",
                    "resolution_code": "NAN-PSTR-R001",
                    "recommended_action": "Replace pump; Bleed system; Fix leaks"
                },
                "Low pressure": {
                    "failure_code": "NAN-NAN-161",
                    "cause_code": "NAN-NAN-C161",
                    "resolution_code": "NAN-NAN-R161",
                    "recommended_action": "Replace pump; Bleed system; Fix leaks"
                },
                "Air ingestion": {
                    "failure_code": "NAN-NAN-162",
                    "cause_code": "NAN-NAN-C162",
                    "resolution_code": "NAN-NAN-R162",
                    "recommended_action": "Replace pump; Bleed system; Fix leaks"
                },
                "Leak": {
                    "failure_code": "NAN-NAN-163",
                    "cause_code": "NAN-NAN-C163",
                    "resolution_code": "NAN-NAN-R163",
                    "recommended_action": "Replace pump; Bleed system; Fix leaks"
                }
            },
            "Hoses": {
                "Hose leak": {
                    "failure_code": "NAN-NAN-164",
                    "cause_code": "NAN-NAN-C164",
                    "resolution_code": "NAN-NAN-R164",
                    "recommended_action": "Replace hose; Retorque fittings"
                },
                "Loose fitting": {
                    "failure_code": "NAN-NAN-165",
                    "cause_code": "NAN-NAN-C165",
                    "resolution_code": "NAN-NAN-R165",
                    "recommended_action": "Replace hose; Retorque fittings"
                },
                "Burst": {
                    "failure_code": "NAN-NAN-166",
                    "cause_code": "NAN-NAN-C166",
                    "resolution_code": "NAN-NAN-R166",
                    "recommended_action": "Replace hose; Retorque fittings"
                }
            },
            "Reservoir": {
                "Crack": {
                    "failure_code": "NAN-NAN-167",
                    "cause_code": "NAN-NAN-C167",
                    "resolution_code": "NAN-NAN-R167",
                    "recommended_action": "Replace reservoir"
                },
                "Filter blockage": {
                    "failure_code": "NAN-NAN-168",
                    "cause_code": "NAN-NAN-C168",
                    "resolution_code": "NAN-NAN-R168",
                    "recommended_action": "Replace reservoir"
                }
            }
        },
        "Electronic Assist": {
            "EPS": {
                "Motor failure": {
                    "failure_code": "NAN-EPS-001",
                    "cause_code": "NAN-EPS-C001",
                    "resolution_code": "NAN-EPS-R001",
                    "recommended_action": "Replace motor; Replace sensor; Replace ECU"
                },
                "Torque sensor fault": {
                    "failure_code": "NAN-NAN-169",
                    "cause_code": "NAN-NAN-C169",
                    "resolution_code": "NAN-NAN-R169",
                    "recommended_action": "Replace motor; Replace sensor; Replace ECU"
                },
                "ECU fault": {
                    "failure_code": "NAN-NAN-170",
                    "cause_code": "NAN-NAN-C170",
                    "resolution_code": "NAN-NAN-R170",
                    "recommended_action": "Replace motor; Replace sensor; Replace ECU"
                }
            }
        }
    },
    "Brakes": {
        "Hydraulic": {
            "Master Cylinder": {
                "Seal bypass": {
                    "failure_code": "BRK-HYD-001",
                    "cause_code": "BRK-HYD-C001",
                    "resolution_code": "BRK-HYD-R001",
                    "recommended_action": "Replace master cylinder; Bleed system"
                },
                "External leak": {
                    "failure_code": "NAN-NAN-171",
                    "cause_code": "NAN-NAN-C171",
                    "resolution_code": "NAN-NAN-R171",
                    "recommended_action": "Replace master cylinder; Bleed system"
                },
                "Corrosion": {
                    "failure_code": "NAN-NAN-172",
                    "cause_code": "NAN-NAN-C172",
                    "resolution_code": "NAN-NAN-R172",
                    "recommended_action": "Replace master cylinder; Bleed system"
                }
            },
            "Brake Booster": {
                "Vacuum leak": {
                    "failure_code": "NAN-NAN-173",
                    "cause_code": "NAN-NAN-C173",
                    "resolution_code": "NAN-NAN-R173",
                    "recommended_action": "Replace booster; Check vacuum supply"
                },
                "Diaphragm rupture": {
                    "failure_code": "NAN-NAN-174",
                    "cause_code": "NAN-NAN-C174",
                    "resolution_code": "NAN-NAN-R174",
                    "recommended_action": "Replace booster; Check vacuum supply"
                }
            },
            "Hoses/Lines": {
                "Rust perforation": {
                    "failure_code": "NAN-NAN-175",
                    "cause_code": "NAN-NAN-C175",
                    "resolution_code": "NAN-NAN-R175",
                    "recommended_action": "Replace line/hose; Bleed system"
                },
                "Hose bulge": {
                    "failure_code": "NAN-NAN-176",
                    "cause_code": "NAN-NAN-C176",
                    "resolution_code": "NAN-NAN-R176",
                    "recommended_action": "Replace line/hose; Bleed system"
                },
                "Internal collapse": {
                    "failure_code": "NAN-NAN-177",
                    "cause_code": "NAN-NAN-C177",
                    "resolution_code": "NAN-NAN-R177",
                    "recommended_action": "Replace line/hose; Bleed system"
                }
            }
        },
        "Friction": {
            "Pads/Shoes": {
                "Worn to backing": {
                    "failure_code": "NAN-FRI-001",
                    "cause_code": "NAN-FRI-C001",
                    "resolution_code": "NAN-FRI-R001",
                    "recommended_action": "Replace pads/shoes; Service hardware"
                },
                "Glazed": {
                    "failure_code": "NAN-NAN-178",
                    "cause_code": "NAN-NAN-C178",
                    "resolution_code": "NAN-NAN-R178",
                    "recommended_action": "Replace pads/shoes; Service hardware"
                },
                "Contaminated": {
                    "failure_code": "NAN-NAN-179",
                    "cause_code": "NAN-NAN-C179",
                    "resolution_code": "NAN-NAN-R179",
                    "recommended_action": "Replace pads/shoes; Service hardware"
                }
            },
            "Rotors/Drums": {
                "Warped": {
                    "failure_code": "NAN-NAN-180",
                    "cause_code": "NAN-NAN-C180",
                    "resolution_code": "NAN-NAN-R180",
                    "recommended_action": "Resurface/replace rotor; Replace drum"
                },
                "Scored": {
                    "failure_code": "NAN-NAN-181",
                    "cause_code": "NAN-NAN-C181",
                    "resolution_code": "NAN-NAN-R181",
                    "recommended_action": "Resurface/replace rotor; Replace drum"
                },
                "Thickness variation": {
                    "failure_code": "NAN-NAN-182",
                    "cause_code": "NAN-NAN-C182",
                    "resolution_code": "NAN-NAN-R182",
                    "recommended_action": "Resurface/replace rotor; Replace drum"
                },
                "Cracked": {
                    "failure_code": "NAN-NAN-183",
                    "cause_code": "NAN-NAN-C183",
                    "resolution_code": "NAN-NAN-R183",
                    "recommended_action": "Resurface/replace rotor; Replace drum"
                }
            },
            "Calipers/Wheel Cyl": {
                "Piston seized": {
                    "failure_code": "NAN-NAN-184",
                    "cause_code": "NAN-NAN-C184",
                    "resolution_code": "NAN-NAN-R184",
                    "recommended_action": "Rebuild/replace caliper; Service slides; Replace seals"
                },
                "Slide pins seized": {
                    "failure_code": "NAN-NAN-185",
                    "cause_code": "NAN-NAN-C185",
                    "resolution_code": "NAN-NAN-R185",
                    "recommended_action": "Rebuild/replace caliper; Service slides; Replace seals"
                },
                "Seal torn": {
                    "failure_code": "NAN-NAN-186",
                    "cause_code": "NAN-NAN-C186",
                    "resolution_code": "NAN-NAN-R186",
                    "recommended_action": "Rebuild/replace caliper; Service slides; Replace seals"
                }
            }
        },
        "ABS/ESC": {
            "Sensors": {
                "Wheel speed sensor fault": {
                    "failure_code": "NAN-ABS-001",
                    "cause_code": "NAN-ABS-C001",
                    "resolution_code": "NAN-ABS-R001",
                    "recommended_action": "Replace sensor; Repair wiring; Clean tone ring"
                },
                "Tone ring damage": {
                    "failure_code": "NAN-NAN-187",
                    "cause_code": "NAN-NAN-C187",
                    "resolution_code": "NAN-NAN-R187",
                    "recommended_action": "Replace sensor; Repair wiring; Clean tone ring"
                },
                "Wiring open": {
                    "failure_code": "NAN-NAN-188",
                    "cause_code": "NAN-NAN-C188",
                    "resolution_code": "NAN-NAN-R188",
                    "recommended_action": "Replace sensor; Repair wiring; Clean tone ring"
                }
            },
            "Hydraulic Modulator": {
                "Valve stuck": {
                    "failure_code": "NAN-NAN-189",
                    "cause_code": "NAN-NAN-C189",
                    "resolution_code": "NAN-NAN-R189",
                    "recommended_action": "Replace/repair modulator; Bleed with scan tool"
                },
                "Pump failure": {
                    "failure_code": "NAN-NAN-190",
                    "cause_code": "NAN-NAN-C190",
                    "resolution_code": "NAN-NAN-R190",
                    "recommended_action": "Replace/repair modulator; Bleed with scan tool"
                },
                "Internal leak": {
                    "failure_code": "NAN-NAN-191",
                    "cause_code": "NAN-NAN-C191",
                    "resolution_code": "NAN-NAN-R191",
                    "recommended_action": "Replace/repair modulator; Bleed with scan tool"
                }
            }
        },
        "Parking/EPB": {
            "Mechanism": {
                "Cable seized": {
                    "failure_code": "NAN-EPB-001",
                    "cause_code": "NAN-EPB-C001",
                    "resolution_code": "NAN-EPB-R001",
                    "recommended_action": "Replace/adjust cable; Replace motor; Replace switch"
                },
                "Motor fault": {
                    "failure_code": "NAN-NAN-192",
                    "cause_code": "NAN-NAN-C192",
                    "resolution_code": "NAN-NAN-R192",
                    "recommended_action": "Replace/adjust cable; Replace motor; Replace switch"
                },
                "Switch fault": {
                    "failure_code": "NAN-NAN-193",
                    "cause_code": "NAN-NAN-C193",
                    "resolution_code": "NAN-NAN-R193",
                    "recommended_action": "Replace/adjust cable; Replace motor; Replace switch"
                },
                "Adjustment out": {
                    "failure_code": "NAN-NAN-194",
                    "cause_code": "NAN-NAN-C194",
                    "resolution_code": "NAN-NAN-R194",
                    "recommended_action": "Replace/adjust cable; Replace motor; Replace switch"
                }
            }
        },
        "Pneumatic (HD)": {
            "Air Compressor": {
                "Low output": {
                    "failure_code": "NAN-PNEU-001",
                    "cause_code": "NAN-PNEU-C001",
                    "resolution_code": "NAN-PNEU-R001",
                    "recommended_action": "Replace compressor; Service drive"
                },
                "Overheat": {
                    "failure_code": "NAN-NAN-195",
                    "cause_code": "NAN-NAN-C195",
                    "resolution_code": "NAN-NAN-R195",
                    "recommended_action": "Replace compressor; Service drive"
                },
                "Leak": {
                    "failure_code": "NAN-NAN-196",
                    "cause_code": "NAN-NAN-C196",
                    "resolution_code": "NAN-NAN-R196",
                    "recommended_action": "Replace compressor; Service drive"
                }
            },
            "Air Dryer": {
                "Desiccant saturated": {
                    "failure_code": "NAN-NAN-197",
                    "cause_code": "NAN-NAN-C197",
                    "resolution_code": "NAN-NAN-R197",
                    "recommended_action": "Service dryer; Replace purge valve"
                },
                "Purge valve stuck": {
                    "failure_code": "NAN-NAN-198",
                    "cause_code": "NAN-NAN-C198",
                    "resolution_code": "NAN-NAN-R198",
                    "recommended_action": "Service dryer; Replace purge valve"
                }
            },
            "Valves": {
                "Relay valve leak": {
                    "failure_code": "NAN-NAN-199",
                    "cause_code": "NAN-NAN-C199",
                    "resolution_code": "NAN-NAN-R199",
                    "recommended_action": "Replace/clean valve"
                },
                "Protection valve stuck": {
                    "failure_code": "NAN-NAN-200",
                    "cause_code": "NAN-NAN-C200",
                    "resolution_code": "NAN-NAN-R200",
                    "recommended_action": "Replace/clean valve"
                },
                "Foot valve leak": {
                    "failure_code": "NAN-NAN-201",
                    "cause_code": "NAN-NAN-C201",
                    "resolution_code": "NAN-NAN-R201",
                    "recommended_action": "Replace/clean valve"
                }
            },
            "Air Tanks": {
                "Corrosion leak": {
                    "failure_code": "NAN-NAN-202",
                    "cause_code": "NAN-NAN-C202",
                    "resolution_code": "NAN-NAN-R202",
                    "recommended_action": "Replace tank; Replace drain valve"
                },
                "Drain valve stuck": {
                    "failure_code": "NAN-NAN-203",
                    "cause_code": "NAN-NAN-C203",
                    "resolution_code": "NAN-NAN-R203",
                    "recommended_action": "Replace tank; Replace drain valve"
                }
            }
        }
    },
    "Electrical/Power": {
        "Battery System": {
            "12V Battery": {
                "Low capacity": {
                    "failure_code": "ELE-BAT-001",
                    "cause_code": "ELE-BAT-C001",
                    "resolution_code": "ELE-BAT-R001",
                    "recommended_action": "Replace battery; Clean terminals; Charge & test"
                },
                "Sulfation": {
                    "failure_code": "NAN-NAN-204",
                    "cause_code": "NAN-NAN-C204",
                    "resolution_code": "NAN-NAN-R204",
                    "recommended_action": "Replace battery; Clean terminals; Charge & test"
                },
                "Terminal corrosion": {
                    "failure_code": "NAN-NAN-205",
                    "cause_code": "NAN-NAN-C205",
                    "resolution_code": "NAN-NAN-R205",
                    "recommended_action": "Replace battery; Clean terminals; Charge & test"
                },
                "Internal short": {
                    "failure_code": "NAN-NAN-206",
                    "cause_code": "NAN-NAN-C206",
                    "resolution_code": "NAN-NAN-R206",
                    "recommended_action": "Replace battery; Clean terminals; Charge & test"
                }
            },
            "Auxiliary Battery": {
                "Low capacity": {
                    "failure_code": "NAN-NAN-207",
                    "cause_code": "NAN-NAN-C207",
                    "resolution_code": "NAN-NAN-R207",
                    "recommended_action": "Replace battery; Replace isolator"
                },
                "Isolator fault": {
                    "failure_code": "NAN-NAN-208",
                    "cause_code": "NAN-NAN-C208",
                    "resolution_code": "NAN-NAN-R208",
                    "recommended_action": "Replace battery; Replace isolator"
                }
            },
            "Battery Tray/Clamps": {
                "Corrosion": {
                    "failure_code": "NAN-NAN-209",
                    "cause_code": "NAN-NAN-C209",
                    "resolution_code": "NAN-NAN-R209",
                    "recommended_action": "Clean/coat; Retorque/replace clamp"
                },
                "Loose clamp": {
                    "failure_code": "NAN-NAN-210",
                    "cause_code": "NAN-NAN-C210",
                    "resolution_code": "NAN-NAN-R210",
                    "recommended_action": "Clean/coat; Retorque/replace clamp"
                }
            },
            "Cables/Terminals": {
                "Loose": {
                    "failure_code": "NAN-NAN-211",
                    "cause_code": "NAN-NAN-C211",
                    "resolution_code": "NAN-NAN-R211",
                    "recommended_action": "Replace cable; Clean/retorque"
                },
                "Corroded": {
                    "failure_code": "NAN-NAN-212",
                    "cause_code": "NAN-NAN-C212",
                    "resolution_code": "NAN-NAN-R212",
                    "recommended_action": "Replace cable; Clean/retorque"
                },
                "Broken strands": {
                    "failure_code": "NAN-NAN-213",
                    "cause_code": "NAN-NAN-C213",
                    "resolution_code": "NAN-NAN-R213",
                    "recommended_action": "Replace cable; Clean/retorque"
                }
            }
        },
        "Charging": {
            "Alternator": {
                "No charge": {
                    "failure_code": "NAN-CHG-001",
                    "cause_code": "NAN-CHG-C001",
                    "resolution_code": "NAN-CHG-R001",
                    "recommended_action": "Replace alternator; Check belt tension"
                },
                "Diode failure": {
                    "failure_code": "NAN-CHG-002",
                    "cause_code": "NAN-CHG-C002",
                    "resolution_code": "NAN-CHG-R002",
                    "recommended_action": "Replace alternator; Check belt tension"
                },
                "Bearing noise": {
                    "failure_code": "NAN-CHG-003",
                    "cause_code": "NAN-CHG-C003",
                    "resolution_code": "NAN-CHG-R003",
                    "recommended_action": "Replace alternator; Check belt tension"
                },
                "Regulator fault": {
                    "failure_code": "NAN-CHG-004",
                    "cause_code": "NAN-CHG-C004",
                    "resolution_code": "NAN-CHG-R004",
                    "recommended_action": "Replace alternator; Check belt tension"
                }
            },
            "Voltage Regulator": {
                "Overcharge": {
                    "failure_code": "NAN-CHG-005",
                    "cause_code": "NAN-CHG-C005",
                    "resolution_code": "NAN-CHG-R005",
                    "recommended_action": "Replace regulator"
                },
                "Undercharge": {
                    "failure_code": "NAN-CHG-006",
                    "cause_code": "NAN-CHG-C006",
                    "resolution_code": "NAN-CHG-R006",
                    "recommended_action": "Replace regulator"
                }
            }
        },
        "Starting": {
            "Starter Motor": {
                "No crank": {
                    "failure_code": "NAN-STR-001",
                    "cause_code": "NAN-STR-C001",
                    "resolution_code": "NAN-STR-R001",
                    "recommended_action": "Replace starter; Repair wiring"
                },
                "Solenoid fault": {
                    "failure_code": "NAN-STR-002",
                    "cause_code": "NAN-STR-C002",
                    "resolution_code": "NAN-STR-R002",
                    "recommended_action": "Replace starter; Repair wiring"
                },
                "Brush wear": {
                    "failure_code": "NAN-STR-003",
                    "cause_code": "NAN-STR-C003",
                    "resolution_code": "NAN-STR-R003",
                    "recommended_action": "Replace starter; Repair wiring"
                }
            },
            "Ignition Switch": {
                "Contact wear": {
                    "failure_code": "NAN-STR-004",
                    "cause_code": "NAN-STR-C004",
                    "resolution_code": "NAN-STR-R004",
                    "recommended_action": "Replace switch"
                },
                "Intermittent": {
                    "failure_code": "NAN-STR-005",
                    "cause_code": "NAN-STR-C005",
                    "resolution_code": "NAN-STR-R005",
                    "recommended_action": "Replace switch"
                }
            }
        },
        "Distribution": {
            "Fuse/Junction Box": {
                "Burned track": {
                    "failure_code": "NAN-DST-001",
                    "cause_code": "NAN-DST-C001",
                    "resolution_code": "NAN-DST-R001",
                    "recommended_action": "Replace box; Seal enclosure"
                },
                "Loose bus": {
                    "failure_code": "NAN-DST-002",
                    "cause_code": "NAN-DST-C002",
                    "resolution_code": "NAN-DST-R002",
                    "recommended_action": "Replace box; Seal enclosure"
                },
                "Water ingress": {
                    "failure_code": "NAN-DST-003",
                    "cause_code": "NAN-DST-C003",
                    "resolution_code": "NAN-DST-R003",
                    "recommended_action": "Replace box; Seal enclosure"
                }
            },
            "Relays": {
                "Contacts burned": {
                    "failure_code": "NAN-DST-004",
                    "cause_code": "NAN-DST-C004",
                    "resolution_code": "NAN-DST-R004",
                    "recommended_action": "Replace relay"
                },
                "Coil open": {
                    "failure_code": "NAN-DST-005",
                    "cause_code": "NAN-DST-C005",
                    "resolution_code": "NAN-DST-R005",
                    "recommended_action": "Replace relay"
                }
            },
            "Wiring Harness": {
                "Open circuit": {
                    "failure_code": "NAN-DST-006",
                    "cause_code": "NAN-DST-C006",
                    "resolution_code": "NAN-DST-R006",
                    "recommended_action": "Repair/replace harness; Replace connector; Add protection"
                },
                "Short to ground": {
                    "failure_code": "NAN-DST-007",
                    "cause_code": "NAN-DST-C007",
                    "resolution_code": "NAN-DST-R007",
                    "recommended_action": "Repair/replace harness; Replace connector; Add protection"
                },
                "Short to power": {
                    "failure_code": "NAN-DST-008",
                    "cause_code": "NAN-DST-C008",
                    "resolution_code": "NAN-DST-R008",
                    "recommended_action": "Repair/replace harness; Replace connector; Add protection"
                },
                "Connector corrosion": {
                    "failure_code": "NAN-DST-009",
                    "cause_code": "NAN-DST-C009",
                    "resolution_code": "NAN-DST-R009",
                    "recommended_action": "Repair/replace harness; Replace connector; Add protection"
                },
                "Chafed wire": {
                    "failure_code": "NAN-DST-010",
                    "cause_code": "NAN-DST-C010",
                    "resolution_code": "NAN-DST-R010",
                    "recommended_action": "Repair/replace harness; Replace connector; Add protection"
                }
            },
            "Ground Straps": {
                "Loose": {
                    "failure_code": "NAN-DST-011",
                    "cause_code": "NAN-DST-C011",
                    "resolution_code": "NAN-DST-R011",
                    "recommended_action": "Retorque ground; Replace strap"
                },
                "Broken": {
                    "failure_code": "NAN-DST-012",
                    "cause_code": "NAN-DST-C012",
                    "resolution_code": "NAN-DST-R012",
                    "recommended_action": "Retorque ground; Replace strap"
                },
                "Corroded": {
                    "failure_code": "NAN-DST-013",
                    "cause_code": "NAN-DST-C013",
                    "resolution_code": "NAN-DST-R013",
                    "recommended_action": "Retorque ground; Replace strap"
                }
            }
        }
    },
    "Lighting & Signaling": {
        "Exterior": {
            "Headlamps": {
                "Bulb failure": {
                    "failure_code": "LGT-EXT-001",
                    "cause_code": "LGT-EXT-C001",
                    "resolution_code": "LGT-EXT-R001",
                    "recommended_action": "Replace bulb/driver; Reseal housing; Replace lamp"
                },
                "LED driver failure": {
                    "failure_code": "NAN-EXT-001",
                    "cause_code": "NAN-EXT-C001",
                    "resolution_code": "NAN-EXT-R001",
                    "recommended_action": "Replace bulb/driver; Reseal housing; Replace lamp"
                },
                "Flicker": {
                    "failure_code": "NAN-EXT-002",
                    "cause_code": "NAN-EXT-C002",
                    "resolution_code": "NAN-EXT-R002",
                    "recommended_action": "Replace bulb/driver; Reseal housing; Replace lamp"
                },
                "Water ingress": {
                    "failure_code": "NAN-EXT-003",
                    "cause_code": "NAN-EXT-C003",
                    "resolution_code": "NAN-EXT-R003",
                    "recommended_action": "Replace bulb/driver; Reseal housing; Replace lamp"
                },
                "Lens crack": {
                    "failure_code": "NAN-EXT-004",
                    "cause_code": "NAN-EXT-C004",
                    "resolution_code": "NAN-EXT-R004",
                    "recommended_action": "Replace bulb/driver; Reseal housing; Replace lamp"
                }
            },
            "Tail/Brake/Indicator": {
                "Bulb out": {
                    "failure_code": "NAN-EXT-005",
                    "cause_code": "NAN-EXT-C005",
                    "resolution_code": "NAN-EXT-R005",
                    "recommended_action": "Replace bulb/socket; Replace lamp assembly"
                },
                "Socket corrosion": {
                    "failure_code": "NAN-EXT-006",
                    "cause_code": "NAN-EXT-C006",
                    "resolution_code": "NAN-EXT-R006",
                    "recommended_action": "Replace bulb/socket; Replace lamp assembly"
                },
                "Fast flash": {
                    "failure_code": "NAN-EXT-007",
                    "cause_code": "NAN-EXT-C007",
                    "resolution_code": "NAN-EXT-R007",
                    "recommended_action": "Replace bulb/socket; Replace lamp assembly"
                },
                "PCB failure": {
                    "failure_code": "NAN-EXT-008",
                    "cause_code": "NAN-EXT-C008",
                    "resolution_code": "NAN-EXT-R008",
                    "recommended_action": "Replace bulb/socket; Replace lamp assembly"
                }
            },
            "Fog/Work Lights": {
                "No light": {
                    "failure_code": "NAN-EXT-009",
                    "cause_code": "NAN-EXT-C009",
                    "resolution_code": "NAN-EXT-R009",
                    "recommended_action": "Replace lamp; Seal housing"
                },
                "Water ingress": {
                    "failure_code": "NAN-EXT-010",
                    "cause_code": "NAN-EXT-C010",
                    "resolution_code": "NAN-EXT-R010",
                    "recommended_action": "Replace lamp; Seal housing"
                },
                "Cracked lens": {
                    "failure_code": "NAN-EXT-011",
                    "cause_code": "NAN-EXT-C011",
                    "resolution_code": "NAN-EXT-R011",
                    "recommended_action": "Replace lamp; Seal housing"
                }
            },
            "License Plate Lamp": {
                "Bulb out": {
                    "failure_code": "NAN-EXT-012",
                    "cause_code": "NAN-EXT-C012",
                    "resolution_code": "NAN-EXT-R012",
                    "recommended_action": "Replace bulb; Clean connector"
                },
                "Corroded connector": {
                    "failure_code": "NAN-EXT-013",
                    "cause_code": "NAN-EXT-C013",
                    "resolution_code": "NAN-EXT-R013",
                    "recommended_action": "Replace bulb; Clean connector"
                }
            }
        },
        "Interior": {
            "Dome/Map Lights": {
                "No light": {
                    "failure_code": "NAN-INT-001",
                    "cause_code": "NAN-INT-C001",
                    "resolution_code": "NAN-INT-R001",
                    "recommended_action": "Replace lamp/switch"
                },
                "Switch fault": {
                    "failure_code": "NAN-INT-002",
                    "cause_code": "NAN-INT-C002",
                    "resolution_code": "NAN-INT-R002",
                    "recommended_action": "Replace lamp/switch"
                }
            }
        }
    },
    "Body/Trim": {
        "Doors/Windows/Locks": {
            "Window Regulator": {
                "Cable fray": {
                    "failure_code": "BDY-DWL-001",
                    "cause_code": "BDY-DWL-C001",
                    "resolution_code": "BDY-DWL-R001",
                    "recommended_action": "Replace regulator/motor; Align tracks"
                },
                "Motor failure": {
                    "failure_code": "NAN-DWL-001",
                    "cause_code": "NAN-DWL-C001",
                    "resolution_code": "NAN-DWL-R001",
                    "recommended_action": "Replace regulator/motor; Align tracks"
                },
                "Track misalignment": {
                    "failure_code": "NAN-DWL-002",
                    "cause_code": "NAN-DWL-C002",
                    "resolution_code": "NAN-DWL-R002",
                    "recommended_action": "Replace regulator/motor; Align tracks"
                }
            },
            "Door Lock/Handle": {
                "Actuator failure": {
                    "failure_code": "NAN-DWL-003",
                    "cause_code": "NAN-DWL-C003",
                    "resolution_code": "NAN-DWL-R003",
                    "recommended_action": "Replace actuator; Repair linkage; Lubricate latch"
                },
                "Linkage disconnected": {
                    "failure_code": "NAN-DWL-004",
                    "cause_code": "NAN-DWL-C004",
                    "resolution_code": "NAN-DWL-R004",
                    "recommended_action": "Replace actuator; Repair linkage; Lubricate latch"
                },
                "Frozen latch": {
                    "failure_code": "NAN-DWL-005",
                    "cause_code": "NAN-DWL-C005",
                    "resolution_code": "NAN-DWL-R005",
                    "recommended_action": "Replace actuator; Repair linkage; Lubricate latch"
                }
            },
            "Door Hinges/Seals": {
                "Hinge wear": {
                    "failure_code": "NAN-DWL-006",
                    "cause_code": "NAN-DWL-C006",
                    "resolution_code": "NAN-DWL-R006",
                    "recommended_action": "Replace hinge; Replace seal"
                },
                "Seal torn": {
                    "failure_code": "NAN-DWL-007",
                    "cause_code": "NAN-DWL-C007",
                    "resolution_code": "NAN-DWL-R007",
                    "recommended_action": "Replace hinge; Replace seal"
                }
            }
        },
        "Seats/Belts": {
            "Seat Mechanism": {
                "Motor fault": {
                    "failure_code": "NAN-SEAT-001",
                    "cause_code": "NAN-SEAT-C001",
                    "resolution_code": "NAN-SEAT-R001",
                    "recommended_action": "Repair/replace motor; Replace track; Replace switch"
                },
                "Track wear": {
                    "failure_code": "NAN-SEAT-002",
                    "cause_code": "NAN-SEAT-C002",
                    "resolution_code": "NAN-SEAT-R002",
                    "recommended_action": "Repair/replace motor; Replace track; Replace switch"
                },
                "Switch fault": {
                    "failure_code": "NAN-SEAT-003",
                    "cause_code": "NAN-SEAT-C003",
                    "resolution_code": "NAN-SEAT-R003",
                    "recommended_action": "Repair/replace motor; Replace track; Replace switch"
                }
            },
            "Seatbelt": {
                "Won\u2019t retract": {
                    "failure_code": "NAN-SEAT-004",
                    "cause_code": "NAN-SEAT-C004",
                    "resolution_code": "NAN-SEAT-R004",
                    "recommended_action": "Replace seatbelt assembly"
                },
                "Pretensioner fault": {
                    "failure_code": "NAN-SEAT-005",
                    "cause_code": "NAN-SEAT-C005",
                    "resolution_code": "NAN-SEAT-R005",
                    "recommended_action": "Replace seatbelt assembly"
                },
                "Latch fault": {
                    "failure_code": "NAN-SEAT-006",
                    "cause_code": "NAN-SEAT-C006",
                    "resolution_code": "NAN-SEAT-R006",
                    "recommended_action": "Replace seatbelt assembly"
                }
            }
        },
        "Glass/Exterior": {
            "Windscreen/Windows": {
                "Cracked": {
                    "failure_code": "NAN-GLS-001",
                    "cause_code": "NAN-GLS-C001",
                    "resolution_code": "NAN-GLS-R001",
                    "recommended_action": "Replace glass; Reseal"
                },
                "Delamination": {
                    "failure_code": "NAN-GLS-002",
                    "cause_code": "NAN-GLS-C002",
                    "resolution_code": "NAN-GLS-R002",
                    "recommended_action": "Replace glass; Reseal"
                },
                "Water leak": {
                    "failure_code": "NAN-GLS-003",
                    "cause_code": "NAN-GLS-C003",
                    "resolution_code": "NAN-GLS-R003",
                    "recommended_action": "Replace glass; Reseal"
                }
            },
            "Mirrors": {
                "Motor fault": {
                    "failure_code": "NAN-GLS-004",
                    "cause_code": "NAN-GLS-C004",
                    "resolution_code": "NAN-GLS-R004",
                    "recommended_action": "Replace mirror assembly"
                },
                "Heater inoperative": {
                    "failure_code": "NAN-GLS-005",
                    "cause_code": "NAN-GLS-C005",
                    "resolution_code": "NAN-GLS-R005",
                    "recommended_action": "Replace mirror assembly"
                },
                "Glass loose": {
                    "failure_code": "NAN-GLS-006",
                    "cause_code": "NAN-GLS-C006",
                    "resolution_code": "NAN-GLS-R006",
                    "recommended_action": "Replace mirror assembly"
                }
            },
            "Bumpers/Grille": {
                "Crack": {
                    "failure_code": "NAN-GLS-007",
                    "cause_code": "NAN-GLS-C007",
                    "resolution_code": "NAN-GLS-R007",
                    "recommended_action": "Replace/realign; Replace clips"
                },
                "Misaligned": {
                    "failure_code": "NAN-GLS-008",
                    "cause_code": "NAN-GLS-C008",
                    "resolution_code": "NAN-GLS-R008",
                    "recommended_action": "Replace/realign; Replace clips"
                },
                "Clip failure": {
                    "failure_code": "NAN-GLS-009",
                    "cause_code": "NAN-GLS-C009",
                    "resolution_code": "NAN-GLS-R009",
                    "recommended_action": "Replace/realign; Replace clips"
                }
            }
        },
        "Sunroof": {
            "Sunroof Module": {
                "Motor jam": {
                    "failure_code": "NAN-SUN-001",
                    "cause_code": "NAN-SUN-C001",
                    "resolution_code": "NAN-SUN-R001",
                    "recommended_action": "Replace motor/module; Clean/grease tracks; Clear drains"
                },
                "Track wear": {
                    "failure_code": "NAN-SUN-002",
                    "cause_code": "NAN-SUN-C002",
                    "resolution_code": "NAN-SUN-R002",
                    "recommended_action": "Replace motor/module; Clean/grease tracks; Clear drains"
                },
                "Drain blockage": {
                    "failure_code": "NAN-SUN-003",
                    "cause_code": "NAN-SUN-C003",
                    "resolution_code": "NAN-SUN-R003",
                    "recommended_action": "Replace motor/module; Clean/grease tracks; Clear drains"
                },
                "Water leak": {
                    "failure_code": "NAN-SUN-004",
                    "cause_code": "NAN-SUN-C004",
                    "resolution_code": "NAN-SUN-R004",
                    "recommended_action": "Replace motor/module; Clean/grease tracks; Clear drains"
                }
            }
        }
    },
    "Chassis/Frame": {
        "Frame/Structure": {
            "Rails/Crossmembers": {
                "Crack": {
                    "failure_code": "CHS-FRM-001",
                    "cause_code": "CHS-FRM-C001",
                    "resolution_code": "CHS-FRM-R001",
                    "recommended_action": "Repair/replace section; Anti-corrosion treat"
                },
                "Corrosion": {
                    "failure_code": "NAN-FRM-001",
                    "cause_code": "NAN-FRM-C001",
                    "resolution_code": "NAN-FRM-R001",
                    "recommended_action": "Repair/replace section; Anti-corrosion treat"
                },
                "Bent": {
                    "failure_code": "NAN-FRM-002",
                    "cause_code": "NAN-FRM-C002",
                    "resolution_code": "NAN-FRM-R002",
                    "recommended_action": "Repair/replace section; Anti-corrosion treat"
                }
            },
            "Mounts/Isolators": {
                "Rubber deterioration": {
                    "failure_code": "NAN-FRM-003",
                    "cause_code": "NAN-FRM-C003",
                    "resolution_code": "NAN-FRM-R003",
                    "recommended_action": "Replace mount; Retorque"
                },
                "Loose bolt": {
                    "failure_code": "NAN-FRM-004",
                    "cause_code": "NAN-FRM-C004",
                    "resolution_code": "NAN-FRM-R004",
                    "recommended_action": "Replace mount; Retorque"
                }
            },
            "Skid Plates": {
                "Bent": {
                    "failure_code": "NAN-FRM-005",
                    "cause_code": "NAN-FRM-C005",
                    "resolution_code": "NAN-FRM-R005",
                    "recommended_action": "Replace plate; Install hardware"
                },
                "Missing bolts": {
                    "failure_code": "NAN-FRM-006",
                    "cause_code": "NAN-FRM-C006",
                    "resolution_code": "NAN-FRM-R006",
                    "recommended_action": "Replace plate; Install hardware"
                }
            },
            "Tow/Recovery Points": {
                "Deformed": {
                    "failure_code": "NAN-FRM-007",
                    "cause_code": "NAN-FRM-C007",
                    "resolution_code": "NAN-FRM-R007",
                    "recommended_action": "Replace hook/bracket; Reweld as spec"
                },
                "Cracked weld": {
                    "failure_code": "NAN-FRM-008",
                    "cause_code": "NAN-FRM-C008",
                    "resolution_code": "NAN-FRM-R008",
                    "recommended_action": "Replace hook/bracket; Reweld as spec"
                }
            }
        }
    },
    "Tires/Wheels": {
        "Rolling Assembly": {
            "Tires": {
                "Puncture": {
                    "failure_code": "TIR-RLL-001",
                    "cause_code": "TIR-RLL-C001",
                    "resolution_code": "TIR-RLL-R001",
                    "recommended_action": "Repair/replace tire; Balance/align; Adjust pressure"
                },
                "Bulge": {
                    "failure_code": "NAN-RLL-001",
                    "cause_code": "NAN-RLL-C001",
                    "resolution_code": "NAN-RLL-R001",
                    "recommended_action": "Repair/replace tire; Balance/align; Adjust pressure"
                },
                "Cupping": {
                    "failure_code": "NAN-RLL-002",
                    "cause_code": "NAN-RLL-C002",
                    "resolution_code": "NAN-RLL-R002",
                    "recommended_action": "Repair/replace tire; Balance/align; Adjust pressure"
                },
                "Feathering": {
                    "failure_code": "NAN-RLL-003",
                    "cause_code": "NAN-RLL-C003",
                    "resolution_code": "NAN-RLL-R003",
                    "recommended_action": "Repair/replace tire; Balance/align; Adjust pressure"
                },
                "Uneven wear": {
                    "failure_code": "NAN-RLL-004",
                    "cause_code": "NAN-RLL-C004",
                    "resolution_code": "NAN-RLL-R004",
                    "recommended_action": "Repair/replace tire; Balance/align; Adjust pressure"
                }
            },
            "Rims": {
                "Bent": {
                    "failure_code": "NAN-RLL-005",
                    "cause_code": "NAN-RLL-C005",
                    "resolution_code": "NAN-RLL-R005",
                    "recommended_action": "Repair/replace rim; Clean bead seat"
                },
                "Cracked": {
                    "failure_code": "NAN-RLL-006",
                    "cause_code": "NAN-RLL-C006",
                    "resolution_code": "NAN-RLL-R006",
                    "recommended_action": "Repair/replace rim; Clean bead seat"
                },
                "Corroded bead seat": {
                    "failure_code": "NAN-RLL-007",
                    "cause_code": "NAN-RLL-C007",
                    "resolution_code": "NAN-RLL-R007",
                    "recommended_action": "Repair/replace rim; Clean bead seat"
                }
            },
            "Hubs/Bearings": {
                "Bearing wear": {
                    "failure_code": "NAN-RLL-008",
                    "cause_code": "NAN-RLL-C008",
                    "resolution_code": "NAN-RLL-R008",
                    "recommended_action": "Replace hub/bearing; Replace seal/studs"
                },
                "Seal leak": {
                    "failure_code": "NAN-RLL-009",
                    "cause_code": "NAN-RLL-C009",
                    "resolution_code": "NAN-RLL-R009",
                    "recommended_action": "Replace hub/bearing; Replace seal/studs"
                },
                "Stud stripped": {
                    "failure_code": "NAN-RLL-010",
                    "cause_code": "NAN-RLL-C010",
                    "resolution_code": "NAN-RLL-R010",
                    "recommended_action": "Replace hub/bearing; Replace seal/studs"
                }
            },
            "TPMS": {
                "Sensor battery low": {
                    "failure_code": "NAN-RLL-011",
                    "cause_code": "NAN-RLL-C011",
                    "resolution_code": "NAN-RLL-R011",
                    "recommended_action": "Replace sensor; Replace seal; Relearn IDs"
                },
                "Seal leak": {
                    "failure_code": "NAN-RLL-012",
                    "cause_code": "NAN-RLL-C012",
                    "resolution_code": "NAN-RLL-R012",
                    "recommended_action": "Replace sensor; Replace seal; Relearn IDs"
                },
                "No RF signal": {
                    "failure_code": "NAN-RLL-013",
                    "cause_code": "NAN-RLL-C013",
                    "resolution_code": "NAN-RLL-R013",
                    "recommended_action": "Replace sensor; Replace seal; Relearn IDs"
                }
            }
        },
        "CTIS (HD)": {
            "CTIS System": {
                "Valve stuck": {
                    "failure_code": "NAN-CTIS-001",
                    "cause_code": "NAN-CTIS-C001",
                    "resolution_code": "NAN-CTIS-R001",
                    "recommended_action": "Replace valve; Repair leak; Replace controller"
                },
                "Air leak": {
                    "failure_code": "NAN-CTIS-002",
                    "cause_code": "NAN-CTIS-C002",
                    "resolution_code": "NAN-CTIS-R002",
                    "recommended_action": "Replace valve; Repair leak; Replace controller"
                },
                "Controller fault": {
                    "failure_code": "NAN-CTIS-003",
                    "cause_code": "NAN-CTIS-C003",
                    "resolution_code": "NAN-CTIS-R003",
                    "recommended_action": "Replace valve; Repair leak; Replace controller"
                }
            }
        }
    },
    "Infotainment/Telematics": {
        "Audio/Navigation": {
            "Head Unit": {
                "No power": {
                    "failure_code": "INF-AUD-001",
                    "cause_code": "INF-AUD-C001",
                    "resolution_code": "INF-AUD-R001",
                    "recommended_action": "Replace head unit; Update firmware"
                },
                "Frozen UI": {
                    "failure_code": "NAN-AUD-001",
                    "cause_code": "NAN-AUD-C001",
                    "resolution_code": "NAN-AUD-R001",
                    "recommended_action": "Replace head unit; Update firmware"
                },
                "No sound": {
                    "failure_code": "NAN-AUD-002",
                    "cause_code": "NAN-AUD-C002",
                    "resolution_code": "NAN-AUD-R002",
                    "recommended_action": "Replace head unit; Update firmware"
                }
            },
            "Amplifier": {
                "No output": {
                    "failure_code": "NAN-AUD-003",
                    "cause_code": "NAN-AUD-C003",
                    "resolution_code": "NAN-AUD-R003",
                    "recommended_action": "Replace amplifier; Check cooling/vent"
                },
                "Overheat": {
                    "failure_code": "NAN-AUD-004",
                    "cause_code": "NAN-AUD-C004",
                    "resolution_code": "NAN-AUD-R004",
                    "recommended_action": "Replace amplifier; Check cooling/vent"
                }
            },
            "Speakers": {
                "Distortion": {
                    "failure_code": "NAN-AUD-005",
                    "cause_code": "NAN-AUD-C005",
                    "resolution_code": "NAN-AUD-R005",
                    "recommended_action": "Replace speaker"
                },
                "Open circuit": {
                    "failure_code": "NAN-AUD-006",
                    "cause_code": "NAN-AUD-C006",
                    "resolution_code": "NAN-AUD-R006",
                    "recommended_action": "Replace speaker"
                }
            },
            "Display/Cluster": {
                "Dead pixels": {
                    "failure_code": "NAN-AUD-007",
                    "cause_code": "NAN-AUD-C007",
                    "resolution_code": "NAN-AUD-R007",
                    "recommended_action": "Replace display/cluster; Check power/ground"
                },
                "No backlight": {
                    "failure_code": "NAN-AUD-008",
                    "cause_code": "NAN-AUD-C008",
                    "resolution_code": "NAN-AUD-R008",
                    "recommended_action": "Replace display/cluster; Check power/ground"
                },
                "No power": {
                    "failure_code": "NAN-AUD-009",
                    "cause_code": "NAN-AUD-C009",
                    "resolution_code": "NAN-AUD-R009",
                    "recommended_action": "Replace display/cluster; Check power/ground"
                }
            }
        },
        "Comms/GPS": {
            "GPS/Antennas": {
                "No signal": {
                    "failure_code": "NAN-GPS-001",
                    "cause_code": "NAN-GPS-C001",
                    "resolution_code": "NAN-GPS-R001",
                    "recommended_action": "Replace antenna; Replace cable"
                },
                "Cable damage": {
                    "failure_code": "NAN-GPS-002",
                    "cause_code": "NAN-GPS-C002",
                    "resolution_code": "NAN-GPS-R002",
                    "recommended_action": "Replace antenna; Replace cable"
                }
            },
            "Telematics Module": {
                "No cellular link": {
                    "failure_code": "NAN-GPS-003",
                    "cause_code": "NAN-GPS-C003",
                    "resolution_code": "NAN-GPS-R003",
                    "recommended_action": "Replace module/SIM; Check APN/config"
                },
                "SIM fault": {
                    "failure_code": "NAN-GPS-004",
                    "cause_code": "NAN-GPS-C004",
                    "resolution_code": "NAN-GPS-R004",
                    "recommended_action": "Replace module/SIM; Check APN/config"
                },
                "No data upload": {
                    "failure_code": "NAN-GPS-005",
                    "cause_code": "NAN-GPS-C005",
                    "resolution_code": "NAN-GPS-R005",
                    "recommended_action": "Replace module/SIM; Check APN/config"
                }
            },
            "Routers/Modems": {
                "No WAN link": {
                    "failure_code": "NAN-GPS-006",
                    "cause_code": "NAN-GPS-C006",
                    "resolution_code": "NAN-GPS-R006",
                    "recommended_action": "Replace modem; Fix power"
                },
                "Power loss": {
                    "failure_code": "NAN-GPS-007",
                    "cause_code": "NAN-GPS-C007",
                    "resolution_code": "NAN-GPS-R007",
                    "recommended_action": "Replace modem; Fix power"
                }
            },
            "Dashcam/DVR": {
                "No recording": {
                    "failure_code": "NAN-GPS-008",
                    "cause_code": "NAN-GPS-C008",
                    "resolution_code": "NAN-GPS-R008",
                    "recommended_action": "Replace SD/HDD; Replace camera"
                },
                "Memory full": {
                    "failure_code": "NAN-GPS-009",
                    "cause_code": "NAN-GPS-C009",
                    "resolution_code": "NAN-GPS-R009",
                    "recommended_action": "Replace SD/HDD; Replace camera"
                },
                "Lens damage": {
                    "failure_code": "NAN-GPS-010",
                    "cause_code": "NAN-GPS-C010",
                    "resolution_code": "NAN-GPS-R010",
                    "recommended_action": "Replace SD/HDD; Replace camera"
                }
            }
        }
    },
    "Safety/ADAS": {
        "SRS/Airbags": {
            "Airbag System": {
                "Module fault": {
                    "failure_code": "SAF-SRS-001",
                    "cause_code": "SAF-SRS-C001",
                    "resolution_code": "SAF-SRS-R001",
                    "recommended_action": "Replace module; Replace clock spring; Replace sensor; Repair connectors"
                },
                "Clock spring fault": {
                    "failure_code": "NAN-SRS-001",
                    "cause_code": "NAN-SRS-C001",
                    "resolution_code": "NAN-SRS-R001",
                    "recommended_action": "Replace module; Replace clock spring; Replace sensor; Repair connectors"
                },
                "Sensor fault": {
                    "failure_code": "NAN-SRS-002",
                    "cause_code": "NAN-SRS-C002",
                    "resolution_code": "NAN-SRS-R002",
                    "recommended_action": "Replace module; Replace clock spring; Replace sensor; Repair connectors"
                },
                "Connector high resistance": {
                    "failure_code": "NAN-SRS-003",
                    "cause_code": "NAN-SRS-C003",
                    "resolution_code": "NAN-SRS-R003",
                    "recommended_action": "Replace module; Replace clock spring; Replace sensor; Repair connectors"
                }
            }
        },
        "ADAS": {
            "Cameras": {
                "Misalignment": {
                    "failure_code": "NAN-ADAS-001",
                    "cause_code": "NAN-ADAS-C001",
                    "resolution_code": "NAN-ADAS-R001",
                    "recommended_action": "Recalibrate; Replace camera; Seal housing"
                },
                "Moisture ingress": {
                    "failure_code": "NAN-ADAS-002",
                    "cause_code": "NAN-ADAS-C002",
                    "resolution_code": "NAN-ADAS-R002",
                    "recommended_action": "Recalibrate; Replace camera; Seal housing"
                },
                "No image": {
                    "failure_code": "NAN-ADAS-003",
                    "cause_code": "NAN-ADAS-C003",
                    "resolution_code": "NAN-ADAS-R003",
                    "recommended_action": "Recalibrate; Replace camera; Seal housing"
                }
            },
            "Radar/Lidar": {
                "No signal": {
                    "failure_code": "NAN-ADAS-004",
                    "cause_code": "NAN-ADAS-C004",
                    "resolution_code": "NAN-ADAS-R004",
                    "recommended_action": "Replace sensor; Align mount; Recalibrate"
                },
                "Mount misaligned": {
                    "failure_code": "NAN-ADAS-005",
                    "cause_code": "NAN-ADAS-C005",
                    "resolution_code": "NAN-ADAS-R005",
                    "recommended_action": "Replace sensor; Align mount; Recalibrate"
                },
                "Internal fault": {
                    "failure_code": "NAN-ADAS-006",
                    "cause_code": "NAN-ADAS-C006",
                    "resolution_code": "NAN-ADAS-R006",
                    "recommended_action": "Replace sensor; Align mount; Recalibrate"
                }
            },
            "Ultrasonic": {
                "No reading": {
                    "failure_code": "NAN-ADAS-007",
                    "cause_code": "NAN-ADAS-C007",
                    "resolution_code": "NAN-ADAS-R007",
                    "recommended_action": "Replace sensor; Seal"
                },
                "Water ingress": {
                    "failure_code": "NAN-ADAS-008",
                    "cause_code": "NAN-ADAS-C008",
                    "resolution_code": "NAN-ADAS-R008",
                    "recommended_action": "Replace sensor; Seal"
                }
            }
        }
    },
    "Auxiliary/Accessories": {
        "Wipers/Washers": {
            "Front Wiper": {
                "Motor failure": {
                    "failure_code": "AUX-WIP-001",
                    "cause_code": "AUX-WIP-C001",
                    "resolution_code": "AUX-WIP-R001",
                    "recommended_action": "Replace motor/linkage; Replace blades"
                },
                "Linkage wear": {
                    "failure_code": "NAN-WIP-001",
                    "cause_code": "NAN-WIP-C001",
                    "resolution_code": "NAN-WIP-R001",
                    "recommended_action": "Replace motor/linkage; Replace blades"
                },
                "Blade smear": {
                    "failure_code": "NAN-WIP-002",
                    "cause_code": "NAN-WIP-C002",
                    "resolution_code": "NAN-WIP-R002",
                    "recommended_action": "Replace motor/linkage; Replace blades"
                }
            },
            "Rear Wiper": {
                "Motor failure": {
                    "failure_code": "NAN-WIP-003",
                    "cause_code": "NAN-WIP-C003",
                    "resolution_code": "NAN-WIP-R003",
                    "recommended_action": "Replace motor; Service spindle"
                },
                "Seized spindle": {
                    "failure_code": "NAN-WIP-004",
                    "cause_code": "NAN-WIP-C004",
                    "resolution_code": "NAN-WIP-R004",
                    "recommended_action": "Replace motor; Service spindle"
                }
            },
            "Washer System": {
                "Pump no output": {
                    "failure_code": "NAN-WIP-005",
                    "cause_code": "NAN-WIP-C005",
                    "resolution_code": "NAN-WIP-R005",
                    "recommended_action": "Replace pump; Repair hose; Clean nozzle"
                },
                "Hose leak": {
                    "failure_code": "NAN-WIP-006",
                    "cause_code": "NAN-WIP-C006",
                    "resolution_code": "NAN-WIP-R006",
                    "recommended_action": "Replace pump; Repair hose; Clean nozzle"
                },
                "Nozzle clog": {
                    "failure_code": "NAN-WIP-007",
                    "cause_code": "NAN-WIP-C007",
                    "resolution_code": "NAN-WIP-R007",
                    "recommended_action": "Replace pump; Repair hose; Clean nozzle"
                }
            }
        },
        "Power Outlets/Converters": {
            "12V/USB Sockets": {
                "No power": {
                    "failure_code": "NAN-POW-001",
                    "cause_code": "NAN-POW-C001",
                    "resolution_code": "NAN-POW-R001",
                    "recommended_action": "Replace socket; Repair wiring"
                },
                "Loose contact": {
                    "failure_code": "NAN-POW-002",
                    "cause_code": "NAN-POW-C002",
                    "resolution_code": "NAN-POW-R002",
                    "recommended_action": "Replace socket; Repair wiring"
                }
            },
            "Inverter": {
                "No output": {
                    "failure_code": "NAN-POW-003",
                    "cause_code": "NAN-POW-C003",
                    "resolution_code": "NAN-POW-R003",
                    "recommended_action": "Replace inverter; Improve cooling"
                },
                "Overheat": {
                    "failure_code": "NAN-POW-004",
                    "cause_code": "NAN-POW-C004",
                    "resolution_code": "NAN-POW-R004",
                    "recommended_action": "Replace inverter; Improve cooling"
                }
            }
        },
        "Winch/Recovery": {
            "Winch": {
                "Motor failure": {
                    "failure_code": "NAN-WIN-001",
                    "cause_code": "NAN-WIN-C001",
                    "resolution_code": "NAN-WIN-R001",
                    "recommended_action": "Replace motor; Replace relay; Replace cable"
                },
                "Solenoid stuck": {
                    "failure_code": "NAN-WIN-002",
                    "cause_code": "NAN-WIN-C002",
                    "resolution_code": "NAN-WIN-R002",
                    "recommended_action": "Replace motor; Replace relay; Replace cable"
                },
                "Cable frayed": {
                    "failure_code": "NAN-WIN-003",
                    "cause_code": "NAN-WIN-C003",
                    "resolution_code": "NAN-WIN-R003",
                    "recommended_action": "Replace motor; Replace relay; Replace cable"
                }
            }
        }
    },
    "Military/Special": {
        "Armor/Protection": {
            "Ballistic Panels": {
                "Delamination": {
                    "failure_code": "MIL-ARM-001",
                    "cause_code": "MIL-ARM-C001",
                    "resolution_code": "MIL-ARM-R001",
                    "recommended_action": "Replace panel; Torque fasteners; Treat corrosion"
                },
                "Crack": {
                    "failure_code": "NAN-ARM-001",
                    "cause_code": "NAN-ARM-C001",
                    "resolution_code": "NAN-ARM-R001",
                    "recommended_action": "Replace panel; Torque fasteners; Treat corrosion"
                },
                "Loose fasteners": {
                    "failure_code": "NAN-ARM-002",
                    "cause_code": "NAN-ARM-C002",
                    "resolution_code": "NAN-ARM-R002",
                    "recommended_action": "Replace panel; Torque fasteners; Treat corrosion"
                },
                "Corrosion": {
                    "failure_code": "NAN-ARM-003",
                    "cause_code": "NAN-ARM-C003",
                    "resolution_code": "NAN-ARM-R003",
                    "recommended_action": "Replace panel; Torque fasteners; Treat corrosion"
                }
            },
            "Ballistic Glass": {
                "Delamination": {
                    "failure_code": "NAN-ARM-004",
                    "cause_code": "NAN-ARM-C004",
                    "resolution_code": "NAN-ARM-R004",
                    "recommended_action": "Replace glass; Seal edges"
                },
                "Crack": {
                    "failure_code": "NAN-ARM-005",
                    "cause_code": "NAN-ARM-C005",
                    "resolution_code": "NAN-ARM-R005",
                    "recommended_action": "Replace glass; Seal edges"
                },
                "Discoloration": {
                    "failure_code": "NAN-ARM-006",
                    "cause_code": "NAN-ARM-C006",
                    "resolution_code": "NAN-ARM-R006",
                    "recommended_action": "Replace glass; Seal edges"
                }
            },
            "Undercarriage Shield": {
                "Bent": {
                    "failure_code": "NAN-ARM-007",
                    "cause_code": "NAN-ARM-C007",
                    "resolution_code": "NAN-ARM-R007",
                    "recommended_action": "Replace/realign shield; Install hardware"
                },
                "Cracked": {
                    "failure_code": "NAN-ARM-008",
                    "cause_code": "NAN-ARM-C008",
                    "resolution_code": "NAN-ARM-R008",
                    "recommended_action": "Replace/realign shield; Install hardware"
                },
                "Loose bolts": {
                    "failure_code": "NAN-ARM-009",
                    "cause_code": "NAN-ARM-C009",
                    "resolution_code": "NAN-ARM-R009",
                    "recommended_action": "Replace/realign shield; Install hardware"
                }
            }
        },
        "Weapon Mounts": {
            "Turret/Pintle/Cradle": {
                "Seized bearing": {
                    "failure_code": "NAN-WPN-001",
                    "cause_code": "NAN-WPN-C001",
                    "resolution_code": "NAN-WPN-R001",
                    "recommended_action": "Replace bearings/bushings; Lubricate; Treat corrosion"
                },
                "Excessive play": {
                    "failure_code": "NAN-WPN-002",
                    "cause_code": "NAN-WPN-C002",
                    "resolution_code": "NAN-WPN-R002",
                    "recommended_action": "Replace bearings/bushings; Lubricate; Treat corrosion"
                },
                "Corrosion": {
                    "failure_code": "NAN-WPN-003",
                    "cause_code": "NAN-WPN-C003",
                    "resolution_code": "NAN-WPN-R003",
                    "recommended_action": "Replace bearings/bushings; Lubricate; Treat corrosion"
                }
            }
        },
        "Aux Power Units": {
            "APU": {
                "No start": {
                    "failure_code": "NAN-APU-001",
                    "cause_code": "NAN-APU-C001",
                    "resolution_code": "NAN-APU-R001",
                    "recommended_action": "Service/replace alternator; Repair fuel/ignition; Repair cooling"
                },
                "No output": {
                    "failure_code": "NAN-APU-002",
                    "cause_code": "NAN-APU-C002",
                    "resolution_code": "NAN-APU-R002",
                    "recommended_action": "Service/replace alternator; Repair fuel/ignition; Repair cooling"
                },
                "Overheat": {
                    "failure_code": "NAN-APU-003",
                    "cause_code": "NAN-APU-C003",
                    "resolution_code": "NAN-APU-R003",
                    "recommended_action": "Service/replace alternator; Repair fuel/ignition; Repair cooling"
                }
            }
        },
        "Convoy/IR Lighting": {
            "IR/Convoy Lamps": {
                "No light": {
                    "failure_code": "NAN-IR-001",
                    "cause_code": "NAN-IR-C001",
                    "resolution_code": "NAN-IR-R001",
                    "recommended_action": "Replace lamp; Check wiring"
                },
                "Dim": {
                    "failure_code": "NAN-IR-002",
                    "cause_code": "NAN-IR-C002",
                    "resolution_code": "NAN-IR-R002",
                    "recommended_action": "Replace lamp; Check wiring"
                },
                "Lens crack": {
                    "failure_code": "NAN-IR-003",
                    "cause_code": "NAN-IR-C003",
                    "resolution_code": "NAN-IR-R003",
                    "recommended_action": "Replace lamp; Check wiring"
                }
            }
        }
    },
    "Hybrid/EV": {
        "HV Battery": {
            "Battery Pack": {
                "Cell imbalance": {
                    "failure_code": "HEV-HVB-001",
                    "cause_code": "HEV-HVB-C001",
                    "resolution_code": "HEV-HVB-R001",
                    "recommended_action": "Replace module; Calibrate BMS; Repair isolation"
                },
                "Overheat": {
                    "failure_code": "NAN-HVB-001",
                    "cause_code": "NAN-HVB-C001",
                    "resolution_code": "NAN-HVB-R001",
                    "recommended_action": "Replace module; Calibrate BMS; Repair isolation"
                },
                "Isolation fault": {
                    "failure_code": "NAN-HVB-002",
                    "cause_code": "NAN-HVB-C002",
                    "resolution_code": "NAN-HVB-R002",
                    "recommended_action": "Replace module; Calibrate BMS; Repair isolation"
                },
                "Contactor weld": {
                    "failure_code": "NAN-HVB-003",
                    "cause_code": "NAN-HVB-C003",
                    "resolution_code": "NAN-HVB-R003",
                    "recommended_action": "Replace module; Calibrate BMS; Repair isolation"
                }
            },
            "Cooling Loop": {
                "Pump failure": {
                    "failure_code": "NAN-HVB-004",
                    "cause_code": "NAN-HVB-C004",
                    "resolution_code": "NAN-HVB-R004",
                    "recommended_action": "Replace pump; Repair leak; Purge air"
                },
                "Leak": {
                    "failure_code": "NAN-HVB-005",
                    "cause_code": "NAN-HVB-C005",
                    "resolution_code": "NAN-HVB-R005",
                    "recommended_action": "Replace pump; Repair leak; Purge air"
                },
                "Blockage": {
                    "failure_code": "NAN-HVB-006",
                    "cause_code": "NAN-HVB-C006",
                    "resolution_code": "NAN-HVB-R006",
                    "recommended_action": "Replace pump; Repair leak; Purge air"
                }
            }
        },
        "Power Electronics": {
            "Inverter": {
                "IGBT failure": {
                    "failure_code": "NAN-PWR-001",
                    "cause_code": "NAN-PWR-C001",
                    "resolution_code": "NAN-PWR-R001",
                    "recommended_action": "Replace inverter; Improve cooling"
                },
                "Overheat": {
                    "failure_code": "NAN-PWR-002",
                    "cause_code": "NAN-PWR-C002",
                    "resolution_code": "NAN-PWR-R002",
                    "recommended_action": "Replace inverter; Improve cooling"
                },
                "Capacitor fault": {
                    "failure_code": "NAN-PWR-003",
                    "cause_code": "NAN-PWR-C003",
                    "resolution_code": "NAN-PWR-R003",
                    "recommended_action": "Replace inverter; Improve cooling"
                }
            },
            "DC-DC Converter": {
                "No output": {
                    "failure_code": "NAN-PWR-004",
                    "cause_code": "NAN-PWR-C004",
                    "resolution_code": "NAN-PWR-R004",
                    "recommended_action": "Replace converter; Check HV feed"
                },
                "Thermal shutdown": {
                    "failure_code": "NAN-PWR-005",
                    "cause_code": "NAN-PWR-C005",
                    "resolution_code": "NAN-PWR-R005",
                    "recommended_action": "Replace converter; Check HV feed"
                }
            }
        },
        "e-Drive": {
            "Electric Motor": {
                "No torque": {
                    "failure_code": "NAN-EDRV-001",
                    "cause_code": "NAN-EDRV-C001",
                    "resolution_code": "NAN-EDRV-R001",
                    "recommended_action": "Replace motor; Service bearings; Check inverter"
                },
                "Encoder fault": {
                    "failure_code": "NAN-EDRV-002",
                    "cause_code": "NAN-EDRV-C002",
                    "resolution_code": "NAN-EDRV-R002",
                    "recommended_action": "Replace motor; Service bearings; Check inverter"
                },
                "Bearing noise": {
                    "failure_code": "NAN-EDRV-003",
                    "cause_code": "NAN-EDRV-C003",
                    "resolution_code": "NAN-EDRV-R003",
                    "recommended_action": "Replace motor; Service bearings; Check inverter"
                }
            },
            "Charge Port/Onboard Charger": {
                "No charge": {
                    "failure_code": "NAN-EDRV-004",
                    "cause_code": "NAN-EDRV-C004",
                    "resolution_code": "NAN-EDRV-R004",
                    "recommended_action": "Replace socket; Replace charger; Seal housing"
                },
                "Pin damage": {
                    "failure_code": "NAN-EDRV-005",
                    "cause_code": "NAN-EDRV-C005",
                    "resolution_code": "NAN-EDRV-R005",
                    "recommended_action": "Replace socket; Replace charger; Seal housing"
                },
                "Water ingress": {
                    "failure_code": "NAN-EDRV-006",
                    "cause_code": "NAN-EDRV-C006",
                    "resolution_code": "NAN-EDRV-R006",
                    "recommended_action": "Replace socket; Replace charger; Seal housing"
                }
            }
        },
        "HV Cabling": {
            "HV Harness": {
                "Insulation damage": {
                    "failure_code": "NAN-HVC-001",
                    "cause_code": "NAN-HVC-C001",
                    "resolution_code": "NAN-HVC-R001",
                    "recommended_action": "Replace cable; Replace connector"
                },
                "Connector burn": {
                    "failure_code": "NAN-HVC-002",
                    "cause_code": "NAN-HVC-C002",
                    "resolution_code": "NAN-HVC-R002",
                    "recommended_action": "Replace cable; Replace connector"
                }
            }
        }
    },
    "Hydraulics (HD)": {
        "PTO/Power Pack": {
            "Hydraulic Pump": {
                "Leak at shaft seal": {
                    "failure_code": "HYDHD-PPP-001",
                    "cause_code": "HYDHD-PPP-C001",
                    "resolution_code": "HYDHD-PPP-R001",
                    "recommended_action": "Replace seal; Rebuild pump; Eliminate restriction"
                },
                "Low pressure": {
                    "failure_code": "NAN-PPP-001",
                    "cause_code": "NAN-PPP-C001",
                    "resolution_code": "NAN-PPP-R001",
                    "recommended_action": "Replace seal; Rebuild pump; Eliminate restriction"
                },
                "Cavitation": {
                    "failure_code": "NAN-PPP-002",
                    "cause_code": "NAN-PPP-C002",
                    "resolution_code": "NAN-PPP-R002",
                    "recommended_action": "Replace seal; Rebuild pump; Eliminate restriction"
                }
            }
        },
        "Cylinders": {
            "Lift/Tip/Stabilizer": {
                "Seal leak": {
                    "failure_code": "NAN-CYL-001",
                    "cause_code": "NAN-CYL-C001",
                    "resolution_code": "NAN-CYL-R001",
                    "recommended_action": "Replace seals; Polish/replace rod"
                },
                "Rod scoring": {
                    "failure_code": "NAN-CYL-002",
                    "cause_code": "NAN-CYL-C002",
                    "resolution_code": "NAN-CYL-R002",
                    "recommended_action": "Replace seals; Polish/replace rod"
                },
                "Bent rod": {
                    "failure_code": "NAN-CYL-003",
                    "cause_code": "NAN-CYL-C003",
                    "resolution_code": "NAN-CYL-R003",
                    "recommended_action": "Replace seals; Polish/replace rod"
                }
            }
        },
        "Hoses/Fittings": {
            "Hydraulic Lines": {
                "Burst": {
                    "failure_code": "NAN-FIT-001",
                    "cause_code": "NAN-FIT-C001",
                    "resolution_code": "NAN-FIT-R001",
                    "recommended_action": "Replace hose; Retorque fittings; Install guards"
                },
                "Leak": {
                    "failure_code": "NAN-FIT-002",
                    "cause_code": "NAN-FIT-C002",
                    "resolution_code": "NAN-FIT-R002",
                    "recommended_action": "Replace hose; Retorque fittings; Install guards"
                },
                "Abrasion": {
                    "failure_code": "NAN-FIT-003",
                    "cause_code": "NAN-FIT-C003",
                    "resolution_code": "NAN-FIT-R003",
                    "recommended_action": "Replace hose; Retorque fittings; Install guards"
                }
            }
        }
    }
}

# ============================================================================
# DATABASE SETUP
# ============================================================================
DB_FILE = "/tmp/amic_fracas_enhanced_complete.db"

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
    """Seed database with 300 demo work orders using complete catalogue."""
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
    
    # Build list of all possible failures from the complete catalogue
    sample_failures = []
    for system in CATALOGUE_HIERARCHY:
        for subsystem in CATALOGUE_HIERARCHY[system]:
            for component in CATALOGUE_HIERARCHY[system][subsystem]:
                for failure_mode in CATALOGUE_HIERARCHY[system][subsystem][component]:
                    codes = CATALOGUE_HIERARCHY[system][subsystem][component][failure_mode]
                    sample_failures.append((
                        system, subsystem, component, failure_mode,
                        codes['failure_code'], codes['cause_code'], codes['resolution_code']
                    ))
    
    print(f"Loaded {len(sample_failures)} failure modes from catalogue")
    
    with engine.begin() as conn:
        for i in range(300):
            vehicle_id = np.random.choice(vehicles)
            vin, model, vtype = vehicle_info[vehicle_id]
            created_dt = datetime.now() - timedelta(days=np.random.randint(0, 120))
            status = np.random.choice(statuses, p=[0.6, 0.15, 0.2, 0.05])
            
            completed_dt = None
            if status in ["Completed", "Closed"]:
                completed_dt = created_dt + timedelta(days=np.random.randint(1, 20))
            
            # Randomly select from ALL failures in the catalogue
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
                }).sort_values('Failures', ascending=True)
                
                system_chart = alt.Chart(system_df).mark_bar().encode(
                    y=alt.Y("System:N", sort='-x', title="System"),
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
                }).sort_values('Reliability %', ascending=True).head(10)
                
                reliability_chart = alt.Chart(reliability_df).mark_bar().encode(
                    y=alt.Y("System:N", sort='-x', title="System"),
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
            }).sort_values('Count', ascending=True)
            
            failure_chart = alt.Chart(failure_df).mark_bar(color='#F97316').encode(
                y=alt.Y("Failure Mode:N", sort='-x', title="Failure Mode"),
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
            }).sort_values('Health Score', ascending=True)
            
            health_chart = alt.Chart(health_df).mark_bar().encode(
                y=alt.Y("Vehicle:N", sort='-x', title="Vehicle"),
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
                }).sort_values('Completion Rate %', ascending=True)
                
                if len(tech_comp_df) > 0:
                    comp_chart = alt.Chart(tech_comp_df).mark_bar(color='#3B82F6').encode(
                        y=alt.Y("Technician:N", sort='-x', title="Technician"),
                        x=alt.X("Completion Rate %:Q", scale=alt.Scale(domain=[0, 100]), title="Completion %"),
                        color=alt.Color("Completion Rate %:Q", scale=alt.Scale(scheme='blues'))
                    ).properties(height=300)
                    
                    st.altair_chart(comp_chart, use_container_width=True)
            
            with col2:
                st.subheader("Average Labor Hours")
                
                tech_labor_df = pd.DataFrame({
                    'Technician': list(tech_stats.keys()),
                    'Avg Labor Hours': [tech_stats[t]['avg_labor'] for t in tech_stats.keys()]
                }).sort_values('Avg Labor Hours', ascending=True)
                
                if len(tech_labor_df) > 0:
                    labor_chart = alt.Chart(tech_labor_df).mark_bar(color='#8B5CF6').encode(
                        y=alt.Y("Technician:N", sort='-x', title="Technician"),
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
            cost_by_system = cost_by_system.sort_values('Total Cost', ascending=True).head(10)
            
            if len(cost_by_system) > 0:
                cost_chart = alt.Chart(cost_by_system).mark_bar(color='#DC2626').encode(
                    y=alt.Y("system:N", sort='-x', title="System"),
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
                breakdown_chart = alt.Chart(breakdown_df).mark_arc().encode(
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
    st.header("ℹ️ About AMIC FRACAS System - Complete Catalogue")
    
    # Count the entries
    total_systems = len(CATALOGUE_HIERARCHY)
    total_subsystems = sum(len(CATALOGUE_HIERARCHY[sys]) for sys in CATALOGUE_HIERARCHY)
    total_components = sum(len(CATALOGUE_HIERARCHY[sys][sub]) for sys in CATALOGUE_HIERARCHY for sub in CATALOGUE_HIERARCHY[sys])
    total_failures = sum(
        len(CATALOGUE_HIERARCHY[sys][sub][comp])
        for sys in CATALOGUE_HIERARCHY
        for sub in CATALOGUE_HIERARCHY[sys]
        for comp in CATALOGUE_HIERARCHY[sys][sub]
    )
    
    st.markdown(f"""
    ### AMIC Work Order Management & FRACAS System
    **Version 3.0 - Complete Catalogue (White Theme)** ✨
    
    #### 📊 Catalogue Statistics
    - ✅ **{total_systems} Systems** imported from Excel
    - ✅ **{total_subsystems} Subsystems** available
    - ✅ **{total_components} Components** catalogued
    - ✅ **{total_failures} Failure Modes** with complete codes
    
    #### 🎯 Systems Included
    """)
    
    # Show all systems in a nice format
    systems_list = sorted(list(CATALOGUE_HIERARCHY.keys()))
    cols = st.columns(3)
    for i, system in enumerate(systems_list):
        subsystem_count = len(CATALOGUE_HIERARCHY[system])
        component_count = sum(len(CATALOGUE_HIERARCHY[system][sub]) for sub in CATALOGUE_HIERARCHY[system])
        
        with cols[i % 3]:
            st.markdown(f"""
            **{system}**
            - {subsystem_count} subsystems
            - {component_count} components
            """)
    
    st.divider()
    
    st.markdown("""
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
    - ✅ **Complete Fault Classification Catalogue**
    
    #### 🔧 Recent Updates
    - ✅ Imported complete 427-entry fault catalogue from Excel
    - ✅ All 17 systems with full hierarchy
    - ✅ Cascading dropdowns with complete data
    - ✅ Auto-filled codes and recommended actions
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
    
    st.markdown("<div class='header-text'>🚗 AMIC FRACAS System v3.0 (Complete Catalogue)</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle-text'>Advanced Analytics Dashboard with Full Fault Classification</div>", unsafe_allow_html=True)
    
    st.sidebar.title("Navigation")
    
    # Count catalogue entries
    total_failures = sum(
        len(CATALOGUE_HIERARCHY[sys][sub][comp])
        for sys in CATALOGUE_HIERARCHY
        for sub in CATALOGUE_HIERARCHY[sys]
        for comp in CATALOGUE_HIERARCHY[sys][sub]
    )
    
    engine = get_engine()
    with engine.connect() as conn:
        wo_count = conn.execute(text("SELECT COUNT(*) FROM work_orders")).scalar()
    
    st.sidebar.success(f"✅ System Ready\n📦 {wo_count} Work Orders\n📊 {total_failures} Fault Modes\n🔧 {len(CATALOGUE_HIERARCHY)} Systems")
    
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
