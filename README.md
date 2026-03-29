# FinePrint AI 🕵️‍♂️ (Hackathon Edition)

FinePrint AI is an autonomous **Financial Compliance Agent** that audits complex 
loan agreements and vendor contracts against Indian regulatory guardrails — 
in under 15 seconds.

Instead of human analysts taking 45+ minutes to manually cross-reference 
15-page contracts against dense regulatory rulebooks, FinePrint ingests the PDF 
and runs it through a **deterministic 6-Agent reasoning pipeline** that flags 
violations, verifies them, cites specific regulatory rules, and generates 
compliant rewrites — with full auditability at every step.

---

## 🤖 The 6-Agent Pipeline

Regulatory Scraper  — Extrapolates new compliance laws from live RBI Circulars and injects into DB
↓
PDF Upload
↓
Parser Agent        — Segments raw text into labelled contract clauses
↓
Knowledge Agent     — Injects live RBI / CPA / SEBI regulatory context per clause
↓
Compliance Agent    — [LLM Call 1] Audits every clause, flags violations with citations
↓
Verification Agent  — [LLM Call 2] Reviews each flag for confidence (HIGH/MEDIUM/LOW)
LOW confidence → routed to `needs_human_review` (not auto-rewritten)
↓
Rewrite Agent       — [LLM Call 3] Generates compliant replacements for verified violations
↓
Risk Engine         — Computes weighted severity score (0–100)
↓
Audit Report        — Full PDF export with citations, rewrites, and human-review flags

**Stack:** FastAPI · Google Gemini 2.5 Flash · PyMuPDF · Pydantic · Next.js · TailwindCSS

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js v18+
- Google Gemini API Key

### 1. Backend (FastAPI)

```bash
cd fineprint-backend
pip install -r requirements.txt
# Create a .env file:
# GEMINI_API_KEY=your-api-key-here
python -m uvicorn main:app --reload
# Running at http://127.0.0.1:8000
```

### 2. Frontend (Next.js)

```bash
cd fineprint-frontend
npm install
npm run dev
# Open http://localhost:3000
```

---

## 🧪 Testing the Demo
A real sample contract is included in the repo:
`fineprint-backend/Hackathon_Demo_Contract.pdf`

- Drag and drop Hackathon_Demo_Contract.pdf into the dashboard
- Click Initiate Audit
- The pipeline runs all 3 LLM calls and returns a full audit report

> **No API key?** If Gemini is unavailable, the system falls back to a pre-computed audit response with the same schema, so the demo UI always renders correctly. A `"mode": "demo"` flag in the response payload identifies this state.

---

## 📊 Quantified Impact

| Metric | Before | After |
|---|---|---|
| Audit time per contract | 45 min | < 15 sec |
| Annual analyst hours (10K contracts) | 7,500 hrs | 41.6 hrs |
| Annual labour cost | ₹60,00,000 | ₹40,000 (API cost) |
| RBI fine exposure | ₹50L+ per violation | Near-zero |

_Assumptions: 10,000 contracts/yr · ₹800/hr analyst cost · ₹4/contract API cost_
