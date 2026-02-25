import streamlit as st
import numpy as np
import plotly.graph_objects as go

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(page_title="B777 Performance Simulator", layout="wide")

st.markdown("""
<style>
body {
    background-color: #0E1117;
}
h1, h2, h3 {
    color: #00C6FF;
}
</style>
""", unsafe_allow_html=True)

st.title("✈ Boeing 777-300 Advanced Performance Dashboard")

# ============================================================
# AIRCRAFT CONSTANT DATA
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
# SIDEBAR INPUTS
# ============================================================

st.sidebar.header("Flight Conditions")

mass = st.sidebar.slider("Aircraft Mass (kg)", 200000, MTOW, 250000)
altitude_ft = st.sidebar.slider("Altitude (ft)", 0, 43000, 35000)
Mach = st.sidebar.slider("Mach Number", 0.2, 0.86, 0.84)
fuel_fraction = st.sidebar.slider("Fuel Ratio (Wi/Wf)", 1.2, 1.8, 1.5)

Wi = mass
Wf = mass / fuel_fraction

# ============================================================
# ISA ATMOSPHERE
# ============================================================

def isa(h):
    T0=288.15; P0=101325; L=-0.0065; R=287
    if h<=11000:
        T=T0+L*h; P=P0*(T/T0)**(-g/(L*R))
    else:
        T=216.65; P=22632*np.exp(-g*(h-11000)/(R*T))
    rho=P/(R*T)
    a=np.sqrt(1.4*R*T)
    return rho,a

rho,a = isa(altitude_ft*0.3048)
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
# TAKEOFF & LANDING
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
# INSTRUMENT GAUGES
# ============================================================

st.header("Flight Instruments")

col1, col2 = st.columns(2)

with col1:
    fig_speed = go.Figure(go.Indicator(
        mode="gauge+number",
        value=V,
        title={'text': "Speed (m/s)"},
        gauge={
            'axis': {'range': [0, 300]},
            'bar': {'color': "cyan"},
            'steps': [
                {'range': [0, 150], 'color': "lightgray"},
                {'range': [150, 250], 'color': "gray"}
            ]
        }
    ))
    st.plotly_chart(fig_speed, use_container_width=True)

with col2:
    thrust_margin = (Thrust_available - Thrust_required)/1000
    fig_thrust = go.Figure(go.Indicator(
        mode="gauge+number",
        value=thrust_margin,
        title={'text': "Thrust Margin (kN)"},
        gauge={'axis': {'range': [-200, 400]}}
    ))
    st.plotly_chart(fig_thrust, use_container_width=True)

# ============================================================
# RUNWAY VISUALIZATION
# ============================================================

st.header("Runway Utilization")

runway_length = 4000
takeoff_ratio = min(S_takeoff/runway_length,1)
landing_ratio = min(S_landing/runway_length,1)

st.progress(takeoff_ratio)
st.write(f"Takeoff Distance Used: {round(S_takeoff)} m")

st.progress(landing_ratio)
st.write(f"Landing Distance Used: {round(S_landing)} m")

# ============================================================
# FULL PERFORMANCE DATA
# ============================================================

st.header("Performance Summary")

c1,c2,c3 = st.columns(3)

c1.metric("Lift (kN)", round(Lift/1000,1))
c1.metric("Drag (kN)", round(Drag/1000,1))
c1.metric("L/D", round(LD,1))

c2.metric("Thrust Required (kN)", round(Thrust_required/1000,1))
c2.metric("Thrust Available (kN)", round(Thrust_available/1000,1))
c2.metric("Power Required (MW)", round(Power_required/1e6,1))

c3.metric("Power Available (MW)", round(Power_available/1e6,1))
c3.metric("Range (km)", round(Range/1000,0))
c3.metric("Endurance (hours)", round(Endurance/3600,1))
# ============================================================
# COMPLETE HORIZONTAL B777 SPECIFICATION PANEL
# ============================================================

st.markdown("---")
st.header("Boeing 777-300 Complete Technical Snapshot")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Wingspan", "64.8 m")
    st.metric("Length", "73.9 m")
    st.metric("Wing Area", "427 m²")
    st.metric("Aspect Ratio", "9.9")

with col2:
    st.metric("MTOW", "299,000 kg")
    st.metric("OEW", "168,000 kg")
    st.metric("Max Fuel", "145,000 kg")
    st.metric("Passengers", "368–451")

with col3:
    st.metric("Engine Type", "GE90-115B")
    st.metric("Thrust / Engine", "512 kN")
    st.metric("Total Thrust", "800 kN")
    st.metric("Bypass Ratio", "9:1")

with col4:
    st.metric("Max Mach", "0.89")
    st.metric("Cruise Mach", "0.84")
    st.metric("Service Ceiling", "43,000 ft")
    st.metric("Typical ROC", "2,000–3,000 ft/min")

with col5:
    st.metric("Design Range", "11,000 km")
    st.metric("Typical Endurance", "14 hours")
    st.metric("Cruise Speed", "905 km/h")
    st.metric("L/D (Cruise)", "17–19")

# ============================================================
# ENGINE THRUST GAUGE
# ============================================================

st.subheader("Engine Maximum Thrust")

fig_engine = go.Figure(go.Indicator(
    mode="gauge+number",
    value=800,
    title={'text': "Total Engine Thrust (kN)"},
    gauge={
        'axis': {'range': [0, 900]},
        'bar': {'color': "orange"},
        'steps': [
            {'range': [0, 400], 'color': "lightgray"},
            {'range': [400, 700], 'color': "gray"},
            {'range': [700, 900], 'color': "darkred"}
        ]
    }
))
st.plotly_chart(fig_engine, use_container_width=True)
