# Smart Hiring Assistant (hrai)

A cloud-based resume screening and analytics platform integrating NLP, machine learning, Salesforce, Power BI, and automated communication tools—all in an intuitive Streamlit web app.

---

## Features

- Upload single or bulk resumes (PDF, TXT)
- Automated candidate fit prediction using NLP & ML (TF-IDF + classifier)
- Interpretable explanations (LIME) for every prediction
- Integration with Salesforce: candidates & predictions synced for real HR workflows
- Rejection/feedback email automation using secure Gmail SMTP
- Analytics dashboard integration via Power BI
- Bulk resume support (zip upload)
- Role-based credential management (env vars)

---

## Project Structure

- `streamlitapp.py` — Streamlit frontend app
- `smart_hiring_model.py` — ML/NLP backend API (Flask/FastAPI)
- `model/` — Saved classifier(s) and vectorizer(s) (joblib)
- `powerbi/` — Data CSV for analytics export
- `.env` — (Not in repo) secret keys for email, Salesforce, etc.

---

## Quickstart

### 1. Backend (API) - Railway

1. Link backend repo to [Railway](https://railway.app), set your start command:
   - Flask: `python smart_hiring_model.py`
   - FastAPI: `uvicorn smart_hiring_model:app --host 0.0.0.0 --port $PORT`
2. Set environment variables for Salesforce, email, etc.
3. Deploy! Note your public API URL (e.g. `https://xyz.up.railway.app/predict`)

### 2. Frontend (Streamlit) - Streamlit Cloud

1. Update `apiurl` in `streamlitapp.py`:
apiurl = "https://xyz.up.railway.app/predict"

text
2. Deploy to [Streamlit Cloud](https://streamlit.io/cloud).
3. Set secrets in Streamlit Cloud for email, API URLs, etc.

---

## ⚙️ Core API Flow

- `/predict` (POST): Single endpoint for uploading a resume, predicting, generating explanation, Salesforce sync, and Power BI logging.
- All logic for extraction, vectorization, prediction, and business integrations live behind a secure backend.

---

##  Security

- All credentials set via environment variables (never hardcoded).
- User uploads are handled securely.
- Error handling returns user-safe feedback when document reading/model inference fails.

---

## 📊 Integrations

- **Salesforce:** Candidate object creation and updates.
- **Power BI:** Pushes prediction results to CSV for dashboard analytics.
- **Email:** Automated rejection/feedback emails over Gmail SMTP.

---

## 📫 Contact

Raise issues or feature requests via GitHub or contact project maintainers.
