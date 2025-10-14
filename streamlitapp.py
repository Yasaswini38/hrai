import streamlit as st
import requests
import os
import smtplib
from email.message import EmailMessage
from PIL import Image
import zipfile
import io
import dotenv
dotenv.load_dotenv()
st.set_page_config(page_title="Smart Hiring Assistant", page_icon="🧸", layout="wide")


def send_rejection_mail(to_email, suggestions, sender=None):
    msg = EmailMessage()
    msg['Subject'] = "Regarding Your Job Application"
    msg['From'] = sender or os.getenv("MAIL_USERNAME") or "hr@mycompany.com"
    msg['To'] = to_email
    msg.set_content(
        f"Thank you for your interest in joining us! After careful review, we regret to inform you that we cannot proceed with your application.\n\n"
        f"Suggestions for future opportunities:\n\n{suggestions}\n\nBest wishes,\nHR Team"
    )
    smtp_user = os.getenv("MAIL_USERNAME")
    smtp_pass = os.getenv("MAIL_PASSWORD")
    smtp_server = os.getenv("MAIL_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("MAIL_PORT", 587))
    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(smtp_user, smtp_pass)
        smtp.send_message(msg)

# ---- Custom CSS for theme and button ----
st.markdown("""
<style>
    body { background: #181428 !important; }
    .stApp { background: linear-gradient(90deg,#f4f4fd 40%, #e6e0fe 100%);}
    .main-header { background: #fff; border-radius: 32px; padding: 32px 30px 24px 30px; margin-bottom: 24px; box-shadow: 0 8px 32px #cfcfff88; }
    .card { border-radius: 20px; padding: 22px; margin-bottom: 10px; box-shadow: 0 4px 20px #e3e6f971; position: relative; }
    .card-purple { background: #D8D5FF; }
    .card-green  { background: #E1FFB3; }
    .card-pink   { background: #FFD1DC; }
    .card-team   { background: #D9D7F1;}
    .bigscore { font-size: 2rem; font-weight: bold; color: #ae38ff;}
    .suggestion { background: #ffe7ffcc; padding: 15px; border-radius: 15px; margin: 12px 0;}
    .result-reject { color: #F94449; font-size: 1.1rem;}
    .result-hire { color: #26b37a; font-size: 1.1rem;}
    .cute-mascot-box {text-align:center;margin-top:10px;}
    div[data-testid="stButton"] button {
        background-color: #bdbdbd;
        color: #262626;
        border-radius: 12px;
        padding: 7px 16px;
        border: 0;
        font-size: 1.02rem;
        margin-top: 8px;
    }
    div[data-testid="stButton"] button:hover {
        background-color: #9e9e9e;
        color: #fff;
    }
    .form-black {
        background: #fff;
        border-radius: 20px;
        padding: 28px 24px 18px 24px;
        margin-bottom: 10px;
        box-shadow: 0 4px 20px #e3e6f971;
    }
</style>
""", unsafe_allow_html=True)

# ----- Header -----
st.markdown("""
<div class='main-header'>
    <div style='display:flex;align-items:center;gap:16px;flex-wrap:wrap;'>
      <span style='font-size:2.1rem;font-weight:bold;color:#131028;'>🌟 Because data-driven hiring shouldn’t be a luxury.</span>
    </div>
    <span style='color:#7371ee;font-weight:bold;font-size:1.09rem;'>Upload candidates and see insights instantly!</span>
</div>
""", unsafe_allow_html=True)

powerbi_url = "https://dietac-my.sharepoint.com/:u:/g/personal/218t1a4238_diet_ac_in/EYDTyBK0RcpEk8XIQpvCNJcBgBbQQTRBXvHnW-nwvVf-KA?e=gnYALO"

if "show_mail_form" not in st.session_state:
    st.session_state.show_mail_form = False

cols = st.columns([1.1,1.1,1])
with cols[0]:
    st.markdown(f"""
    <div class='card card-purple'>
        <span style='font-size:1.3rem;font-weight:600;color:#392B61;'>Barcode Data Feed</span><br>
        <span style='font-size:1rem;font-weight:400;;color:#12355B;'>Access Live Data <br></span>
        <a href="{powerbi_url}" target="_blank" style='text-decoration:none;'>
        <button style='background:#EFC3E6;color:#333;border-radius:12px;padding:7px 16px;border:0;margin-top:9px;font-size:1.07rem;'>
            Dashboards
        </button>
        </a>
        <img src='https://img.icons8.com/fluency/48/bar-chart.png'
        style='margin-top:10px;margin-bottom:8px;float:right;'/>
    </div>
    """, unsafe_allow_html=True)

with cols[1]:
    st.markdown("""
    <div class='card card-green' style='padding:28px 24px 18px 24px; border-radius:20px; box-shadow:0 4px 20px #e3e6f971; position:relative;'>
        <span style='font-size:1.3rem;font-weight:600;color:#355527;'>Send Rejection Mail</span><br>
        <span style='font-size:1rem;font-weight:400; color:#12355B;'>Quickly send a personalized rejection email.<br></span>
        <img src='https://img.icons8.com/color/24/000000/new-post.png' alt='Mail Icon' style='position:absolute; top:24px; right:24px;'/>
    </div>
    """, unsafe_allow_html=True)
    send_btn = st.button("Send Mail", key="mail_btn_in_card")

if send_btn:
    st.session_state.show_mail_form = True



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_PATH = os.path.join(BASE_DIR, "AVO.jpg")
img = Image.open(IMG_PATH)
img = img.resize((325, 150)) 
with cols[2]:
    st.image(img, use_container_width=True)

# ---- Display mail form below the second column ----
if st.session_state.show_mail_form:
    st.markdown("""
    <div class='card card-green' style='padding:28px 24px 18px 24px; border-radius:20px; margin-top:14px; box-shadow:0 4px 20px #e3e6f971;'>
        <span style='font-size:1.1rem;font-weight:bold;color:#355527;'>
            Send Rejection Mail
        </span>
    """, unsafe_allow_html=True)
    st.markdown("""
    <style>
        /* Target the last input in the DOM (or use nth-of-type for more precision) */
        input[type="text"] {
            color: #222 !important;
        }
        label { color: #222 !important; }
    </style>
    """, unsafe_allow_html=True)

    email = st.text_input("Candidate Email (to send rejection)")
    suggestions = st.text_area("Suggestions (from Model)", "")
    submit_mail = st.button("Send Email", key="send_email_btn")
    if submit_mail and email and suggestions:
        try:
            send_rejection_mail(email, suggestions)
            st.success(f"Email sent to {email}!")
        except Exception as e:
            st.error(f"Failed to send email: {e}")
            st.info("Please check your email environment variables (MAIL_USER, MAIL_PASS)")
    close = st.button("Close Mail Form", key="close_mail_btn")
    if close:
        st.session_state.show_mail_form = False
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ---- Upload Form ----
st.markdown("""
<div class='form-black'>
    <span style='font-size:1.3rem;font-weight:bold;color:#222;'>
        Upload Candidate Resume & Score Instantly!
    </span>
</div>
""", unsafe_allow_html=True)
st.markdown("""
    <style>
    input[type="text"], textarea, .stTextInput input, .stTextArea textarea {
        color: #fff !important;
    }
    label, .stTextInput>label, .stFileUploader>label {
        color: #222 !important;
    }
    </style>
""", unsafe_allow_html=True)
with st.form("score_form", clear_on_submit=True):
    name = st.text_input("Candidate Name", value="", max_chars=64, help="Enter candidate's full name")
    candidate_email = st.text_input("Candidate Email (for auto reject mail)")
    file = st.file_uploader("Upload Resume", type=["pdf", "txt"], help="PDF or TXT only, max 5MB.")
    submitted = st.form_submit_button("Score Candidate Fit", help="Analyze the candidate's resume")

apiurl = "https://hrai-production-d483.up.railway.app/predict"


if submitted:
    if not name or not file:
        st.warning("Please enter a name and upload a resume.")
    else:
        with st.spinner("Analyzing resume, picking out all the cute details..."):
            files = {"file": (file.name, file, file.type)}
            data = {"name": name}
            resp = requests.post(api_url, files=files, data=data)
            if resp.status_code == 200:
                result = resp.json()
                score = float(result['Hire_Probability'])
                status = result['Predicted_Status']

                status_html = f"<div class='bigscore'>{name} is predicted: "
                if status == "Hire":
                    status_html += f"<span class='result-hire'>HIRED</span>"
                else:
                    status_html += f"<span class='result-reject'>REJECTED</span>"
                status_html += f"</div>"
                st.markdown(status_html, unsafe_allow_html=True)
                st.progress(score)
                st.markdown(f"<div style='margin-bottom:0.7em;color:#222'><b>Fit score:</b> <span style='color:#red;font-size:1.1rem'>{score:.2%}</span></div>", unsafe_allow_html=True)

                lime_summary = result.get('LIME_SUMMARY', None)
                if lime_summary:
                    st.markdown(f"<div class='suggestion' style='color:#222'><b>Suggestion:</b> {lime_summary}</div>", unsafe_allow_html=True)
                else:
                    st.info("No detailed model explanation available. Please check the backend.")

                # Auto-rejection mail if status is "Reject"
                if status == "Reject" and candidate_email:
                    try:
                        send_rejection_mail(candidate_email, lime_summary or "No specific feedback.")
                        st.success(f"Auto rejection email sent to {candidate_email}!")
                    except Exception as e:
                        st.warning(f"Could not send auto-rejection mail: {e}")

                if status == "Reject":
                    st.markdown("<div style='background:#222;padding:12px;border-radius:12px;margin-top:7px;'>Not a perfect fit yet. See above for improvements!</div>", unsafe_allow_html=True)
            else:
                st.error("Failed! Please check file or try again.")

# ---- Bulk upload ----
st.markdown("""
<div class='card card-white'>
    <span style='font-size:1.3rem;font-weight:bold;color:#222;'>
        Bulk Resume Upload (ZIP): Score Multiple Candidates Instantly!
    </span>
</div>
""", unsafe_allow_html=True)

bulk_file = st.file_uploader(
    "Upload a ZIP with multiple resumes (PDF/TXT)", 
    type=["zip"], 
    help="Each file should be a candidate's resume (.pdf or .txt); the filename will be used as the candidate name."
)
bulk_submit = st.button("Bulk Score All Resumes", help="Batch analyze every file in the ZIP.")

if bulk_file and bulk_submit:
    with st.spinner("Analyzing all resumes..."):
        results = []
        with zipfile.ZipFile(bulk_file) as z:
            for f in z.namelist():
                if not (f.endswith(".pdf") or f.endswith(".txt")):
                    continue
                candidate_name = f.rsplit('.', 1)[0]
                file_bytes = z.read(f)
                files = {"file": (f, io.BytesIO(file_bytes), "application/pdf" if f.endswith(".pdf") else "text/plain")}
                data = {"name": candidate_name}
                resp = requests.post(api_url, files=files, data=data)
                if resp.status_code == 200:
                    result = resp.json()
                    results.append({
                        "Candidate": candidate_name,
                        "Status": result['Predicted_Status'],
                        "Score": float(result['Hire_Probability'])
                    })
                else:
                    results.append({
                        "Candidate": candidate_name,
                        "Status": "ERROR",
                        "Score": 0
                    })
        st.markdown("### Bulk Results")
        st.dataframe(results)

# ---- Footer ----
st.markdown("""
<div style='text-align:center;margin:30px 0 0 0;color:#836FFF;font-weight:bold;'>
    <span style='opacity:0.8;font-size:1.05rem;'>Built by Yash – 2025</span>
</div>
""", unsafe_allow_html=True)
