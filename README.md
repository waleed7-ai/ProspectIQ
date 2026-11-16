# ProspectIQ — Agentic AI Business Research

A portfolio prototype that uses a Gemini tool-calling agent to research an approved public company website, generate evidence-grounded opportunities, score a lead, and draft outreach for **human approval**. Research is saved to a local SQLite database and exportable as CSV.

## Features
- Real LLM function calling: the model invokes a Python `fetch_website` tool.
- Public URL validation and redirect blocking.
- Evidence, limitations, opportunity analysis, and transparent lead scoring.
- Human-reviewed outreach drafts; **no automatic email sending**.
- Local CRM-style dashboard, SQLite persistence, CSV export, and agent activity log.

## Setup
Requires Python 3.10+ and a Gemini API key.

```bash
python -m venv .venv
# Windows PowerShell:
.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Put your key in .env or enter it in the app sidebar
streamlit run app.py
```

## Architecture
`Streamlit UI → Gemini agent → approved fetch_website tool → JSON report → human review → SQLite → CSV export`

## Test checklist (run and record results before claiming completion)
- [ ] Public business homepage produces a grounded report and a visible tool log.
- [ ] Invalid or private URL is rejected.
- [ ] Unavailable website fails gracefully without fabricated claims.
- [ ] Saving the same URL updates the existing record rather than duplicating it.
- [ ] CSV export contains the saved prospect.
- [ ] Draft email is not sent automatically.

## Limitations
This prototype reads one public HTML page, not an entire site. Some sites block automated requests or require JavaScript. Lead scores and recommendations are heuristic LLM outputs, not validated commercial predictions. URL DNS validation is a defense-in-depth check, not a production-grade SSRF sandbox; deploy only behind additional network controls. Review all research and outreach before use.

## AI assistance and ownership
Document your actual implementation decisions, code changes, debugging, and testing here before submitting. Disclose any AI coding assistance accurately.
