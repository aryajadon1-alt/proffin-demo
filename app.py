import streamlit as st
import openpyxl
import io
import json
import PyPDF2
import google.generativeai as genai

# --- 1. Page Setup ---
st.set_page_config(page_title="Proffin AI Auditor", page_icon="⚖️", layout="wide")
st.title("⚖️ Proffin AI - Sec 198 Auditor (Auto-Detect Edition)")
st.subheader("Smart Engine: Finds the correct AI model automatically")

# --- 2. API Key & Auto-Detect AI Setup ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # 🚨 THE MAGIC: Google से पूछना कि कौन से मॉडल चालू हैं 🚨
    working_models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            working_models.append(m.name)
            
    # साइडबार में दिखाना कि तुम्हारी चाबी के पास क्या पावर है
    st.sidebar.success("✅ Google AI Connected")
    st.sidebar.write("Your active models:", working_models)
    
    # सबसे बेस्ट मॉडल को खुद चुनना
    active_model_name = None
    for name in working_models:
        if 'gemini-1.5-flash' in name or 'gemini-1.0-pro' in name or 'gemini-pro' in name:
            active_model_name = name
            break
            
    if not active_model_name and working_models:
        active_model_name = working_models[0] # जो भी पहला मिले, उसे चला दो
        
    if active_model_name:
        model = genai.GenerativeModel(active_model_name)
        st.sidebar.info(f"🚀 Using Engine: {active_model_name}")
    else:
        st.error("🚨 तुम्हारी API Key के लिए कोई भी मॉडल एक्टिव नहीं है!")

except Exception as e:
    st.warning("🚨 Streamlit Secrets में API Key नहीं मिली या कोई एरर है!")

# --- 3. Uploaders ---
uploaded_pdf = st.file_uploader("📥 1. Upload Balance Sheet (PDF)", type="pdf")
uploaded_template = st.file_uploader("📥 2. Upload Master Excel (.xlsx)", type="xlsx")

if uploaded_pdf and uploaded_template:
    st.success("✅ Files Uploaded! Ready to scan.")
    
    if st.button("🚀 Run AI Engine"):
        
        # PDF Reading
        with st.spinner("📖 Reading PDF..."):
            pdf_reader = PyPDF2.PdfReader(uploaded_pdf)
            pdf_text = "".join([page.extract_text() for page in pdf_reader.pages])
                
        # AI Extraction
        with st.spinner(f"🧠 AI ({active_model_name}) is extracting figures..."):
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
                
                # Text Cleaning (ये वाला हिस्सा मैंने ठीक कर दिया है)
                raw_text = response.text.strip()
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                    
                extracted_data = json.loads(raw_text.strip())
                
                ext_pat = float(extracted_data.get("pat", 0))
                ext_premium = float(extracted_data.get("premium", 0))
                ext_remun = float(extracted_data.get("remuneration", 0))
                ext_past_losses = float(extracted_data.get("past_losses", 0))
                
                st.success("✅ AI Extraction Complete!")
                st.json(extracted_data)
                
            except Exception as e:
                st.error(f"AI Error: {e}")
                st.stop()

        # Excel Automation
        with st.spinner("📊 Injecting into Excel Working Papers..."):
            wb = openpyxl.load_workbook(uploaded_template)
            sheet = wb.active 
            
            sheet['E5'] = ext_pat
            sheet['E6'] = ext_premium
            sheet['E7'] = ext_remun
            sheet['E8'] = ext_past_losses
            
            virtual_workbook = io.BytesIO()
            wb.save(virtual_workbook)
            virtual_workbook.seek(0)
            
            st.markdown("---")
            st.download_button(
                label="📥 Download AI-Filled Excel",
                data=virtual_workbook,
                file_name="Proffin_Sec198_Final_AI.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
