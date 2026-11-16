"""ISO 6976:2016 calculation subset for the IGGL E&I TOOLS gas component list.

This module is a Python adaptation of the published GPL-3.0-or-later clean-room
implementation ISO6976.2016 by Ruediger Forster (2026), using its published
component constants and equations. Original project: https://github.com/RuedigerForster/ISO_6976
The application must be distributed under GPL-3.0-or-later when this module is included.

Scope: methane, ethane, propane, i-/n-butane, i-/n-pentane, n-hexane,
N2, CO2, H2, H2S, O2, CO and He. This is not a full 60-component ISO table.
Reference-condition limits are enforced. Results are not certified for custody
transfer until validated against the licensed ISO 6976:2016 Annex D examples
and an independently verified reference implementation.
"""
from __future__ import annotations
import math

R = 8.3144621                 # J/(mol K)
P_REF_KPA = 101.325
M_AIR = 28.96546               # kg/kmol
Z_AIR = {0.0: 0.999419, 15.0: 0.999595, 15.55: 0.999601, 20.0: 0.999645}

# Per-component data ordered to match the app's gas input names.
# M [kg/kmol], hydrogen atom count, s_i at (0, 15, 15.55, 20 C),
# ideal gross CV at (0, 15, 15.55, 20, 25 C) [kJ/mol].
DATA = {
    "Methane":  (16.04246, 4, (0.04886,0.04452,0.04437,0.04317), (892.92,891.51,891.46,891.05,890.58)),
    "Ethane":   (30.06904, 6, (0.0997,0.0919,0.0916,0.0895), (1564.35,1562.14,1562.06,1561.42,1560.69)),
    "Propane":  (44.09562, 8, (0.1465,0.1344,0.1340,0.1308), (2224.03,2221.10,2220.99,2220.13,2219.17)),
    "i-Butane": (58.12220,10, (0.1885,0.1722,0.1717,0.1673), (2874.21,2870.58,2870.45,2869.39,2868.20)),
    "n-Butane": (58.12220,10, (0.2022,0.1840,0.1834,0.1785), (2883.35,2879.76,2879.63,2878.58,2877.40)),
    "i-Pentane":(72.14878,12, (0.2458,0.2251,0.2244,0.2189), (3536.01,3531.68,3531.52,3530.25,3528.83)),
    "n-Pentane":(72.14878,12, (0.2586,0.2361,0.2354,0.2295), (3542.91,3538.60,3538.45,3537.19,3535.77)),
    "Hexane":   (86.17536,14, (0.3319,0.3001,0.2990,0.2907), (4203.24,4198.24,4198.06,4196.60,4194.95)),
    "Nitrogen": (28.01340, 0, (0.0214,0.0170,0.0169,0.0156), (0,0,0,0,0)),
    "CO₂":      (44.00950, 0, (0.0821,0.0752,0.0749,0.0730), (0,0,0,0,0)),
    "Hydrogen": (2.01588, 2, (-0.01,-0.01,-0.01,-0.01), (286.64,286.15,286.13,285.99,285.83)),
    "H₂S":      (34.08088, 2, (0.1006,0.0923,0.0920,0.0898), (562.93,562.38,562.36,562.19,562.01)),
    "Oxygen":   (31.99880, 0, (0.0311,0.0276,0.0275,0.0265), (0,0,0,0,0)),
    "CO":       (28.01010, 0, (0.0258,0.0217,0.0215,0.0203), (282.80,282.91,282.91,282.95,282.98)),
    "Helium":   (4.002602,0, (-0.01,-0.01,-0.01,-0.01), (0,0,0,0,0)),
}
T_S = (0.0, 15.0, 15.55, 20.0)
T_HC = (0.0, 15.0, 15.55, 20.0, 25.0)
L_VAP = (45.064, 44.431, 44.408, 44.222, 44.013)  # kJ/mol


def _nearest_index(value: float, choices: tuple[float, ...], label: str) -> int:
    for i, c in enumerate(choices):
        if abs(value-c) < 1e-6:
            return i
    raise ValueError(f"{label} must be one of: {', '.join(map(str, choices))} °C")


