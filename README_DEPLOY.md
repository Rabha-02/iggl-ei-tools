# IGGL E&I TOOLS – Website

Designed by T. Rabha.

## Publish with Streamlit Community Cloud
1. Create a GitHub repository.
2. Upload all files in this folder to the repository root.
3. Sign in at https://share.streamlit.io/ using GitHub.
4. Create an app, select the repository and `app.py`, then deploy.
5. Share the generated website URL.

## Run locally
```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py
```

## Included workspaces
- Instrumentation
- Electrical
- Telecom
- Audit Trail

Gas Engineering has been removed from the navigation and application.
The home page provides simple workspace cards and responsive navigation.

Audit Trail is session-based and can be exported as CSV. It is not persistent or tamper-evident.
