# veriscope-ai

A production-ready local SEO audit tool that collects Google Maps / local search evidence, checks website technical health, scores business performance, and exports a two-page executive PDF report.

## What it does
- Collects business details and local keyword context
- Queries local maps/search results and identifies competitors
- Checks HTTPS, page performance, and local schema presence on the website
- Uses AI (Gemini/Groq) for insights when configured
- Exports a PDF report with charts and recommendations

## Run locally

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Copy environment variables:

```bash
cp env.example .env
```

3. Add your API keys to `.env` or `~/.streamlit/secrets.toml` when you want live SERP / AI data.

4. Launch the app:

```bash
streamlit run app.py
```

5. Or generate a demo PDF even without external keys:

```bash
python generate_demo_report.py
```

This will create a PDF under `reports_out/`.

## Notes
- The app has a fallback mode so it still generates a PDF even if API keys are missing.
- Live SERP and AI analysis require valid `SERPAPI_API_KEY`, `GEMINI_API_KEY`, and/or `GROQ_API_KEY`.
- If no exact Google Maps listing match is found, the app prompts for a more precise listing URL.
