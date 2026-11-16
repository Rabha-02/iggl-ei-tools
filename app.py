import math
import csv
import io
from datetime import datetime
import streamlit as st

st.set_page_config(page_title="IGGL E&I TOOLS v2.1", page_icon="🛠️", layout="wide")
st.markdown("""
<style>
.stApp {background:#0b1220;color:#e8eef7}
[data-testid="stSidebar"] {background:#101c2e}
h1,h2,h3 {color:#e8eef7}
div[data-testid="stMetric"] {background:#111e31;padding:12px;border-radius:10px}
</style>
""", unsafe_allow_html=True)

st.title("IGGL E&I TOOLS")
st.caption("Version 2.1 · Designed by T. Rabha")
st.info("Python-based local engineering utility. Verify all results against approved project design documents, controlled standards and manufacturer data before operational use.")

PAGES = ["Dashboard", "Gas Engineering", "Instrumentation", "Electrical", "Telecom", "Audit Trail"]
page = st.sidebar.radio("Department", PAGES)

def result(label, value):
    st.metric(label, value)

def gas_composition():
    from iso6976_engine import calculate_iso6976
    from aga8_engine import calculate_aga8_detail

    st.subheader("Gas composition – AGA 8 DETAIL and ISO 6976")
    st.write("Enter gas composition on a molar-percent basis. The two standards are applied independently: AGA 8 DETAIL for operating-condition Z; ISO 6976 for combustion and reference-condition properties.")
    components = ["Methane", "Ethane", "Propane", "i-Butane", "n-Butane", "i-Pentane",
                  "n-Pentane", "Hexane", "Nitrogen", "CO₂", "Hydrogen", "H₂S", "Oxygen", "CO", "Helium"]
    defaults = [90, 5, 2, 0, 0, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0]
    cols = st.columns(3)
    composition = {}
    for i, (name, default) in enumerate(zip(components, defaults)):
        with cols[i % 3]:
            composition[name] = st.number_input(f"{name} (mol %)", min_value=0.0, max_value=100.0,
                                                  value=float(default), step=0.01, key=f"gas_{name}")
    total = sum(composition.values())
    c1, c2 = st.columns(2)
    c1.metric("Composition total", f"{total:.4f} mol %")
    c2.metric("Composition check", "PASS" if abs(total - 100) <= 0.001 else "CHECK")

    st.markdown("**AGA 8 operating conditions**")
    a1, a2 = st.columns(2)
    with a1:
        p = st.number_input("Operating pressure (bar absolute)", min_value=0.001, value=50.0, key="aga8_p")
    with a2:
        t = st.number_input("Operating temperature (°C)", value=25.0, key="aga8_t")

    st.markdown("**ISO 6976 reference conditions**")
    i1, i2, i3 = st.columns(3)
    with i1:
        bp = st.number_input("Volume reference pressure (kPa absolute)", min_value=90.0, max_value=110.0, value=101.325, key="iso_bp")
    with i2:
        bt = st.selectbox("Volume reference temperature (°C)", [0.0, 15.0, 15.55, 20.0], index=1, key="iso_bt")
    with i3:
        ct = st.selectbox("Combustion temperature (°C)", [0.0, 15.0, 15.55, 20.0, 25.0], index=4, key="iso_ct")

    st.caption("No composition normalization is performed. The entered mole percentages must sum to 100.000% (±0.001%).")
    if st.button("Calculate AGA 8 DETAIL + ISO 6976", type="primary"):
        if abs(total - 100) > 0.001:
            st.error(f"Composition totals {total:.4f} mol %. Correct the composition before calculating.")
            return
        # AGA-8 DETAIL at actual operating pressure and temperature
        try:
            aga = calculate_aga8_detail(composition, p, t)
            st.markdown("#### AGA 8 2017 Part 1 DETAIL")
            st.metric("Compressibility factor Z (operating conditions)", f"{aga['z']:.7f}")
            st.caption(f"{aga['engine']} · {aga['validation_status']}")
        except Exception as exc:
            st.error(f"AGA 8 DETAIL calculation unavailable: {exc}")

        # ISO 6976 calculations at declared reference conditions
        try:
            iso = calculate_iso6976(composition, bt, ct, bp)
            st.markdown("#### ISO 6976:2016")
            st.caption("Combustion properties and density are calculated independently of the AGA 8 operating-condition Z.")
            rows = [
                ("Molar mass", f"{iso['molar_mass_kg_kmol']:.5f} kg/kmol"),
                ("Gross calorific value – molar", f"{iso['gcv_molar_kj_mol']:.4f} kJ/mol"),
                ("Net calorific value – molar", f"{iso['ncv_molar_kj_mol']:.4f} kJ/mol"),
                ("Gross calorific value – mass", f"{iso['gcv_mass_mj_kg']:.5f} MJ/kg"),
                ("Net calorific value – mass", f"{iso['ncv_mass_mj_kg']:.5f} MJ/kg"),
                ("Gross calorific value – volume", f"{iso['gcv_vol_mj_m3']:.5f} MJ/m³"),
                ("Net calorific value – volume", f"{iso['ncv_vol_mj_m3']:.5f} MJ/m³"),
                ("Density", f"{iso['density_kg_m3']:.6f} kg/m³"),
                ("Relative density / specific gravity", f"{iso['relative_density']:.6f}"),
                ("Gross Wobbe index", f"{iso['gcv_wobbe_mj_m3']:.5f} MJ/m³"),
                ("Net Wobbe index", f"{iso['ncv_wobbe_mj_m3']:.5f} MJ/m³"),
                ("ISO reference-condition Z", f"{iso['z_reference']:.7f}"),
            ]
            st.table({"Property": [r[0] for r in rows], "Calculated value": [r[1] for r in rows]})
            st.warning(iso["status"])
        except Exception as exc:
            st.error(f"ISO 6976 calculation not performed: {exc}")

    with st.expander("Calculation method and limitations"):
        st.markdown("""
        - **AGA 8:** `pyaga8` adapter to the NIST AGA8 code port; DETAIL equation only. Pressure is converted from bar absolute to kPa and temperature from °C to K.
        - **ISO 6976:** Separate ISO property calculation using the supported component subset in `iso6976_engine.py`. It does not use AGA 8 operating Z as a substitute for ISO reference-condition compression factor.
        - ISO volume-basis applicability is checked at the selected reference conditions (Z must be greater than 0.9); reference temperature and pressure restrictions are enforced.
        - The ISO engine currently supports the 15 components displayed above. It is not a full 60-component ISO Table A.2 implementation; unresolved C6+ must not be treated as pure n-hexane without an approved composition methodology.
        - **Validation status:** This integration has not yet passed a documented independent NIST AGA8 verification run or the ISO 6976:2016 Annex D regression suite. Do not use for custody transfer, billing, fiscal metering, or operational set-point decisions until independently verified and approved.
        """)