def calculate_iso6976(composition_pct: dict[str, float], reference_temperature_c: float = 15.0,
                       combustion_temperature_c: float = 25.0, reference_pressure_kpa: float = 101.325) -> dict:
    """Calculate ISO 6976 properties at stated reference conditions.

    Composition must be mol %. This module deliberately does not normalize it.
    """
    if set(composition_pct) - set(DATA):
        raise ValueError("One or more components are not supported by this ISO 6976 subset.")
    total = sum(float(v) for v in composition_pct.values())
    if any((not math.isfinite(float(v)) or float(v) < 0) for v in composition_pct.values()):
        raise ValueError("Mole percentages must be finite and non-negative.")
    if abs(total - 100.0) > 0.001:
        raise ValueError(f"Composition totals {total:.5f} mol %, not 100.00000 mol %. No normalization is applied.")
    ks = _nearest_index(reference_temperature_c, T_S, "Volume reference temperature")
    kh = _nearest_index(combustion_temperature_c, T_HC, "Combustion temperature")
    if not 90.0 <= reference_pressure_kpa <= 110.0:
        raise ValueError("ISO 6976 volume reference pressure must be within 90–110 kPa.")

    x = {k: float(v)/100.0 for k, v in composition_pct.items()}
    molar_mass = sum(x[k] * DATA[k][0] for k in DATA)
    sum_s = sum(x[k] * DATA[k][2][ks] for k in DATA)
    z_ref = 1.0 - (reference_pressure_kpa/P_REF_KPA) * sum_s**2
    if z_ref <= 0.9:
        raise ValueError(f"ISO 6976 volume-basis applicability check failed: Z at reference conditions is {z_ref:.6f} (must be > 0.9).")

    h_gross = sum(x[k] * DATA[k][3][kh] for k in DATA)
    sum_h_atoms = sum(x[k] * DATA[k][1] for k in DATA)
    h_net = h_gross - 0.5 * sum_h_atoms * L_VAP[kh]
    if h_gross <= 0 or h_net <= 0:
        raise ValueError("Calculated calorific value is non-positive; check composition and supported components.")

    t_k = reference_temperature_c + 273.15
    molar_volume = z_ref * R * t_k / (reference_pressure_kpa * 1000.0)  # m3/mol
    density = (reference_pressure_kpa * 1000.0) * (molar_mass/1000.0) / (z_ref * R * t_k)
    z_air = Z_AIR[reference_temperature_c]
    air_density = (reference_pressure_kpa * 1000.0) * (M_AIR/1000.0) / (z_air * R * t_k)
    relative_density = density / air_density
    gcv_vol = (h_gross / molar_volume) / 1000.0  # MJ/m3
    ncv_vol = (h_net / molar_volume) / 1000.0
    gcv_mass = h_gross / molar_mass             # MJ/kg
    ncv_mass = h_net / molar_mass
    wobbe_gross = gcv_vol / math.sqrt(relative_density)
    wobbe_net = ncv_vol / math.sqrt(relative_density)
    return {
        "molar_mass_kg_kmol": molar_mass,
        "gcv_molar_kj_mol": h_gross,
        "ncv_molar_kj_mol": h_net,
        "gcv_mass_mj_kg": gcv_mass,
        "ncv_mass_mj_kg": ncv_mass,
        "gcv_vol_mj_m3": gcv_vol,
        "ncv_vol_mj_m3": ncv_vol,
        "density_kg_m3": density,
        "relative_density": relative_density,
        "gcv_wobbe_mj_m3": wobbe_gross,
        "ncv_wobbe_mj_m3": wobbe_net,
        "z_reference": z_ref,
        "reference_temperature_c": reference_temperature_c,
        "combustion_temperature_c": combustion_temperature_c,
        "reference_pressure_kpa": reference_pressure_kpa,
        "status": "CALCULATED — independent Annex D/reference validation still required before operational or custody-transfer use",
    }
