IGGL E&I TOOLS v2.1 – Python / Streamlit
Designed by T. Rabha

WHAT CHANGED
- Added AGA 8 2017 Part 1 DETAIL integration through pyaga8, a Python binding to a Rust port of NIST's AGA8 code.
- Added a Python ISO 6976:2016 calculation module for the component subset displayed in the Gas Properties screen.
- AGA 8 operating-condition Z and ISO 6976 reference-condition Z are kept separate.
- ISO 6976 outputs include molar/mass/volume GCV and NCV, density, relative density, gross/net Wobbe index and molar mass.
- Composition is never silently normalized. The input must sum to 100.000 mol % within 0.001 mol %.
- ISO reference temperature and pressure applicability checks are enforced.

INSTALLATION (Windows)
1. Install Python 3.10 or later.
2. Extract this ZIP into a folder.
3. Open Command Prompt in the extracted folder.
4. Run:
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   streamlit run app.py

AGA 8 ENGINE
The AGA 8 adapter uses pyaga8. Install requirements while connected to the internet. The app intentionally raises an error if the DETAIL engine is unavailable or its compressibility factor cannot be read. No Peng–Robinson or other substitute EOS is used.

IMPORTANT TECHNICAL LIMITATIONS
- AGA 8 integration is wired to pyaga8's DETAIL state API, but this package has not yet executed the NIST official verification suite in this build environment. Verify output against the official NIST AGA8 supplementary test data before operational use.
- The ISO 6976 Python engine currently supports the 15 components shown in the app, not the complete 60-component ISO Table A.2. Hexane is represented as n-hexane; this is not a valid substitute for unresolved C6+ unless an approved pseudo-component/splitting method is defined.
- The ISO module includes calculation and input checks but has not yet passed a documented regression against all ISO 6976:2016 Annex D worked examples or an independently verified reference implementation.
- Therefore these calculations are for engineering development / review only. Do not use for custody transfer, fiscal metering, billing, contract energy determination or operational set-point decisions until independent validation, uncertainty review and formal approval are completed.
- Use the applicable licensed, controlled editions of AGA 8 and ISO 6976. This software does not reproduce the full standards.

TESTS
Run:
   python -m unittest -v
The current unit tests cover ISO input validation and internal sanity checks only. They are not standards conformance tests.

LICENSING / ATTRIBUTION
The ISO 6976 Python adaptation is based on the published component data and calculation structure of ISO6976.2016 by Ruediger Forster, https://github.com/RuedigerForster/ISO_6976, licensed GPL-3.0-or-later. This distribution therefore includes GPL-3.0 license terms; see LICENSE-GPL-3.0.txt.
pyaga8 is a separate third-party package; see https://github.com/equinor/pyaga8 and its MIT license. Install it from PyPI via requirements.txt.
