import unittest
from iso6976_engine import calculate_iso6976

class ISO6976EngineTests(unittest.TestCase):
    def setUp(self):
        self.mix = {"Methane":90,"Ethane":5,"Propane":2,"i-Butane":0,"n-Butane":0,
                    "i-Pentane":0,"n-Pentane":0,"Hexane":0,"Nitrogen":2,"CO₂":1,
                    "Hydrogen":0,"H₂S":0,"Oxygen":0,"CO":0,"Helium":0}

    def test_default_mixture_returns_positive_properties(self):
        r = calculate_iso6976(self.mix, 15.0, 25.0, 101.325)
        for key in ("molar_mass_kg_kmol", "gcv_molar_kj_mol", "ncv_molar_kj_mol",
                    "density_kg_m3", "relative_density", "gcv_vol_mj_m3", "ncv_vol_mj_m3"):
            self.assertGreater(r[key], 0, key)
        self.assertGreater(r["z_reference"], 0.9)

    def test_composition_not_normalized(self):
        mix = dict(self.mix); mix["Methane"] = 89
        with self.assertRaises(ValueError):
            calculate_iso6976(mix)

    def test_reference_temperature_restricted(self):
        with self.assertRaises(ValueError):
            calculate_iso6976(self.mix, 10.0, 25.0, 101.325)

    def test_reference_pressure_restricted(self):
        with self.assertRaises(ValueError):
            calculate_iso6976(self.mix, 15.0, 25.0, 120.0)

if __name__ == "__main__":
    unittest.main()
