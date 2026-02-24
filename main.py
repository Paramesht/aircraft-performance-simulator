import streamlit as st
import numpy as np

st.set_page_config(layout="wide")
st.title("✈ Boeing 777-300 Engineering Performance Dashboard")

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
# USER INPUTS
# ============================================================

mass = st.sidebar.slider("Aircraft Mass (kg)", 200000, MTOW, 250000)
cruise_alt_ft = st.sidebar.slider("Cruise Altitude (ft)", 30000, 43000, 35000)
Mach = st.sidebar.slider("Cruise Mach", 0.80, 0.86, 0.84)
fuel_fraction = st.sidebar.slider("Fuel Ratio (Wi/Wf)", 1.2, 1.8, 1.5)

Wi = mass
Wf = mass / fuel_fraction

# ============================================================
# ISA
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
# THRUST
# ============================================================

sigma = rho/1.225
Thrust_available = thrust_SL*(sigma**0.8)*(1-0.25*Mach)
Thrust_required = Drag

# ============================================================
# POWER
# ============================================================

Power_required = Thrust_required * V
Power_available = Thrust_available * V

# ============================================================
# RATE OF CLIMB
# ============================================================

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
Range_km = Range/1000

Endurance = (1/TSFC_sec) * LD * np.log(Wi/Wf)
Endurance_hr = Endurance/3600

# ============================================================
# DISPLAY
# ============================================================

st.subheader("Cruise Performance")

c1,c2,c3 = st.columns(3)

c1.metric("Cruise Mach", round(Mach,3))
c1.metric("Cruise Speed (m/s)", round(V,1))
c1.metric("Lift (kN)", round(Lift/1000,1))

c2.metric("Drag (kN)", round(Drag/1000,1))
c2.metric("Thrust Required (kN)", round(Thrust_required/1000,1))
c2.metric("Thrust Available (kN)", round(Thrust_available/1000,1))

c3.metric("Power Required (MW)", round(Power_required/1e6,1))
c3.metric("Rate of Climb (ft/min)", round(ROC*196.85,0))
c3.metric("L/D", round(LD,1))

st.subheader("Takeoff & Landing")

c4,c5,c6 = st.columns(3)

c4.metric("V2 (m/s)", round(V2,1))
c5.metric("Takeoff Distance (m)", round(S_takeoff,0))
c6.metric("Landing Distance (m)", round(S_landing,0))

st.subheader("Mission Performance")

c7,c8 = st.columns(2)

c7.metric("Estimated Range (km)", round(Range_km,0))
c8.metric("Estimated Endurance (hours)", round(Endurance_hr,1))

# ============================================================
# SPECIFICATIONS (Illustrative Style)
# ============================================================

st.markdown("---")
st.subheader("Boeing 777-300 Specifications")

colA, colB, colC = st.columns(3)

with colA:
    st.markdown("### ✈ Airframe")
    st.write(f"• Wingspan: {Wingspan} m")
    st.write(f"• Length: {Length} m")
    st.write(f"• Wing Area: {S} m²")

with colB:
    st.markdown("### ⚖ Weights")
    st.write(f"• MTOW: {MTOW:,} kg")
    st.write(f"• OEW: {OEW:,} kg")
    st.write(f"• Max Fuel: {MaxFuel:,} kg")

with colC:
    st.markdown("### 🚀 Performance Limits")
    st.write(f"• Max Mach: {MaxMach}")
    st.write(f"• Service Ceiling: {ServiceCeiling:,} ft")
    st.write(f"• Design Range: {DesignRange:,} km")
