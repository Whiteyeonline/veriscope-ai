# Veriscope AI - Professional Local SEO Audit SaaS

**A production-grade automated local SEO & Google Business Profile audit tool** that helps agencies, local businesses, and marketers evaluate and improve online visibility on Google Maps and search results.

## Features

✅ **Real-Time Local Search Data**
- Live Google Maps search results using SerpAPI
- Competitor identification and benchmark scoring
- Local ranking position verification

✅ **Website Technical Audit**
- HTTPS security verification
- Mobile responsiveness check
- Local schema markup detection (LocalBusiness, Organization)
- Page load performance metrics

✅ **AI-Powered Business Intelligence**
- Google Gemini or Groq for insights generation
- Automated GBP Health Score (0-100)
- Actionable priority recommendations
- Review sentiment analysis patterns

✅ **Professional PDF Reports**
- 2-page executive summary with charts
- GBP health gauge visualization
- Competitor benchmark comparison
- Priority action plan
- Bilingual support (English/Malayalam)

## Quick Start

### 1. Prerequisites

**Python 3.8+** and these free API keys:
- **SerpAPI** (required): https://serpapi.com - Free tier: 100 searches/month
- **Google Gemini** (recommended): https://ai.google.dev - Generous free quotas
- **Groq** (optional fallback): https://console.groq.com - Fast inference

### 2. Installation

```bash
# Clone repository
git clone https://github.com/Whiteyeonline/veriscope-ai.git
cd veriscope-ai

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API keys
SERPAPI_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
```

### 4. Launch

```bash
# Run Streamlit app
streamlit run app.py
```

The app opens at `http://localhost:8501`

## How It Works

### End-to-End Workflow

1. **User Input** - Enter business name, category, location, and keywords
2. **SERP Harvesting** - SerpAPI queries Google Maps and local search results
3. **Identity Verification** - Machine matches candidate businesses with confidence scoring
4. **Website Crawl** - Direct HTTP crawler checks HTTPS, schema, and performance
5. **AI Analysis** - Gemini/Groq generates insights from evidence data
6. **Chart Generation** - QuickChart generates GBP gauge and competitor comparison
7. **PDF Export** - ReportLab builds professional 2-page executive report

### Data Flow

```
Business Input
    ↓
[SerpAPI] → Local Results + Competitors
[Website Crawler] → Tech Metrics + Schema
    ↓
Identity Matcher → Verified Business Record
    ↓
AI Engine (Gemini/Groq) → Insights + Recommendations
    ↓
Chart Generator → Visual Assets
    ↓
PDF Builder → Executive Report
    ↓
Download PDF
```

## Project Structure

```
.
├── app.py                    # Streamlit UI
├── requirements.txt          # Python dependencies
├── .env.example             # Configuration template
│
├── core/
│   ├── orchestrator.py      # Main pipeline coordinator
│   ├── models.py            # Data schemas (Pydantic)
│   └── cache.py             # SQLite caching layer
│
├── providers/
│   ├── base.py              # Abstract provider class
│   ├── serpapi.py           # Google Maps API integration
│   ├── website.py           # Website crawler
│   └── provider_manager.py  # Provider orchestration
│
├── analysis/
│   ├── gemini.py            # Google Gemini AI engine
│   └── groq_fallback.py     # Groq LLM fallback
│
├── identity/
│   └── business_matcher.py  # Business verification logic
│
├── charts/
│   └── quickchart.py        # Chart URL generation
│
├── reports/
│   ├── pdf.py               # PDF generation (ReportLab)
│   └── styles.py            # PDF styling
│
└── config/
    ├── prompts.json         # AI prompt templates
    └── providers.json       # Provider configuration
```

## API Requirements

### SerpAPI (Required)
Used for Google Maps search and local business discovery.

```python
# Example: Search for businesses
await provider.search_local_business(
    query="dentist muvattupuzha",
    location="Kollam, India"
)
```

