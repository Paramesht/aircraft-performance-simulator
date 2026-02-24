import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad
from fpdf import FPDF

st.set_page_config(layout="wide")
st.title("✈ Aircraft Performance & Mission Simulator")

# =============================
# Aircraft Database
# =============================
aircraft_db = {
    "Boeing 777": {"mass":230000, "S":430, "CD0":0.018, "K":0.0484, "thrust_sl":800000, "TSFC":0.6},
    "A320": {"mass":75000, "S":122, "CD0":0.020, "K":0.045, "thrust_sl":240000, "TSFC":0.6},
    "ATR72": {"mass":22000, "S":61, "CD0":0.025, "K":0.055, "thrust_sl":50000, "TSFC":0.5},
    "Business Jet": {"mass":16000, "S":48, "CD0":0.021, "K":0.050, "thrust_sl":100000, "TSFC":0.7},
}

selected = st.sidebar.selectbox("Select Aircraft", list(aircraft_db.keys()))
data = aircraft_db[selected]

mass = st.sidebar.number_input("Mass (kg)", value=data["mass"])
S = data["S"]
CD0 = data["CD0"]
K = data["K"]
thrust_sl = data["thrust_sl"]
TSFC = data["TSFC"]

altitude_ft = st.sidebar.number_input("Altitude (ft)", value=30000.0)
Mach = st.sidebar.number_input("Mach", value=0.83)
throttle = st.sidebar.slider("Throttle (%)", 50, 100, 90)/100

# =============================
# ISA Atmosphere
# =============================
def isa(h):
    T0=288.15; P0=101325; L=-0.0065; R=287; g=9.81
    if h<=11000:
        T=T0+L*h; P=P0*(T/T0)**(-g/(L*R))
    else:
        T=216.65; P=22632*np.exp(-g*(h-11000)/(R*T))
    rho=P/(R*T); a=np.sqrt(1.4*R*T)
    return rho,a

alt_m = altitude_ft*0.3048
rho,a = isa(alt_m)

# =============================
# Thrust Model
# =============================
def thrust_model(thrust_sl, rho, Mach):
    sigma=rho/1.225
    return thrust_sl*(sigma**0.8)*(1-0.25*Mach)

TA = thrust_model(thrust_sl,rho,Mach)*throttle

# =============================
# Aerodynamics
# =============================
V = Mach*a
W = mass*9.81
q = 0.5*rho*V**2

CL = W/(q*S)
CD = CD0 + K*CL**2
TR = q*S*CD
PR = TR*V

ROC = (TA-TR)*V/W
gamma = (TA-TR)/W*180/np.pi
LD_max = 1/(2*np.sqrt(CD0*K))

# =============================
# Service Ceiling
# =============================
def compute_ceiling():
    for h in np.linspace(0,15000,200):
        rho_h,a_h = isa(h)
        TA_h = thrust_model(thrust_sl,rho_h,Mach)*throttle
        V_h = Mach*a_h
        q_h = 0.5*rho_h*V_h**2
        CL_h = W/(q_h*S)
        CD_h = CD0 + K*CL_h**2
        TR_h = q_h*S*CD_h
        ROC_h = (TA_h-TR_h)*V_h/W
        if ROC_h<=0:
            return h/0.3048
    return None

ceiling_ft = compute_ceiling()

# =============================
# Time to Climb
# =============================
def time_to_climb(h1_ft,h2_ft):
    h_vals=np.linspace(h1_ft,h2_ft,100)
    t=0
    for i in range(len(h_vals)-1):
        h_mid=(h_vals[i]+h_vals[i+1])/2
        rho_h,a_h=isa(h_mid*0.3048)
        TA_h=thrust_model(thrust_sl,rho_h,Mach)*throttle
        V_h=Mach*a_h
        q_h=0.5*rho_h*V_h**2
        CL_h=W/(q_h*S)
        CD_h=CD0+K*CL_h**2
        TR_h=q_h*S*CD_h
        ROC_h=(TA_h-TR_h)*V_h/W
        if ROC_h>0:
            dh=(h_vals[i+1]-h_vals[i])*0.3048
            t+=dh/ROC_h
    return t/60

ttc = time_to_climb(5000,altitude_ft)

# =============================
# Breguet Range
# =============================
Wi = st.sidebar.number_input("Initial Weight (kg)", value=mass)
Wf = st.sidebar.number_input("Final Weight (kg)", value=mass*0.85)
range_breguet = (V/TSFC)*LD_max*np.log(Wi/Wf)/1000

# =============================
# Display
# =============================
st.subheader("Performance Summary")

col1,col2,col3 = st.columns(3)

col1.metric("Velocity (m/s)", round(V,2))
col1.metric("Thrust Required (N)", round(TR,0))
col1.metric("ROC (m/s)", round(ROC,2))

col2.metric("Climb Angle (deg)", round(gamma,2))
col2.metric("Service Ceiling (ft)", round(ceiling_ft,0))
col2.metric("Time to Climb (min)", round(ttc,1))

col3.metric("Max L/D", round(LD_max,2))
col3.metric("Power Required (MW)", round(PR/1e6,2))
col3.metric("Breguet Range (km)", round(range_breguet,1))

# =============================
# Thrust vs Mach Plot
# =============================
st.subheader("Engine Thrust vs Mach")

M_range=np.linspace(0,0.9,100)
TA_mach=thrust_model(thrust_sl,rho,M_range)

fig,ax=plt.subplots()
ax.plot(M_range,TA_mach)
ax.set_xlabel("Mach")
ax.set_ylabel("Thrust (N)")
ax.grid()
st.pyplot(fig)
