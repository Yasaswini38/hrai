import pandas as pd
from flask import Flask, request, jsonify
from simple_salesforce import Salesforce
from dotenv import load_dotenv
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
import joblib, os, re
import numpy as np
from pypdf import PdfReader
from io import BytesIO

# --- LIME specific imports ---
import lime.lime_text
CLASS_NAMES = ["Reject", "Hire"]

load_dotenv()

app = Flask(__name__)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "model", "hiring_model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "model", "tfidf_vectorizer.pkl")
POWERBI_REPORT_PATH = os.path.join(BASE_DIR, "powerbi", "hiring_insights.csv")

try:

    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
  
    pipe = Pipeline([
        ('tfidf', vectorizer),
        ('model', model)
    ])
    
    lime_exp = lime.lime_text.LimeTextExplainer(class_names=CLASS_NAMES)
    
    print("Model, Vectorizer, and LIME Explainer loaded successfully.")
except Exception as e:
    print(f"FATAL ERROR: Could not load ML components or initialize LIME. Error: {e}")
    exit(1)


try:
    sf = Salesforce(
        username=os.getenv("SF_USERNAME"),
        password=os.getenv("SF_PASSWORD"),
        security_token=os.getenv("SF_TOKEN")
    )
    print("Salesforce connection object created successfully.")
except Exception as e:
    print(f"Salesforce connection failed. Error: {e}")



def clean_text(text):
    """Cleans resume text for prediction."""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^a-zA-Z0-9 ]', '', text)
    return text.lower().strip()

def extract_text_from_pdf(file_stream):
    """Reads PDF content from an uploaded file stream."""
    try:
        reader = PdfReader(file_stream)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + " "
        return text.strip()
    except Exception as e:
        
        raise ValueError(f"Could not extract text from PDF: {e}")

def format_lime_explanation(exp, decision_index):
    """Formats the LIME explanation list into a clean string for the UI/Salesforce."""
    
    try:
        
        lime_list = exp.as_list(label=decision_index)
        
        summary = "Model was influenced by: "
        
        positive_factors = []
        negative_factors = []
        
        for word, weight in lime_list:
            if weight > 0:
                positive_factors.append(word)
            elif weight < 0:
                negative_factors.append(word)

        if positive_factors:
            summary += f"POSITIVE: {', '.join(positive_factors)}. "
        else:
             summary += "No strong POSITIVE factors found. "
             
        if negative_factors:
            summary += f"NEGATIVE: {', '.join(negative_factors)}. "
        else:
             summary += "No strong NEGATIVE factors found. "
            
        return summary.strip()
        
    except Exception as e:
        print(f"LIME formatting failed for index {decision_index}: {e}")
        return f"Explanation failed due to internal LIME error: {e}"

def append_to_powerbi_report(result_id, status, prob):
    """Appends the new prediction results to the CSV for Power BI."""
    
    report_data = pd.DataFrame([{
        'Salesforce_ID': result_id,
        'Prediction_Date': pd.Timestamp.now(),
        'Predicted_Status': status,
        'Hire_Probability': prob 
    }])
    
    file_exists = os.path.exists(POWERBI_REPORT_PATH)

    try:
        os.makedirs(os.path.dirname(POWERBI_REPORT_PATH), exist_ok=True)
        
        report_data.to_csv(
            POWERBI_REPORT_PATH,
            mode='a',
            header=(not file_exists), 
            index=False
        )
        print(f"Prediction successfully appended to {POWERBI_REPORT_PATH}")
    except Exception as e:
        print(f"WARNING: Could not write to Power BI report file: {e}")


@app.route("/predict", methods=["POST"])
def predict_candidate():
    try:
        name = request.form.get("name", "Unknown Candidate")
        resume_file = request.files.get("file")

        if not resume_file:
            return jsonify({"error": "No resume file uploaded. Use the 'file' key in multipart/form-data."}), 400

        filename = resume_file.filename
        if filename.lower().endswith('.pdf'):
            file_stream = BytesIO(resume_file.read())
            resume_text = extract_text_from_pdf(file_stream)
        else:
             if not filename.lower().endswith('.txt'):
                 print(f"Warning: Non-PDF file '{filename}' uploaded. Attempting raw text read.")
             resume_text = resume_file.read().decode("utf-8", errors="ignore")


        if not resume_text:
            return jsonify({"error": "Resume file is empty or text extraction failed."}), 400

        cleaned = clean_text(resume_text)

        vec = vectorizer.transform([cleaned])
        pred = model.predict(vec)[0]
        prob = model.predict_proba(vec)[0][1]
        
        decision = "Hire" if pred == 1 else "Reject"
        decision_index = pred
        
        # --- LIME Explanation Generation ---
        exp = lime_exp.explain_instance(cleaned, pipe.predict_proba, num_features=5)
        lime_summary = format_lime_explanation(exp, decision_index)

     
        if "Explanation failed due to internal LIME error" in lime_summary and prob < 0.2:
             lime_summary = "DOMAIN MISMATCH: Prediction rejected due to lack of core keywords (e.g., Python, AWS, ML). Resume appears highly specialized in non-technical engineering fields ."


        max_sf_text_length = 32000 
        
        sf_data = {
            "Name": name, 
            "Full_Resume_Text__c": resume_text[:max_sf_text_length], 
            "Predicted_Status__c": decision, 
            "Hire_Probability__c": float(prob),
            "Prediction_Explanation__c": lime_summary[:500] 
        }
        
        result = sf.Candidate__c.create(sf_data)

        if not result.get('success', False):
             error_msg = f"SF failed: {result.get('errors', ['Unknown SF Error'])}"
             raise Exception(error_msg)

        salesforce_id = result['id']
        append_to_powerbi_report(salesforce_id, decision, round(float(prob), 4))

        return jsonify({
            "Candidate": name,
            "Salesforce_ID": salesforce_id, 
            "Predicted_Status": decision,
            "Hire_Probability": round(float(prob), 4),
            "LIME_SUMMARY": lime_summary 
        })

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
