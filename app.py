import streamlit as st
import openpyxl
import io
import json
import PyPDF2
import google.generativeai as genai

# --- 1. Page Setup ---
st.set_page_config(page_title="Proffin AI Auditor", page_icon="⚖️", layout="wide")
st.title("⚖️ Proffin AI - Sec 198 Auditor (Final Clean Version)")
st.subheader("Smart Engine with Traffic Controller 🚦")

# --- 2. API Key & Auto-Detect AI Setup ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # सिर्फ हाई-लिमिट वाले मॉडल्स ढूँढना
    working_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    # Priority: सबसे पहले 'Flash' (क्योंकि इसकी स्पीड और लिमिट सबसे ज्यादा है)
    active_model_name = None
    for name in working_models:
        if 'gemini-1.5-flash' in name:
            active_model_name = name
            break
            
    # अगर Flash न मिले, तो Pro उठा लो
    if not active_model_name:
        for name in working_models:
            if 'gemini-1.0-pro' in name or 'gemini-pro' in name:
                active_model_name = name
                break
                
    if active_model_name:
        model = genai.GenerativeModel(active_model_name)
        st.sidebar.success(f"🚀 AI Engine Online: {active_model_name}")
    else:
        st.error("🚨 तुम्हारी API Key के लिए कोई भी मॉडल एक्टिव नहीं है!")

except Exception as e:
    st.warning("🚨 Streamlit Secrets में API Key नहीं मिली!")

# --- 3. Uploaders ---
uploaded_pdf = st.file_uploader("📥 1. Upload Balance Sheet (PDF)", type="pdf")
uploaded_template = st.file_uploader("📥 2. Upload Master Excel (.xlsx)", type="xlsx")

if uploaded_pdf and uploaded_template:
    st.success("✅ Files Uploaded! Ready to scan.")
    
    if st.button("🚀 Run AI Engine"):
        
        # PDF Reading
        with st.spinner("📖 Reading PDF..."):
            pdf_reader = PyPDF2.PdfReader(uploaded_pdf)
            pdf_text = "".join([page.extract_text() or "" for page in pdf_reader.pages])
                
        # AI Extraction
        with st.spinner("🧠 AI is extracting figures..."):
            ai_prompt = f"""
            You are an expert CA/CS. Read the financial statement text and extract these 4 values.
            Return 0 if not found. Make expenses/losses negative.
            1. Net profit as per Profit and Loss a/c (pat)
            2. Profits by way of premium on shares (premium)
            3. Director's remuneration (remuneration)
            4. Excess of expenditure over income / past losses (past_losses)
            
            Respond ONLY with a valid JSON format. Do not add any extra text, no markdown.
            Example: {{"pat": 10.5, "premium": 0.0, "remuneration": -1.2, "past_losses": 0.0}}
            
            Text:
            {pdf_text[:15000]}
            """
            
            try:
                response = model.generate_content(ai_prompt)
                
                raw_text = response.text.strip()
                if raw_text.startswith("
