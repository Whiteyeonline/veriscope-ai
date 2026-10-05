"""
app.py
Streamlit Web Application Entrypoint
"""
import os
import asyncio

import streamlit as st

from core.orchestrator import AuditOrchestrator
from identity.business_matcher import IdentityResolutionError

st.set_page_config(page_title="Local SEO Audit Engine", page_icon="🔍", layout="centered")

st.title("🔍 Local SEO & GBP Audit Generator")
st.caption("Generate zero-cost, customer-ready executive PDF audits in seconds.")

try:
    secrets = st.secrets
except Exception:
    secrets = {}

serpapi_key = secrets.get("SERPAPI_API_KEY", os.getenv("SERPAPI_API_KEY", "")) if hasattr(secrets, "get") else os.getenv("SERPAPI_API_KEY", "")
gemini_key = secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", "")) if hasattr(secrets, "get") else os.getenv("GEMINI_API_KEY", "")
groq_key = secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", "")) if hasattr(secrets, "get") else os.getenv("GROQ_API_KEY", "")

if not any([serpapi_key, gemini_key, groq_key]):
    st.info("No API keys detected. The app will generate a demo-quality PDF using local fallback logic so the workflow still works.")

with st.form("audit_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Business Name*", "ABC Dental Clinic")
        category = st.text_input("Category*", "Dentist")
        locality = st.text_input("Locality", "Muvattupuzha")
        city = st.text_input("City*", "Kollam")
    with col2:
        country = st.text_input("Country*", "India")
        primary_kw = st.text_input("Primary Keyword*", "dentist in Muvattupuzha")
        website = st.text_input("Website URL", "https://example.com")
        maps_url = st.text_input("Google Maps URL (Optional)")

    language = st.selectbox("Report Language", ["English", "Malayalam"])
    submit = st.form_submit_button("GENERATE AUDIT")

if submit:
    if not name or not city or not primary_kw:
        st.error("Please fill in all required fields marked with *")
    else:
        payload = {
            "name": name,
            "category": category,
            "locality": locality,
            "city": city,
            "country": country,
            "primary_keyword": primary_kw,
            "website": website,
            "maps_url": maps_url,
            "language": language,
            "phone": ""
        }

        orchestrator = AuditOrchestrator(
            serpapi_key=serpapi_key,
            gemini_key=gemini_key,
            groq_key=groq_key
        )

        with st.status("Generating Audit...", expanded=True) as status:
            try:
                st.write("🔍 Searching local maps and crawling site...")
                pdf_path, record = asyncio.run(orchestrator.execute_audit(payload))
                status.update(label="✓ Audit Completed Successfully!", state="complete")

                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="📥 DOWNLOAD EXECUTIVE PDF REPORT",
                        data=f,
                        file_name=os.path.basename(pdf_path),
                        mime="application/pdf"
                    )

                st.success(f"Report saved to: {pdf_path}")
            except IdentityResolutionError as exc:
                status.update(label="⚠️ Verification Needed", state="error")
                st.warning(str(exc))
            except Exception as exc:
                status.update(label="❌ Audit Failed", state="error")
                st.error(f"Error during execution: {str(exc)}")
