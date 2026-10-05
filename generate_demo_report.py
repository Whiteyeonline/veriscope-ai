import asyncio
import os

from core.orchestrator import AuditOrchestrator


def main():
    payload = {
        "name": "ABC Dental Clinic",
        "category": "Dentist",
        "locality": "Muvattupuzha",
        "city": "Kollam",
        "country": "India",
        "primary_keyword": "dentist in Muvattupuzha",
        "website": "https://example.com",
        "maps_url": "",
        "language": "English",
        "phone": ""
    }

    os.makedirs("reports_out", exist_ok=True)
    orchestrator = AuditOrchestrator(serpapi_key="", gemini_key="", groq_key="")
    pdf_path, _ = asyncio.run(orchestrator.execute_audit(payload))
    print(f"Demo report generated at: {pdf_path}")


if __name__ == "__main__":
    main()
