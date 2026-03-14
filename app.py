import streamlit as st
import openpyxl
import io
import json
import PyPDF2
import google.generativeai as genai

st.set_page_config(page_title="Proffin AI Auditor", page_icon="⚖️", layout="wide")
st.title("⚖️ Proffin AI - Sec 198 Auditor (Ultimate Fix)")

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    st.error("🚨 API Key Error!")

uploaded_pdf = st.file_uploader("📥 1. Upload Balance Sheet (PDF)", type="pdf")
uploaded_template = st.file_uploader("📥 2. Upload Master Excel (.xlsx)", type="xlsx")

if uploaded_pdf and uploaded_template:
    if st.button("🚀 Run AI Engine"):
        with st.spinner("📖 Reading & Extracting..."):
            pdf_reader = PyPDF2.PdfReader(uploaded_pdf)
            pdf_text = "".join([page.extract_text() or "" for page in pdf_reader.pages])
                
            ai_prompt = f"""
            You are a CA/CS. Extract these 4 values from the text. Return 0 if not found. Make expenses negative.
            1. Net profit as per Profit and Loss a/c (pat)
            2. Profits by way of premium on shares (premium)
            3. Director's remuneration (remuneration)
            4. Excess of expenditure over income / past losses (past_losses)
            
            Respond ONLY with valid JSON. Example: {{"pat": 10.5, "premium": 0.0, "remuneration": -1.2, "past_losses": 0.0}}
            
            Text:
            {pdf_text[:15000]}
            """
            
            try:
                response = model.generate_content(ai_prompt)
                
                # यहाँ मैंने कोड बदल दिया है ताकि कोई लाइन न टूटे
                raw_text = response.text.replace("```json", "").replace("```", "").strip()
                extracted_data = json.loads(raw_text)
                
                ext_pat = float(extracted_data.get("pat", 0))
                ext_premium = float(extracted_data.get("premium", 0))
                ext_remun = float(extracted_data.get("remuneration", 0))
                ext_past_losses = float(extracted_data.get("past_losses", 0))
                
                st.success("✅ Extraction Complete!")
                st.json(extracted_data)
                
                wb = openpyxl.load_workbook(uploaded_template)
                sheet = wb.active 
                sheet["E5"] = ext_pat
                sheet["E6"] = ext_premium
                sheet["E7"] = ext_remun
                sheet["E8"] = ext_past_losses
                
                virtual_workbook = io.BytesIO()
                wb.save(virtual_workbook)
                virtual_workbook.seek(0)
                
                st.download_button("📥 Download Excel", virtual_workbook, "Proffin_Final.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                
            except Exception as e:
                st.error(f"Error: {e}")