def gas_engineering():
    st.header("Gas Engineering")
    tab1, tab2, tab3, tab4 = st.tabs(["Gas properties", "Velocity", "Line pack", "Gas balance"])
    with tab1:
        gas_composition()
    with tab2:
        st.subheader("Gas velocity")
        q = st.number_input("Actual flow (m³/h)", min_value=0.0, value=10000.0)
        d = st.number_input("Internal diameter (mm)", min_value=0.01, value=500.0)
        if st.button("Calculate velocity"):
            area = math.pi * (d / 1000) ** 2 / 4
            velocity = (q / 3600) / area
            result("Gas velocity", f"{velocity:.4f} m/s")
    with tab3:
        st.subheader("Pipeline line pack – single segment")
        length = st.number_input("Pipeline length (km)", min_value=0.0, value=100.0)
        diameter = st.number_input("Internal diameter (mm)", min_value=0.01, value=500.0)
        pressure = st.number_input("Average absolute pressure (bara)", min_value=0.001, value=40.0)
        temp = st.number_input("Average gas temperature (°C)", value=25.0)
        z = st.number_input("Compressibility factor Z (enter validated value)", min_value=0.01, value=0.9)
        base_p = st.number_input("Base pressure (bara)", min_value=0.001, value=1.01325)
        base_t = st.number_input("Base temperature (K)", min_value=0.001, value=288.15)
        if st.button("Calculate line pack"):
            volume = math.pi * (diameter / 1000) ** 2 / 4 * length * 1000
            base_volume = volume * pressure / base_p * base_t / (temp + 273.15) / z
            result("Geometric pipeline volume", f"{volume:,.2f} m³")
            result("Approximate base-volume equivalent", f"{base_volume:,.2f} Sm³")
            st.caption("Uses user-entered Z. This is a single-segment ideal-gas conversion estimate, not a pressure-profile or AGA-8 calculation.")
    with tab4:
        st.subheader("Gas balance / unaccounted-for gas")
        incoming = st.number_input("Total input (Sm³)", min_value=0.0, value=100000.0)
        outgoing = st.number_input("Total output (Sm³)", min_value=0.0, value=98500.0)
        if st.button("Calculate gas balance"):
            ufg = incoming - outgoing
            result("Unaccounted-for gas", f"{ufg:,.2f} Sm³")
            result("UFG (% of input)", f"{(ufg / incoming * 100 if incoming else 0):.4f} %")

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

if page == "Dashboard":
    st.header("Engineering tools for pipeline O&M")
    st.write("Choose a department from the sidebar.")
    cols = st.columns(5)
    for col, name, desc in zip(cols, PAGES[1:], [
        "Gas properties, pipeline flow and balance", "4–20 mA, RTD and calibration",
        "UPS, cables and power", "OFC and network", "Session records and CSV export"
    ]):
        with col:
            st.markdown(f"**{name}**")
            st.caption(desc)
elif page == "Gas Engineering": gas_engineering()
elif page == "Instrumentation": instrumentation()
elif page == "Electrical": electrical()
elif page == "Telecom": telecom()
elif page == "Audit Trail": audit_trail()

st.divider()
st.caption("IGGL E&I TOOLS v2.1 · Designed by T. Rabha · Local Python/Streamlit application")
