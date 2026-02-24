import streamlit as st
import numpy as np

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(page_title="B777 Performance Simulator", layout="wide")

# Custom Styling
st.markdown("""
<style>
.main {
    background-color: #0E1117;
    color: white;
}
h1, h2, h3 {
    color: #00C6FF;
}
.metric-box {
    background-color: #1E222A;
    padding: 15px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("✈ Boeing 777-300 Performance Dashboard")

# ============================================================
# AIRCRAFT DATA
# ============================================================

MTOW = 299000
OEW = 168000
MaxFuel = 145000
S = 427
Wingspan = 64.8
Length = 73.9
CD0 = 0.018
K = 0.045
CLmax_TO = 1.6
CLmax_L = 2.2
thrust_SL = 800000
TSFC_hr = 0.6
MaxMach = 0.89
ServiceCeiling = 43000
DesignRange = 11000
g = 9.81

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("Flight Conditions")

mass = st.sidebar.slider("Aircraft Mass (kg)", 200000, MTOW, 250000)
cruise_alt_ft = st.sidebar.slider("Cruise Altitude (ft)", 30000, 43000, 35000)
Mach = st.sidebar.slider("Cruise Mach", 0.80, 0.86, 0.84)
fuel_fraction = st.sidebar.slider("Fuel Ratio (Wi/Wf)", 1.2, 1.8, 1.5)

Wi = mass
Wf = mass / fuel_fraction

# ============================================================
# ISA MODEL
# ============================================================

def isa(h):
    T0=288.15; P0=101325; L=-0.0065; R=287; g=9.81
    if h<=11000:
        T=T0+L*h; P=P0*(T/T0)**(-g/(L*R))
    else:
        T=216.65; P=22632*np.exp(-g*(h-11000)/(R*T))
    rho=P/(R*T)
    a=np.sqrt(1.4*R*T)
    return rho,a

rho,a = isa(cruise_alt_ft*0.3048)
V = Mach*a
W = mass*g

# ============================================================
# AERODYNAMICS
# ============================================================

q = 0.5*rho*V**2
CL = W/(q*S)
CD = CD0 + K*CL**2

Lift = q*S*CL
Drag = q*S*CD
LD = CL/CD

# ============================================================
# THRUST & POWER
# ============================================================

sigma = rho/1.225
Thrust_available = thrust_SL*(sigma**0.8)*(1-0.25*Mach)
Thrust_required = Drag

Power_required = Thrust_required * V
Power_available = Thrust_available * V

ROC = (Thrust_available - Thrust_required)*V/W

# ============================================================
# TAKEOFF
# ============================================================

rho0,_ = isa(0)
W0 = mass*g

V_stall_TO = np.sqrt(2*W0/(rho0*S*CLmax_TO))
V2 = 1.2 * V_stall_TO

mu_roll = 0.02
Drag_TO = 0.5*rho0*V2**2*S*(CD0 + K*(W0/(0.5*rho0*V2**2*S))**2)
Net_force = thrust_SL - Drag_TO - mu_roll*W0
a_TO = Net_force/mass
S_takeoff = V2**2/(2*a_TO)

# ============================================================
# LANDING
# ============================================================

Landing_weight = 0.85 * mass
W_land = Landing_weight * g

V_stall_L = np.sqrt(2*W_land/(rho0*S*CLmax_L))
V_app = 1.3 * V_stall_L
a_brake = 0.3 * g
S_landing = V_app**2/(2*a_brake)

# ============================================================
# RANGE & ENDURANCE
# ============================================================

TSFC_sec = TSFC_hr/3600
Range = (V/TSFC_sec) * LD * np.log(Wi/Wf)
Endurance = (1/TSFC_sec) * LD * np.log(Wi/Wf)

# ============================================================
# DISPLAY
# ============================================================

st.subheader("Cruise Performance")

col1,col2,col3,col4 = st.columns(4)

col1.metric("Mach", round(Mach,3))
col1.metric("Speed (m/s)", round(V,1))

col2.metric("Lift (kN)", round(Lift/1000,1))
col2.metric("Drag (kN)", round(Drag/1000,1))

col3.metric("Thrust Required (kN)", round(Thrust_required/1000,1))
col3.metric("Thrust Available (kN)", round(Thrust_available/1000,1))

col4.metric("Power Required (MW)", round(Power_required/1e6,1))
col4.metric("Power Available (MW)", round(Power_available/1e6,1))

st.subheader("Takeoff & Landing")

col5,col6,col7 = st.columns(3)

col5.metric("V2 (m/s)", round(V2,1))
col6.metric("Takeoff Distance (m)", round(S_takeoff,0))
col7.metric("Landing Distance (m)", round(S_landing,0))

st.subheader("Mission Performance")

col8,col9,col10 = st.columns(3)

col8.metric("Rate of Climb (ft/min)", round(ROC*196.85,0))
col9.metric("Range (km)", round(Range/1000,0))
col10.metric("Endurance (hours)", round(Endurance/3600,1))

st.markdown("---")

st.subheader("Boeing 777-300")

st.image("https://upload.wikimedia.org/wikipedia/commons/0/0c/Boeing_777-300ER_%28Air_China%29.jpg",
         use_column_width=True)

st.markdown("### Specifications")

spec1,spec2,spec3 = st.columns(3)

with spec1:
    st.markdown("**Airframe**")
    st.write(f"Wingspan: {Wingspan} m")
    st.write(f"Length: {Length} m")
    st.write(f"Wing Area: {S} m²")

with spec2:
    st.markdown("**Weights**")
    st.write(f"MTOW: {MTOW:,} kg")
    st.write(f"OEW: {OEW:,} kg")
    st.write(f"Max Fuel: {MaxFuel:,} kg")

with spec3:
    st.markdown("**Limits**")
    st.write(f"Max Mach: {MaxMach}")
    st.write(f"Service Ceiling: {ServiceCeiling:,} ft")
    st.write(f"Design Range: {DesignRange:,} km")
