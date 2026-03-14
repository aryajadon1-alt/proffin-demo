import streamlit as st
import pandas as pd
import time
import io
import openpyxl

st.set_page_config(page_title="Proffin Advisors", page_icon="⚖️", layout="wide")
st.title("⚖️ Proffin AI - Sec 198 Auditor")
st.subheader("Auto-Computation & Excel Generator")

# --- 1. File Upload ---
uploaded_pdf = st.file_uploader("📥 Upload Audited Financials (PDF)", type="pdf")
uploaded_template = st.file_uploader("📥 Upload Proffin Master Excel Template (.xlsx)", type="xlsx")

if uploaded_pdf and uploaded_template:
    st.info("✅ Files Accepted. Ready for AI Extraction.")
    
    if st.button("🚀 Run AI Auditor"):
        
        with st.spinner("AI is scanning PDF for Financial Figures..."):
            time.sleep(2)
            
        # --- 2. AI Extracted Data (Dummy data for MVP Demo) ---
        # मान लो AI ने PDF से ये नंबर्स निकाले (Crores में)
        extracted_pbt = 6.50
        extracted_tax = 1.25
        extracted_def_tax = 0.10
        extracted_remuneration = 0.50
        extracted_book_dep = 1.20
        extracted_sec123_dep = 1.20
        
        # --- 3. Python Math (For Screen Display) ---
        # (A + B - C - D) as per your Excel logic
        additions = extracted_tax + extracted_def_tax + extracted_remuneration + extracted_book_dep
        net_profit_198 = (extracted_pbt + additions) - extracted_sec123_dep
        
        st.success("✅ AI Extraction & Computation Complete!")
        st.markdown(f"### 📊 Computed Net Profit (Sec 198): **₹ {net_profit_198:.2f} Cr**")
        
        # CSR Check
        if net_profit_198 >= 5.0:
            st.error("🚨 **CSR TRIGGERED:** Profit exceeds ₹5 Cr threshold.")
        else:
            st.success("✅ **SAFE:** CSR Not Applicable.")

        # --- 4. EXCEL INJECTION MAGIC ---
        with st.spinner("Preparing Working Papers..."):
            # तुम्हारा ओरिजिनल एक्सेल खोलना
            wb = openpyxl.load_workbook(uploaded_template)
            
            # शीट सेलेक्ट करना (मान लेते हैं पहली शीट एक्टिव है या नाम 'Revised Computation' है)
            sheet = wb.active 
            
            # तुम्हारे Cell Numbers में AI का डेटा भरना
            sheet['D7'] = extracted_pbt
            sheet['C9'] = extracted_tax
            sheet['C10'] = extracted_def_tax
            sheet['C11'] = extracted_remuneration
            sheet['C13'] = extracted_book_dep
            sheet['D22'] = extracted_sec123_dep
            
            # नई एक्सेल फाइल को मेमोरी में सेव करना
            virtual_workbook = io.BytesIO()
            wb.save(virtual_workbook)
            virtual_workbook.seek(0)
            
            st.markdown("### 📥 Download Working Papers")
            st.download_button(
                label="📊 Download Auto-Filled Excel Computation",
                data=virtual_workbook,
                file_name="Proffin_Client_Sec198_Working.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
