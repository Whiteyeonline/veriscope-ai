"""
app.py
Streamlit Web Application Entrypoint
"""
import os
import asyncio
import sys

import streamlit as st
from dotenv import load_dotenv

from core.orchestrator import AuditOrchestrator
from identity.business_matcher import IdentityResolutionError

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="Local SEO Audit Engine",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar with API Key status
with st.sidebar:
    st.title("🔧 Configuration")
    st.info(
        "This is a production Local SEO audit tool. "
        "Your API keys are required to generate accurate reports."
    )
    
    # Check for API keys
    serpapi_key = os.getenv("SERPAPI_API_KEY", "")
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    groq_key = os.getenv("GROQ_API_KEY", "")
    
    st.subheader("API Status")
    col1, col2 = st.columns(2)
    with col1:
        if serpapi_key:
            st.success("✓ SerpAPI")
        else:
            st.error("✗ SerpAPI Key Missing")
    with col2:
        if gemini_key or groq_key:
            st.success("✓ AI Provider")
        else:
            st.error("✗ AI Key Missing")
    
    st.divider()
    
    st.subheader("Setup Guide")
    with st.expander("Get API Keys (Free Tier)"):
        st.markdown("""
        ### SerpAPI (Required)
        - Visit: https://serpapi.com
        - Free tier: 100 searches/month
        - Add to `.env`: `SERPAPI_API_KEY=your_key`
        
        ### Google Gemini (Recommended)
        - Visit: https://ai.google.dev
        - Free tier: Generous quotas
        - Add to `.env`: `GEMINI_API_KEY=your_key`
        
        ### Groq (Fallback)
        - Visit: https://console.groq.com
        - Free tier: Fast inference
        - Add to `.env`: `GROQ_API_KEY=your_key`
        """)
    
    if st.button("🔄 Reload Configuration", use_container_width=True):
        st.rerun()

st.title("🔍 Professional Local SEO & GBP Audit Engine")
st.caption("Generate production-grade executive PDF audits with real Google Maps data and AI-powered insights.")

# Main form
with st.form("audit_form"):
    st.subheader("Business Information")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input(
            "Business Name*",
            value="ABC Dental Clinic",
            help="Full legal business name"
        )
        category = st.text_input(
            "Business Category*",
            value="Dentist",
            help="e.g., Dentist, Pizza Restaurant, Hair Salon"
        )
        locality = st.text_input(
            "Locality/Neighborhood",
            value="Muvattupuzha",
            help="Specific area (optional, improves accuracy)"
        )
        city = st.text_input(
            "City*",
            value="Kollam",
            help="City where business operates"
        )
    
    with col2:
        country = st.text_input(
            "Country*",
            value="India",
            help="Country/Region"
        )
        primary_kw = st.text_input(
            "Primary Local Keyword*",
            value="dentist in Muvattupuzha",
            help="How customers search for your business"
        )
        website = st.text_input(
            "Website URL",
            value="https://example.com",
            help="Business website (optional)"
        )
        maps_url = st.text_input(
            "Google Maps URL",
            value="",
            help="Direct link to Google Business profile (helps verify exact location)"
        )
    
    language = st.selectbox(
        "Report Language",
        ["English", "Malayalam"],
        help="PDF report language"
    )
    
    col1, col2, col3 = st.columns(3)
    with col1:
        submit = st.form_submit_button("🚀 GENERATE AUDIT", use_container_width=True)
    with col2:
        st.form_submit_button("📋 Clear Form", use_container_width=True, on_click=lambda: None)
    with col3:
        st.form_submit_button("ℹ️ Example Report", use_container_width=True, on_click=lambda: None)

if submit:
    # Validate inputs
    if not name or not city or not primary_kw:
        st.error("❌ Please fill in all required fields marked with *")
        st.stop()
    
    # Validate API keys
    serpapi_key = os.getenv("SERPAPI_API_KEY", "")
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    groq_key = os.getenv("GROQ_API_KEY", "")
    
    if not serpapi_key:
        st.error(
            "❌ **SERPAPI_API_KEY is required.**\n\n"
            "This tool generates reports using real Google Maps data. "
            "Please set your SerpAPI key in the `.env` file or environment variables. "
            "[Get a free key](https://serpapi.com)"
        )
        st.stop()
    
    if not (gemini_key or groq_key):
        st.error(
            "❌ **At least one AI provider key is required.**\n\n"
            "Set GEMINI_API_KEY or GROQ_API_KEY in `.env`. "
            "[Get free keys](https://ai.google.dev) or [Groq](https://console.groq.com)"
        )
        st.stop()
    
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

    with st.status("🔄 Generating Your Audit...", expanded=True) as status:
        try:
            # Run async orchestration
            pdf_path, record = asyncio.run(orchestrator.execute_audit(payload))
            
            status.update(label="✅ Audit Completed Successfully!", state="complete")
            
            # Provide download button
            st.success("Your professional PDF report is ready!")
            
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📥 DOWNLOAD EXECUTIVE PDF REPORT",
                    data=f.read(),
                    file_name=os.path.basename(pdf_path),
                    mime="application/pdf",
                    use_container_width=True,
                    key="pdf_download"
                )
            
            # Show key findings
            with st.expander("📊 Quick Insights", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        "Rating",
                        f"{record.get('rating', 'N/A')}/5.0" if record.get('rating') else "No rating"
                    )
                with col2:
                    st.metric(
                        "Reviews",
                        record.get('review_count', 0) or 0
                    )
                with col3:
                    st.metric(
                        "Website",
                        "✓ Present" if record.get('website') else "✗ Missing"
                    )
                
                st.write(f"**Business:** {record.get('name')}")
                st.write(f"**Location:** {record.get('city')}, {record.get('country')}")
                st.write(f"**Category:** {record.get('category')}")
        
        except RuntimeError as e:
            status.update(label="❌ Configuration Error", state="error")
            st.error(f"**Setup Required:** {str(e)}")
        except IdentityResolutionError as e:
            status.update(label="⚠️ Verification Issue", state="error")
            st.warning(
                f"**Could not verify business:**\n\n{str(e)}\n\n"
                "Try providing a Google Maps URL or being more specific with the business name."
            )
        except Exception as e:
            status.update(label="❌ Error", state="error")
            st.error(f"**Error during audit:** {str(e)}")
            if "quota" in str(e).lower():
                st.info("💡 You've hit your API quota. Upgrade your plan or try again later.")

st.divider()

with st.expander("❓ FAQ"):
    st.markdown("""
    **Q: Why do I need API keys?**
    A: This tool pulls real data from Google Maps and uses AI for analysis. 
    API keys are free and we recommend starting with the free tier.
    
    **Q: How accurate is the report?**
    A: Reports use live Google Maps data, website crawl results, and AI-powered analysis. 
    Accuracy depends on data completeness in Google Business Profile.
    
    **Q: Can I use this without API keys?**
    A: No, this is a professional tool that requires live data. 
    A demo version with fallback data is available on request.
    
    **Q: How much does this cost?**
    A: Most costs come from SerpAPI (100 free searches/month). 
    AI providers offer free tier quotas suitable for getting started.
    """)
