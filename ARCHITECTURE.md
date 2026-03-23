# FinePrint AI — Architecture Document

## Overview
FinePrint AI is a 6-agent autonomous compliance pipeline that audits Indian 
loan agreements and vendor contracts against RBI, CPA, and SEBI guardrails. 
The system is designed around three principles: determinism (low-temperature 
LLM calls with strict Pydantic schemas), auditability (every decision carries 
a regulatory citation), and resilience (graceful fallback at every failure point).

---

## Agent Roles & Responsibilities

| Agent | Type | Role |
|---|---|---|
| **Regulatory Scraper** | Service | Scrapes live RBI circulars, extracts new compliance rules via Gemini, appends to `compliance_rules.json` |
| **Parser Agent** | LLM-assisted | Segments raw PDF text into labelled contract clauses (parties, fees, penalties, cooling-off, etc.) |
| **Knowledge Agent** | Deterministic | Loads `compliance_rules.json` and formats rules into a structured prompt context block |
| **Compliance Agent** | LLM Call 1 | Audits every clause against injected rules. Returns structured violation objects with `regulatory_citation` and `severity` |
| **Verification Agent** | LLM Call 2 | Reviews each violation flag for confidence (HIGH / MEDIUM / LOW). LOW confidence items are routed to `needs_human_review` and never auto-rewritten |
| **Rewrite Agent** | LLM Call 3 | Generates legally compliant replacement clauses for all verified violations, with full statutory citations |

---

## Pipeline Flow

```
[RBI Website] 
    ↓ (on-demand via POST /refresh-regulations)
Regulatory Scraper → compliance_rules.json

[PDF Upload via FastAPI]
    ↓
PyMuPDF Text Extraction
    ↓
Parser Agent
    ↓
Knowledge Agent (injects regulatory context)
    ↓
Compliance Agent ————————— [LLM Call 1]
    ↓
Verification Agent ————————[LLM Call 2]
    ↓                              ↓
verified_violations         needs_human_review
    ↓                              ↓
Rewrite Agent ————————————[LLM Call 3]
    ↓                              ↓
Risk Engine (0–100 score)          ↓
    ↓                              ↓
Audit Report ←—————————————————————
```

---

## Agent Communication
All agents are orchestrated sequentially by `main.py`. Data is passed between 
agents as strictly typed Pydantic objects — no agent receives unvalidated input. 
The output of each agent is the input of the next, creating a clean, 
inspectable chain where every transformation is traceable.

---

## Tool Integrations

| Integration | Purpose |
|---|---|
| **Google Gemini 2.5 Flash** | Powers all 3 LLM calls at temperature 0.1 for deterministic output |
| **PyMuPDF (fitz)** | PDF ingestion and raw text extraction with zero data loss |
| **Pydantic** | Strict JSON schema enforcement on all LLM outputs |
| **BeautifulSoup4** | HTML parsing for live RBI circular scraping |
| **FastAPI** | REST API backend with typed request/response models |
| **Next.js + TailwindCSS** | Auditor dashboard frontend |

---

## Error Handling & Resilience

| Failure Point | Handling |
|---|---|
| Gemini API unavailable (429 / no key) | try/except catches exception, returns pre-computed mock audit with `"mode": "demo"` flag |
| Verification Agent call fails | All Compliance Agent violations treated as HIGH confidence and passed to Rewrite Agent |
| Regulatory Scraper finds no new rules | Existing `compliance_rules.json` unchanged, pipeline unaffected |
| PDF contains no extractable text | PyMuPDF returns empty string, Parser Agent returns empty clause list, audit returns clean report |

---

## Compliance Guardrails
The system enforces the following Indian regulatory frameworks:
- **RBI Fair Practices Code** — interest rate disclosure, cooling-off periods, penalty reasonableness
- **Consumer Protection Act 2019** — unfair contract terms, hidden charges
- **SEBI Guidelines** — applicable to vendor and investment-linked agreements

Every violation flagged by the Compliance Agent must include:
- `regulatory_citation` — the specific rule ID (e.g. `RBI_FPC_001`)
- `severity` — `major` or `medium`, used by the Risk Engine
- `compliant` — boolean

LOW confidence violations flagged by the Verification Agent are never 
auto-rewritten. They are surfaced to the human reviewer with full context, 
preserving human oversight for ambiguous edge cases.

---

## Quantified Impact Model

| Metric | Before | After |
|---|---|---|
| Audit time per contract | 45 min | < 15 sec |
| Annual analyst hours (10K contracts) | 7,500 hrs | 41.6 hrs |
| Annual labour cost | ₹60,00,000 | ₹40,000 (API cost) |
| RBI fine exposure | ₹50L+ per violation | Near-zero |

*Assumptions: 10,000 contracts/yr · ₹800/hr analyst cost · ₹4/contract 
API cost · 95%+ AI flag accuracy · Cloud hosting <₹4,000/mo*