**Pricing:**
- Free tier: 100 searches/month
- Paid: $5-100/month depending on volume

### Google Gemini (Recommended)
Primary AI engine for analysis and recommendations.

```python
# Example: Generate insights
ai_insights = await gemini.generate_analysis(
    evidence=business_data,
    prompt_template=prompt,
    language="English"
)
```

**Pricing:** Free tier suitable for most use cases

### Groq (Fallback)
Fast alternative if Gemini is unavailable.

```python
# Example: Failover to Groq
ai_insights = await groq.generate_analysis(...)
```

**Pricing:** Free tier with generous quotas

## Usage Examples

### Run a Single Audit Programmatically

```python
import asyncio
from core.orchestrator import AuditOrchestrator

async def main():
    orchestrator = AuditOrchestrator(
        serpapi_key="your_key",
        gemini_key="your_key",
        groq_key="your_key"
    )
    
    payload = {
        "name": "ABC Dental Clinic",
        "category": "Dentist",
        "city": "Kollam",
        "country": "India",
        "primary_keyword": "dentist in Kollam",
        "website": "https://abcdental.com",
        "language": "English"
    }
    
    pdf_path, record = await orchestrator.execute_audit(payload)
    print(f"Report saved: {pdf_path}")

asyncio.run(main())
```

### Integrate into Your Backend

```python
# FastAPI example
from fastapi import FastAPI
from core.orchestrator import AuditOrchestrator

app = FastAPI()
orchestrator = AuditOrchestrator(
    serpapi_key=os.getenv("SERPAPI_API_KEY"),
    gemini_key=os.getenv("GEMINI_API_KEY"),
    groq_key=os.getenv("GROQ_API_KEY")
)

@app.post("/audit")
async def generate_audit(business: BusinessInput):
    pdf_path, record = await orchestrator.execute_audit(business.dict())
    return FileResponse(pdf_path, media_type="application/pdf")
```

## Environment Variables

| Variable | Required | Source | Purpose |
|----------|----------|--------|----------|
| `SERPAPI_API_KEY` | ✅ Yes | https://serpapi.com | Google Maps search |
| `GEMINI_API_KEY` | ⚠️ One of two | https://ai.google.dev | AI analysis |
| `GROQ_API_KEY` | ⚠️ One of two | https://console.groq.com | AI fallback |

## Troubleshooting

### "SERPAPI_API_KEY is required"
```bash
# Add to .env
SERPAPI_API_KEY=your_key_here

# Or set in terminal
export SERPAPI_API_KEY=your_key_here
```

### "No local business results found"
- Verify business name is spelled correctly
- Use more specific locality information
- Provide Google Maps URL directly

### "SerpAPI quota exceeded"
- Upgrade your SerpAPI plan
- Use free tier more carefully (100 searches/month)

### "Failed to generate AI analysis"
- Check Gemini/Groq API keys are valid
- Verify you haven't exceeded free tier quotas
- Try the alternative AI provider

## Performance Metrics

- **Average audit time:** 15-45 seconds
- **API calls per audit:** 2-3 (SerpAPI + AI)
- **PDF generation:** <5 seconds
- **Report file size:** 200-500 KB

## Security

- ✅ API keys stored in `.env` (not committed)
- ✅ No customer data persisted
- ✅ HTTPS only for website checks
- ✅ Cache layer reduces API quota usage

## Roadmap

- [ ] Agency dashboard with audit history
- [ ] Automated report scheduling
- [ ] Multi-location audits
- [ ] Competitor tracking over time
- [ ] Integration with CRM platforms
- [ ] Mobile app

## License

MIT License - See LICENSE file

## Support

- GitHub Issues: https://github.com/Whiteyeonline/veriscope-ai/issues
- Email: support@veriscope.ai
- Docs: https://veriscope.ai/docs

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

**Built with ❤️ for local SEO professionals**
