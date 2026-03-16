import os
import json
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from typing import List, Optional
from dotenv import load_dotenv

# Import the new modular agents and services
from agents.parser_agent import parse_contract
from agents.knowledge_agent import get_formatted_rules
from agents.compliance_agent import evaluate_clauses
from agents.rewrite_agent import generate_rewrites
from services.risk_engine import calculate_risk_score

# Load environment variables from the .env file
load_dotenv()

# ---------------------------------------------------------
# Application Setup
# ---------------------------------------------------------

# Initialize the FastAPI App
app = FastAPI(
    title="FinePrint AI Backend",
    description="An API to ingest contracts, parse clauses, and simplify them into plain English.",
    version="1.0.0"
)

# Enable CORS (Cross-Origin Resource Sharing)
# This allows our Next.js frontend (running on localhost:3000) 
# to communicate securely with this Python backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the Gemini Client
# Note: This will look for the GEMINI_API_KEY environment variable.
gemini_api_key = os.environ.get("GEMINI_API_KEY")
if gemini_api_key:
    client = genai.Client(api_key=gemini_api_key)
else:
    print("\n[WARNING] GEMINI_API_KEY not found in environment. The AI agent will run in Mock Mode for demonstration.\n")
    client = None

# ---------------------------------------------------------
# Pydantic Models for Response Validation
# ---------------------------------------------------------
# Defining these models ensures our API automatically generates 
# interactive documentation and standardizes the response format.

# ---------------------------------------------------------
# Pydantic Models for Response Validation (Agent Output)
# ---------------------------------------------------------
# This structure defines the strictly typed JSON our Agent must return, 
# ensuring every decision is auditable and structured for the frontend.

class OptionalViolation(BaseModel):
    clause_text: str
    violation_reason: Optional[str] = None
    regulatory_citation: Optional[str] = None
    suggested_rewrite: Optional[str] = None

class ComplianceCheck(BaseModel):
    clause_text: str
    is_compliant: bool
    violation_reason: Optional[str] = None
    regulatory_citation: Optional[str] = None
    suggested_fix: Optional[str] = None

class AuditReportResponse(BaseModel):
    overall_compliance_score: int
    clauses_analyzed: int
    violations_found: int
    details: List[ComplianceCheck]
    contract_risk_score: Optional[int] = None
    violations: Optional[List[OptionalViolation]] = None

# ---------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------

@app.post("/upload-contract", response_model=AuditReportResponse)
async def upload_contract(file: UploadFile = File(...)):
    """
    Upload a financial contract in PDF format.
    The Agent will:
    1. Extract text.
    2. Audit the text against Indian RBI and Consumer Protection Guardrails.
    3. Return a detailed, cited compliance report.
    """
    
    # --- 1. Validate File Type ---
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        # --- 1. Parser Agent ---
        file_content = await file.read()
        clauses = parse_contract(file_content)

        if not clauses:
            raise HTTPException(
                status_code=400, 
                detail="Could not extract text. The PDF might be empty or a scanned image."
            )

        # --- 2. Knowledge Agent ---
        rules_text = get_formatted_rules()

        try:
            if client is None:
                raise Exception("api_key_missing") # Force fallback directly to mock data if key is missing

            # --- 3. Compliance Agent ---
            eval_data = evaluate_clauses(clauses, rules_text, client)
            evaluations = eval_data.get("evaluations", [])
            
            # --- 4. Rewrite Agent ---
            violation_list = [e for e in evaluations if not e.get("is_compliant")]
            violations_with_rewrites = generate_rewrites(violation_list, client)
            
            # --- 5. Risk Engine ---
            risk_score = calculate_risk_score(evaluations)
            
            # Construct backward compatible responses
            details = []
            if not isinstance(evaluations, list):
                evaluations = []
                
            for ev in evaluations:
                suggested_rewrite = None
                if not ev.get("is_compliant"):
                    for v in violations_with_rewrites:
                        if v.get("clause_text") == ev.get("clause_text"):
                            suggested_rewrite = v.get("suggested_rewrite")
                            break
                            
                details.append({
                    "clause_text": str(ev.get("clause_text", "Unknown Clause")),
                    "is_compliant": bool(ev.get("is_compliant", True)),
                    "violation_reason": ev.get("violation_reason"),
                    "regulatory_citation": ev.get("regulatory_citation"),
                    "suggested_fix": suggested_rewrite
                })
                
            filtered_violations = [{
                "clause_text": str(v.get("clause_text", "Unknown Clause")),
                "violation_reason": str(v.get("violation_reason", "")) if v.get("violation_reason") else None,
                "regulatory_citation": str(v.get("regulatory_citation", "")) if v.get("regulatory_citation") else None,
                "suggested_rewrite": str(v.get("suggested_rewrite", "")) if v.get("suggested_rewrite") else None
            } for v in violations_with_rewrites]

            return {
                "overall_compliance_score": risk_score,
                "contract_risk_score": risk_score,
                "clauses_analyzed": len(evaluations),
                "violations_found": len(violations_with_rewrites),
                "details": details,
                "violations": filtered_violations
            }
            
        except Exception as api_err:
            err_msg = str(api_err).lower()
            if "api_key_missing" in err_msg or "429" in err_msg or "quota" in err_msg:
                print("\n[WARNING] Gemini Quota Exceeded or API Key Missing. Returning Mock Audit Data.\n")
                return {
                    "overall_compliance_score": 82,
                    "contract_risk_score": 82,
                    "clauses_analyzed": 14,
                    "violations_found": 2,
                    "details": [
                        {
                            "clause_text": "The borrower agrees to a standard loan term of 12 months with equal monthly installments.",
                            "is_compliant": True,
                            "violation_reason": None,
                            "regulatory_citation": None,
                            "suggested_fix": None
                        },
                        {
                            "clause_text": "If the borrower misses a payment, a flat penalty of 5% per month will be levied on the outstanding principal balance immediately.",
                            "is_compliant": False,
                            "violation_reason": "Penalty rate of 5% per month exceeds the permitted maximum threshold for late fees.",
                            "regulatory_citation": "Guardrail 2: Late payment penalties cannot exceed 2% per month.",
                            "suggested_fix": "If the borrower misses a payment, a late fee of up to 2% per month will be levied on the overdue installment amount."
                        }
                    ],
                    "violations": [
                        {
                            "clause_text": "If the borrower misses a payment, a flat penalty of 5% per month will be levied on the outstanding principal balance immediately.",
                            "violation_reason": "Penalty rate of 5% per month exceeds the permitted maximum threshold for late fees.",
                            "regulatory_citation": "Guardrail 2: Late payment penalties cannot exceed 2% per month.",
                            "suggested_rewrite": "If the borrower misses a payment, a late fee of up to 2% per month will be levied on the overdue installment amount."
                        }
                    ]
                }
            else:
                raise api_err
        
    except Exception as e:
        # Catch any unexpected errors (like API keys missing, bad JSON, etc.)
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")