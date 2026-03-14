import streamlit as st
import openpyxl
import io
import json
import PyPDF2
import google.generativeai as genai

# --- 1. Page & AI Setup ---
st.set_page_config(page_title="Proffin AI Auditor", page_icon="⚖️", layout="wide")
st.title("⚖️ Proffin AI - Sec 198 Auditor (Live AI)")
st.subheader("Upload Balance Sheet -> AI Extraction -> Excel Working Paper")

# तिजोरी से तुम्हारी चाबी निकालना
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Gemini 1.5 Pro मॉडल को JSON (डेटा) निकालने के लिए सेट करना
    model = genai.GenerativeModel('gemini-1.5-pro', generation_config={"response_mime_type": "application/json"})
except Exception as e:
    st.error("🚨 API Key तिजोरी में नहीं मिली! कृपया Secrets सेट करें।")

# --- 2. File Uploaders ---
uploaded_pdf = st.file_uploader("📥 1. Upload Audited Financials (PDF)", type="pdf")
uploaded_template = st.file_uploader("📥 2. Upload Proffin Master Excel (.xlsx)", type="xlsx")

if uploaded_pdf and uploaded_template:
    st.info("✅ Both files accepted. Ready for AI Magic!")
    
    if st.button("🚀 Run Live AI Auditor"):
        
        # --- 3. PDF Reading Logic ---
        with st.spinner("1️⃣ AI is reading the PDF Document..."):
            pdf_reader = PyPDF2.PdfReader(uploaded_pdf)
            pdf_text = ""
            for page in range(len(pdf_reader.pages)):
                pdf_text += pdf_reader.pages[page].extract_text()
                
        # --- 4. The AI Brain (Prompt) ---
        with st.spinner("2️⃣ Gemini AI is extracting Financial Figures..."):
            ai_prompt = f"""
            You are an expert Indian Chartered Accountant and Company Secretary.
            Read the following text extracted from a company's financial statement and extract these 4 values (in Crores or exact figures as mentioned).
            If a value is an expense/loss, keep it negative. If not found, return 0.
            
            1. Net profit as per Profit and Loss a/c (pat)
            2. Profits by way of premium on shares (premium)
            3. Director's remuneration (remuneration)
            4. Excess of expenditure over income / past losses (past_losses)
            
            Return strictly in this JSON format:
            {{"pat": 0.0, "premium": 0.0, "remuneration": 0.0, "past_losses": 0.0}}
            
            Financial Text:
            {pdf_text[:15000]}  # Reading the first 15000 characters
            """
            
            try:
                # AI से जवाब मांगना
                response = model.generate_content(ai_prompt)
                extracted_data = json.loads(response.text)
                
                # AI के निकाले हुए नंबर्स
                ext_pat = float(extracted_data.get("pat", 0))
                ext_premium = float(extracted_data.get("premium", 0))
                ext_remun = float(extracted_data.get("remuneration", 0))
                ext_past_losses = float(extracted_data.get("past_losses", 0))
                
                st.success("✅ Data Extracted by AI Successfully!")
                st.json(extracted_data) # स्क्रीन पर AI का निकाला हुआ डेटा दिखाना
                
            except Exception as e:
                st.error(f"AI Extraction Failed: {e}")
                st.stop()

        # --- 5. EXCEL INJECTION MAGIC ---
        with st.spinner("3️⃣ Injecting AI Data into your Excel Formula..."):
            wb = openpyxl.load_workbook(uploaded_template)
            sheet = wb.active 
            
            # तुम्हारी Excel के E column में AI का डेटा डालना (Financial Year 2025)
            sheet['E5'] = ext_pat
            sheet['E6'] = ext_premium
            sheet['E7'] = ext_remun
            sheet['E8'] = ext_past_losses
            
            virtual_workbook = io.BytesIO()
            wb.save(virtual_workbook)
            virtual_workbook.seek(0)
            
            st.markdown("---")
            st.markdown("### 📥 Download Final Working Papers")
            st.success("तुम्हारी एक्सेल तैयार है! नीचे क्लिक करके डाउनलोड करो और देखो फॉर्मूले ने क्या रिजल्ट दिया!")
            
            st.download_button(
                label="📊 Download AI-Filled Excel",
                data=virtual_workbook,
                file_name="Proffin_AI_Sec198_Working.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
