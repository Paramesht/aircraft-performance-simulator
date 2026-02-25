import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(layout="wide")

st.markdown("""
<style>
body {
    background-color: black;
}
h1 {
    color: cyan;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

st.title("B777-300 Cockpit Performance Display")

# ============================================================
# AIRCRAFT CONSTANTS
# ============================================================

MTOW = 299000
S = 427
CD0 = 0.018
K = 0.045
thrust_SL = 800000
TSFC_hr = 0.6
g = 9.81

# ============================================================
# SIDEBAR INPUTS
# ============================================================

mass = st.sidebar.slider("Mass (kg)", 200000, MTOW, 250000)
altitude_ft = st.sidebar.slider("Altitude (ft)", 0, 43000, 35000)
Mach = st.sidebar.slider("Mach", 0.2, 0.86, 0.84)
fuel_fraction = st.sidebar.slider("Fuel Ratio Wi/Wf", 1.2, 1.8, 1.5)

# ============================================================
# ISA
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

Drag = q*S*CD
Lift = q*S*CL
LD = CL/CD

sigma = rho/1.225
Thrust_available = thrust_SL*(sigma**0.8)*(1-0.25*Mach)
Thrust_required = Drag

Power_required = Thrust_required * V
Power_available = Thrust_available * V

ROC = (Thrust_available - Thrust_required)*V/W

# ============================================================
# RANGE & ENDURANCE
# ============================================================

Wi = mass
Wf = mass/fuel_fraction
TSFC_sec = TSFC_hr/3600

Range = (V/TSFC_sec) * LD * np.log(Wi/Wf)
Endurance = (1/TSFC_sec) * LD * np.log(Wi/Wf)

# ============================================================
# COCKPIT LAYOUT
# ============================================================

left, center, right = st.columns(3)

# ================= SPEED GAUGE =================
with left:
    fig_speed = go.Figure(go.Indicator(
        mode="gauge+number",
        value=V,
        title={'text': "Airspeed (m/s)"},
        gauge={
            'axis': {'range': [0, 300]},
            'bar': {'color': "lime"},
            'bgcolor': "black",
            'bordercolor': "white"
        }
    ))
    st.plotly_chart(fig_speed, use_container_width=True)

    fig_alt = go.Figure(go.Indicator(
        mode="number",
        value=altitude_ft,
        title={'text': "Altitude (ft)"}
    ))
    st.plotly_chart(fig_alt, use_container_width=True)

# ================= CENTER DATA =================
with center:
    st.metric("Lift (kN)", round(Lift/1000,1))
    st.metric("Drag (kN)", round(Drag/1000,1))
    st.metric("L/D", round(LD,1))
    st.metric("ROC (ft/min)", round(ROC*196.85,0))

# ================= ENGINE GAUGE =================
with right:
    thrust_margin = (Thrust_available - Thrust_required)/1000

    fig_thrust = go.Figure(go.Indicator(
        mode="gauge+number",
        value=thrust_margin,
        title={'text': "Thrust Margin (kN)"},
        gauge={
            'axis': {'range': [-200, 400]},
            'bar': {'color': "orange"},
            'bgcolor': "black",
            'bordercolor': "white"
        }
    ))
    st.plotly_chart(fig_thrust, use_container_width=True)

    fig_end = go.Figure(go.Indicator(
        mode="gauge+number",
        value=Endurance/3600,
        title={'text': "Endurance (hrs)"},
        gauge={'axis': {'range': [0, 20]}}
    ))
    st.plotly_chart(fig_end, use_container_width=True)

# ============================================================
# RUNWAY VISUAL
# ============================================================

st.markdown("---")
st.subheader("Runway Utilization")

runway = 4000
takeoff_ratio = min((V**2)/(2*5)/runway,1)

st.progress(takeoff_ratio)
st.write(f"Estimated Range: {round(Range/1000)} km")
