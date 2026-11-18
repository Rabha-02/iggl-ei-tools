import math
import csv
import io
from datetime import datetime
import streamlit as st

st.set_page_config(page_title="IGGL E&I TOOLS", page_icon="🧰", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
:root { --ink:#243746; --muted:#718096; --teal:#168b83; --teal-dark:#116b66; --mint:#e8f5f1; --paper:#f5f8f7; --line:#e3ece9; }
.stApp { background:linear-gradient(135deg,#f7faf9 0%,#eef6f3 55%,#f8fafc 100%); color:var(--ink); }
[data-testid="stHeader"] { background:rgba(247,250,249,.82); }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#edf7f4 0%,#f7faf9 100%); border-right:1px solid #e0ebe7; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:#3d5960; }
h1,h2,h3,h4 { color:#203b46 !important; letter-spacing:-.025em; }
h1 { font-weight:750 !important; }
p, label, .stMarkdown { color:#405660; }
div[data-testid="stMetric"] { background:rgba(255,255,255,.88); border:1px solid var(--line); padding:16px 18px; border-radius:16px; box-shadow:0 5px 18px rgba(39,78,71,.045); transition:transform .18s ease,box-shadow .18s ease; }
div[data-testid="stMetric"]:hover { transform:translateY(-2px); box-shadow:0 9px 24px rgba(39,78,71,.09); }
div[data-testid="stMetric"] label { color:#71858a !important; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color:#176f69 !important; font-weight:700; }
.stButton > button, .stDownloadButton > button { border:0; border-radius:12px; padding:.58rem 1.1rem; background:linear-gradient(135deg,#168b83,#36a99b); color:white; font-weight:650; box-shadow:0 5px 14px rgba(22,139,131,.16); transition:all .18s ease; }
.stButton > button:hover, .stDownloadButton > button:hover { background:linear-gradient(135deg,#116f69,#238e84); transform:translateY(-1px); box-shadow:0 8px 18px rgba(22,139,131,.22); color:white; }
.stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"], .stTextArea textarea { border-radius:10px !important; background:#fff !important; }
[data-baseweb="tab-list"] { gap:8px; border-bottom:1px solid #e1ebe7; }
button[data-baseweb="tab"] { border-radius:10px 10px 0 0; color:#5a7378; padding:10px 16px; }
button[data-baseweb="tab"][aria-selected="true"] { color:#137b74; border-bottom:3px solid #168b83; background:#eaf6f2; font-weight:700; }
[data-testid="stAlert"] { border-radius:14px; border:1px solid #e1ebe7; }
[data-testid="stExpander"] { border:1px solid #e2ece8; border-radius:13px; background:rgba(255,255,255,.65); }
hr { border-color:#e2ece8; }
small,.stCaption { color:#71858a !important; }
.stProgress > div > div { background:#168b83; }
a { color:#137b74 !important; }
@media (max-width: 700px) {
 .block-container { padding-top:1.2rem; padding-left:1rem; padding-right:1rem; }
 h1 { font-size:1.8rem !important; }
 div[data-testid="stMetric"] { padding:12px; }
}

.brandbar {display:flex;align-items:center;justify-content:space-between;gap:16px;padding:20px 24px;margin:4px 0 24px;background:linear-gradient(110deg,#ffffff 0%,#f0faf6 100%);border:1px solid #e2eee9;border-radius:20px;box-shadow:0 8px 28px rgba(38,86,72,.055);}
.brandname {font-size:28px;line-height:1.1;font-weight:850;letter-spacing:-1.2px;color:#173e43;}
.brandname span {color:#16958a;}
.brandtag {font-size:13px;color:#71858a;margin-top:6px;}
.brandpill {font-size:10px;letter-spacing:1px;font-weight:750;color:#14786f;background:#e5f5ef;border:1px solid #cfe9df;padding:9px 12px;border-radius:999px;white-space:nowrap;}
div[role="radiogroup"] {gap:8px;background:#edf5f2;padding:7px;border-radius:14px;border:1px solid #e0ebe6;}
div[role="radiogroup"] label {background:transparent;border-radius:10px;padding:8px 14px;}
div[role="radiogroup"] label:has(input:checked) {background:#ffffff;box-shadow:0 2px 8px rgba(31,82,70,.08);}
div[role="radiogroup"] label p {font-weight:650;color:#35565a;}
.stApp [data-testid="stVerticalBlock"] > div:has(> [data-testid="stHorizontalBlock"]) {min-width:0;}
.tool-card {height:100%;background:#fff;border:1px solid #e3eee9;border-radius:18px;padding:20px;box-shadow:0 6px 20px rgba(35,78,66,.045);transition:all .2s ease;}
.tool-card:hover {transform:translateY(-3px);box-shadow:0 12px 26px rgba(35,78,66,.09);border-color:#c7e4d9;}
.tool-icon {width:42px;height:42px;border-radius:13px;display:flex;align-items:center;justify-content:center;background:#e8f6f1;color:#168b83;font-size:21px;margin-bottom:13px;}
.tool-title {font-size:17px;font-weight:750;color:#24434a;margin-bottom:5px;}
.tool-desc {font-size:13px;color:#71858a;line-height:1.5;}
@media(max-width:700px){.brandbar{padding:16px;border-radius:15px;align-items:flex-start;flex-direction:column}.brandname{font-size:24px}.brandpill{font-size:9px}div[role="radiogroup"]{overflow-x:auto;flex-wrap:nowrap}div[role="radiogroup"] label{white-space:nowrap;padding:7px 10px}}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="brandbar">
  <div><div class="brandname">IGGL <span>E&I</span> TOOLS</div>
  <div class="brandtag">A practical workspace for operations & maintenance</div></div>
  <div class="brandpill">DESIGNED BY T. RABHA</div>
</div>
""", unsafe_allow_html=True)

PAGES = ["Home", "Instrumentation", "Electrical", "Telecom", "Audit Trail"]
if "active_page" not in st.session_state:
    st.session_state.active_page = "Home"
page = st.radio("Navigate", PAGES, horizontal=True, key="active_page", label_visibility="collapsed")

def result(label, value):
    st.metric(label, value)

def instrumentation():
    st.header("Instrumentation")
    tabs = st.tabs(["4–20 mA", "Pt100", "Pressure", "Master / DUT", "Five-point calibration"])
    with tabs[0]:
        st.subheader("4–20 mA to engineering-unit converter")
        lrv = st.number_input("LRV", value=0.0); urv = st.number_input("URV", value=100.0)
        ma = st.number_input("Measured signal (mA)", value=12.0)
        if st.button("Convert signal"):
            if urv <= lrv: st.error("URV must be greater than LRV.")
            else:
                eng = lrv + (ma - 4) / 16 * (urv - lrv)
                result("Engineering value", f"{eng:.5f}")
                st.write("Signal status:", "Within 4–20 mA" if 4 <= ma <= 20 else "Outside 4–20 mA range")
    with tabs[1]:
        st.subheader("Pt100 – IEC 60751 nominal CVD")
        temp = st.number_input("Temperature (°C)", value=100.0)
        if st.button("Calculate Pt100 resistance"):
            A, B, C, R0 = 3.9083e-3, -5.775e-7, -4.183e-12, 100.0
            r = R0 * (1 + A*temp + B*temp**2) if temp >= 0 else R0*(1 + A*temp + B*temp**2 + C*(temp-100)*temp**3)
            result("Nominal resistance", f"{r:.5f} Ω")
            st.caption("Nominal IEC 60751 Callendar–Van Dusen relationship; verify sensor class and applicable temperature range.")
    with tabs[2]:
        st.subheader("Pressure conversion")
        kg = st.number_input("Pressure (kgf/cm²)", value=10.0)
        atm = st.number_input("Atmospheric pressure (bar)", value=1.01325)
        if st.button("Convert pressure"):
            barg = kg * 0.980665
            result("Pressure", f"{barg:.5f} bar")
            result("Absolute pressure (if input is gauge)", f"{barg + atm:.5f} bara")
    with tabs[3]:
        st.subheader("Master calibrator vs DUT accuracy")
        master = st.number_input("Master accuracy (% of same basis)", min_value=0.0001, value=0.1)
        dut = st.number_input("DUT accuracy (% of same basis)", min_value=0.0001, value=0.25)
        if st.button("Check 2:1 accuracy ratio"):
            ratio = dut / master
            result("DUT / master accuracy ratio", f"{ratio:.2f}:1")
            (st.success if ratio >= 2 else st.error)("PASS – meets 2:1 criterion" if ratio >= 2 else "FAIL – master is not at least twice as accurate.")
    with tabs[4]:
        st.subheader("Five-point calibration error analysis")
        tolerance = st.number_input("Permissible error (% span)", min_value=0.0, value=0.5)
        errors = {}
        cols = st.columns(5)
        for col, point in zip(cols, [0, 25, 50, 75, 100]):
            with col: errors[point] = st.number_input(f"{point}% point error (% span)", value=0.0, key=f"err_{point}")
        if st.button("Evaluate five-point calibration"):
            passed = True
            for point, error in errors.items():
                ok = abs(error) <= tolerance
                passed &= ok
                st.write(f"{point}% point: {error:.4f}% span — {'PASS' if ok else 'FAIL'}")
            (st.success if passed else st.error)("Overall result: PASS" if passed else "Overall result: FAIL")

def electrical():
    st.header("Electrical")
    tabs = st.tabs(["UPS / battery autonomy", "DC cable voltage drop", "Single-phase power"])
    with tabs[0]:
        load = st.number_input("DC load (W)", min_value=0.1, value=500.0)
        voltage = st.number_input("Battery voltage (V)", min_value=0.1, value=48.0)
        capacity = st.number_input("Battery capacity (Ah)", min_value=0.1, value=200.0)
        usable = st.number_input("Usable capacity fraction", min_value=0.01, max_value=1.0, value=0.8)
        efficiency = st.number_input("Conversion efficiency", min_value=0.01, max_value=1.0, value=0.9)
        if st.button("Calculate battery autonomy"):
            result("Estimated autonomy", f"{voltage*capacity*usable*efficiency/load:.2f} h")
            st.caption("Energy approximation only. Apply battery discharge curves, ageing, temperature, rate and manufacturer derating.")
    with tabs[1]:
        current = st.number_input("Load current (A)", min_value=0.0, value=10.0)
        length = st.number_input("One-way cable length (m)", min_value=0.0, value=100.0)
        area = st.number_input("Conductor area (mm²)", min_value=0.001, value=6.0)
        rho = st.number_input("Conductor resistivity (Ω·mm²/m)", min_value=0.000001, value=0.0175, format="%.6f")
        system_v = st.number_input("System voltage (V)", min_value=0.1, value=24.0)
        if st.button("Calculate cable voltage drop"):
            resistance = rho * 2 * length / area
            drop = current * resistance
            result("Loop resistance", f"{resistance:.5f} Ω")
            result("Voltage drop", f"{drop:.4f} V ({drop/system_v*100:.3f}%)")
    with tabs[2]:
        voltage = st.number_input("AC voltage (V)", min_value=0.0, value=230.0)
        current = st.number_input("AC current (A)", min_value=0.0, value=5.0)
        pf = st.number_input("Power factor", min_value=0.0, max_value=1.0, value=0.9)
        if st.button("Calculate AC power"):
            result("Active power", f"{voltage*current*pf:.2f} W")
            result("Apparent power", f"{voltage*current:.2f} VA")

def telecom():
    st.header("Telecom")
    tabs = st.tabs(["OFC link budget", "Network performance", "CCTV / IP phone bandwidth"])
    with tabs[0]:
        length = st.number_input("Fiber length (km)", min_value=0.0, value=50.0)
        attenuation = st.number_input("Fiber attenuation (dB/km)", min_value=0.0, value=0.25)
        splices = st.number_input("Number of splices", min_value=0, value=10)
        splice_loss = st.number_input("Loss per splice (dB)", min_value=0.0, value=0.1)
        connector = st.number_input("Total connector loss (dB)", min_value=0.0, value=1.0)
        margin = st.number_input("Engineering margin (dB)", min_value=0.0, value=3.0)
        if st.button("Calculate OFC link budget"):
            loss = length*attenuation + splices*splice_loss + connector
            result("Calculated link loss", f"{loss:.2f} dB")
            result("Required optical budget including margin", f"{loss+margin:.2f} dB")
    with tabs[1]:
        sent = st.number_input("Packets sent", min_value=1, value=10000)
        lost = st.number_input("Packets lost", min_value=0, value=2)
        latency = st.number_input("Average latency (ms)", min_value=0.0, value=12.0)
        jitter = st.number_input("Jitter (ms)", min_value=0.0, value=1.5)
        if st.button("Evaluate network performance"):
            result("Packet loss", f"{lost/sent*100:.4f}%")
            result("Latency / jitter", f"{latency:.2f} ms / {jitter:.2f} ms")
    with tabs[2]:
        cameras = st.number_input("Number of CCTV cameras", min_value=0, value=12)
        camera_bw = st.number_input("Mbps per camera", min_value=0.0, value=4.0)
        phones = st.number_input("Number of IP phones", min_value=0, value=10)
        phone_bw = st.number_input("Mbps per phone", min_value=0.0, value=0.1)
        overhead = st.number_input("Overhead / headroom factor", min_value=1.0, value=1.2)
        if st.button("Calculate bandwidth requirement"):
            result("Estimated aggregate bandwidth", f"{(cameras*camera_bw+phones*phone_bw)*overhead:.2f} Mbps")

def audit_trail():
    st.header("Audit Trail")
    if "audit_entries" not in st.session_state:
        st.session_state.audit_entries = []
    with st.form("audit_form", clear_on_submit=True):
        department = st.selectbox("Department", ["Gas Engineering", "Instrumentation", "Electrical", "Telecom"])
        tag = st.text_input("Station / equipment tag")
        observation = st.text_area("Observation / activity")
        submitted = st.form_submit_button("Add audit entry")
    if submitted:
        st.session_state.audit_entries.append({
            "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
            "department": department, "tag": tag, "observation": observation
        })
        st.success("Entry added to this session.")
    entries = st.session_state.audit_entries
    if entries:
        st.dataframe(entries, use_container_width=True)
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=["timestamp", "department", "tag", "observation"])
        writer.writeheader(); writer.writerows(entries)
        st.download_button("Export audit trail as CSV", buffer.getvalue(), "IGGL_Audit_Trail.csv", "text/csv")
        if st.button("Clear session log"):
            st.session_state.audit_entries = []
            st.rerun()
    st.caption("Session-only log. It is not persistent, tamper-evident or a controlled records system.")

if page == "Home":
    st.markdown("## Welcome")
    st.markdown("Select a workspace to get started.")
    cards = [
        ("🎛️", "Instrumentation", "Signal conversion, RTD, pressure and calibration tools."),
        ("⚡", "Electrical", "Battery autonomy, cable voltage drop and power calculations."),
        ("🌐", "Telecom", "OFC link budget, network performance and bandwidth."),
        ("📋", "Audit Trail", "Record observations and export your session log.")
    ]
    cols = st.columns(2, gap="large")
    for col, (icon, name, desc) in zip(cols, cards):
        with col:
            st.markdown(f'<div class="tool-card"><div class="tool-icon">{icon}</div><div class="tool-title">{name}</div><div class="tool-desc">{desc}</div></div>', unsafe_allow_html=True)
            if st.button(f"Open {name} →", key=f"open_{name}", use_container_width=True):
                st.session_state.active_page = name
                st.rerun()
    st.markdown("")
    st.caption("Choose a department above or open a workspace card.")
elif page == "Instrumentation":
    instrumentation()
elif page == "Electrical":
    electrical()
elif page == "Telecom":
    telecom()
elif page == "Audit Trail":
    audit_trail()

st.divider()
st.caption("IGGL E&I TOOLS  ·  Designed by T. Rabha")
