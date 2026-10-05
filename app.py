"""
app.py
Streamlit Web Application Entrypoint
Production-ready local SEO audit SaaS
"""
import os
import asyncio
import streamlit as st

from core.orchestrator import AuditOrchestrator
from identity.business_matcher import IdentityResolutionError


st.set_page_config(
    page_title="Local SEO Audit Engine",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)


def get_secret(name: str) -> str:
    """Read a secret from Streamlit or environment variables."""
    try:
        value = st.secrets.get(name, "")
        if value:
            return str(value)
    except Exception:
        pass
    return os.environ.get(name, "")


with st.sidebar:
    st.title("⚙️ Configuration")
    st.info("Professional Local SEO Audit Tool. Keep API keys only in Streamlit Secrets.")

    serpapi_key = get_secret("SERPAPI_API_KEY")
    gemini_key = get_secret("GEMINI_API_KEY")
    groq_key = get_secret("GROQ_API_KEY")

    st.subheader("API Status")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.success("✓ SerpAPI") if serpapi_key else st.error("✗ SerpAPI")
    with col2:
        st.success("✓ Gemini") if gemini_key else st.info("- Gemini")
    with col3:
        st.success("✓ Groq") if groq_key else st.info("- Groq")

    if not serpapi_key or not (gemini_key or groq_key):
        st.warning("⚠️ Add the keys under Streamlit Cloud → Manage app → Secrets")
        st.code(
            """SERPAPI_API_KEY = \"your_serpapi_key\"
GEMINI_API_KEY = \"your_gemini_key\"
GROQ_API_KEY = \"your_groq_key\"""",
            language="toml",
        )

st.title("🔍 Professional Local SEO & GBP Audit Engine")
st.caption("Generate production-grade executive PDF audits with real Google Maps data and AI-powered insights.")

with st.form("audit_form"):
    st.subheader("📋 Business Information")

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Business Name *", value="", placeholder="e.g., McDonald's")
        category = st.text_input("Business Category *", value="", placeholder="e.g., Fast Food")
        locality = st.text_input("Locality / Area", value="", placeholder="e.g., Midtown")
        city = st.text_input("City *", value="", placeholder="e.g., New York")

    with col2:
        country = st.text_input("Country *", value="United States", placeholder="e.g., United States")
        primary_kw = st.text_input("Search Keyword *", value="", placeholder="e.g., McDonald's near me")
        website = st.text_input("Website URL", value="", placeholder="https://example.com (optional)")
        maps_url = st.text_input("Google Maps URL", value="", placeholder="https://maps.google.com/... (optional)")

    language = st.selectbox("Report Language", ["English", "Malayalam"])
    submit = st.form_submit_button("🚀 GENERATE AUDIT", use_container_width=True)

if submit:
    if not name or not city or not country or not primary_kw:
        st.error("❌ Please fill in all required fields (marked with *).")
        st.stop()

    serpapi_key = get_secret("SERPAPI_API_KEY")
    gemini_key = get_secret("GEMINI_API_KEY")
    groq_key = get_secret("GROQ_API_KEY")

    if not serpapi_key:
        st.error("❌ SERPAPI_API_KEY is missing in Streamlit Secrets.")
        st.stop()

    if not (gemini_key or groq_key):
        st.error("❌ Add at least one AI key: GEMINI_API_KEY or GROQ_API_KEY.")
        st.stop()

    payload = {
        "name": name.strip(),
        "category": category.strip() or "Local Business",
        "locality": locality.strip() or "",
        "city": city.strip(),
        "country": country.strip(),
        "primary_keyword": primary_kw.strip(),
        "website": website.strip() or "",
        "maps_url": maps_url.strip() or "",
        "language": language,
        "phone": "",
    }

    orchestrator = AuditOrchestrator(
        serpapi_key=serpapi_key,
        gemini_key=gemini_key,
        groq_key=groq_key,
    )

    with st.status("🔄 Generating your audit...", expanded=True) as status:
        try:
            pdf_path, record = asyncio.run(orchestrator.execute_audit(payload))
            status.update(label="✅ Audit completed successfully!", state="complete")

            st.success("✨ Your professional PDF report is ready!")
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📥 DOWNLOAD EXECUTIVE PDF REPORT",
                    data=f.read(),
                    file_name=os.path.basename(pdf_path),
                    mime="application/pdf",
                    use_container_width=True,
                    key="pdf_download",
                )

            with st.expander("📊 Quick Insights", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    rating = record.get("rating")
                    st.metric("Rating", f"{rating}/5.0" if rating else "N/A")
                with col2:
                    reviews = record.get("review_count") or 0
                    st.metric("Reviews", int(reviews))
                with col3:
                    st.metric("Website", "✓ Listed" if record.get("website") else "✗ Missing")

                st.write(f"**Business:** {record.get('name')}")
                st.write(f"**Location:** {record.get('city')}, {record.get('country')}")
                st.write(f"**Category:** {record.get('category')}")

        except RuntimeError as e:
            status.update(label="⚠️ Configuration or API Error", state="error")
            st.error(f"**Setup Required:** {str(e)}")
        except ValueError as e:
            status.update(label="⚠️ Input Error", state="error")
            st.error(f"**Invalid Input:** {str(e)}")
        except IdentityResolutionError as e:
            status.update(label="⚠️ Verification issue", state="error")
            st.warning(f"**Could not verify business**: {str(e)}")
        except Exception as e:
            status.update(label="❌ Error", state="error")
            st.error(f"**Error during audit:** {str(e)}")

st.divider()
with st.expander("❓ FAQ"):
    st.markdown(
        """
        **Q: Why do I need API keys?**
        A: Google Maps and AI analysis require live API access.

        **Q: Are my keys safe?**
        A: Yes. Keep them only in Streamlit Secrets and never commit them to GitHub.

        **Q: Can the app work without a website?**
        A: Yes. It will still create the report and mark the website as missing.

        **Q: What business should I test first?**
        A: Use a famous local business like McDonald's or Starbucks, with city + country.
        """
    )
