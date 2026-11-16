# IGGL E&I TOOLS v2.1 – Streamlit Website

**Designed by T. Rabha**

## Deploy as a website (Streamlit Community Cloud)

This folder is the deployment root.

1. Create a GitHub repository, e.g. `iggl-ei-tools`.
2. Upload all files and folders from this `website` folder to the repository root.
3. Open https://share.streamlit.io/ and sign in with GitHub.
4. Select **Create app** and choose the repository, branch, and `app.py` as the main file.
5. Deploy. Streamlit will install dependencies from `requirements.txt`.
6. Share the generated `https://....streamlit.app` URL.

You need to use your own GitHub and Streamlit accounts. I cannot publish to your accounts or generate a live public URL without access/authorization.

## Run locally

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Important operating notes

- Website access requires internet. For station use with no connectivity, run the same app locally on a laptop on its own machine; this does not create a phone-installable offline app.
- Streamlit Community Cloud may restart/redeploy the app. The existing Audit Trail is session-based and is not durable across sessions/restarts. Do not use it as an official controlled audit record.
- AGA-8 DETAIL is connected through `pyaga8`; the NIST official verification suite has not yet been executed in this package.
- ISO 6976 supports only the 15 displayed components, not the complete ISO 6976 component table. It has not yet passed a documented Annex D regression.
- Do not use the gas property outputs for custody transfer, fiscal metering, billing, contract energy determination, or operational set-point decisions until independent validation and formal approval.
- C6+ is not represented by pure n-hexane unless an approved characterization/splitting method is defined.
