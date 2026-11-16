"""AGA 8 2017 Part 1 DETAIL adapter using pyaga8 (NIST AGA8 code port)."""
from __future__ import annotations

AGA8_COMPONENT_MAP = {
    "Methane": "methane", "Nitrogen": "nitrogen", "CO₂": "carbon_dioxide",
    "Ethane": "ethane", "Propane": "propane", "i-Butane": "isobutane",
    "n-Butane": "n_butane", "i-Pentane": "isopentane", "n-Pentane": "n_pentane",
    "Hexane": "hexane", "Hydrogen": "hydrogen", "H₂S": "hydrogen_sulfide",
    "Oxygen": "oxygen", "CO": "carbon_monoxide", "Helium": "helium",
}


def calculate_aga8_detail(composition_pct: dict[str, float], pressure_bar_abs: float, temperature_c: float) -> dict:
    """Calculate DETAIL compressibility at P,T. pyaga8 uses kPa and kelvin."""
    try:
        import pyaga8
    except ImportError as exc:
        raise RuntimeError("AGA-8 engine is not installed. Run: pip install pyaga8") from exc

    total = sum(float(v) for v in composition_pct.values())
    if abs(total - 100.0) > 0.001:
        raise ValueError(f"Composition totals {total:.5f} mol %, not 100.00000 mol %. No normalization is applied.")
    if pressure_bar_abs <= 0 or temperature_c <= -273.15:
        raise ValueError("Pressure must be positive absolute and temperature must be above absolute zero.")

    comp = pyaga8.Composition()
    for label, attr in AGA8_COMPONENT_MAP.items():
        value = float(composition_pct.get(label, 0.0)) / 100.0
        try:
            setattr(comp, attr, value)
        except Exception as exc:
            raise RuntimeError(f"pyaga8 component mapping failed for {label} ({attr}): {exc}") from exc

    detail = pyaga8.Detail()
    detail.set_composition(comp)
    detail.temperature = float(temperature_c) + 273.15
    detail.pressure = float(pressure_bar_abs) * 100.0  # 1 bar = 100 kPa
    detail.calc_density()

    z = None
    for attr in ("z", "compressibility_factor", "compressibility"):
        if hasattr(detail, attr):
            candidate = getattr(detail, attr)
            candidate = candidate() if callable(candidate) else candidate
            if isinstance(candidate, (int, float)):
                z = float(candidate)
                break
    if z is None:
        raise RuntimeError("The installed pyaga8 build did not expose a recognized compressibility-factor property. No substitute EOS was used.")
    if not 0.0 < z < 2.0:
        raise RuntimeError(f"AGA-8 returned an implausible compressibility factor: {z}")
    return {
        "z": z,
        "pressure_bar_abs": pressure_bar_abs,
        "temperature_c": temperature_c,
        "engine": "AGA 8 2017 Part 1 DETAIL via pyaga8 / NIST AGA8 code port",
        "density_raw": getattr(detail, "d", None),
        "validation_status": "Engine connected; independent NIST verification suite has not yet been executed in this package build.",
    }
