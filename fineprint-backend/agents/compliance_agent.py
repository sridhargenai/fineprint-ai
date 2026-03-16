from google import genai
from google.genai import types
import json

def evaluate_clauses(clauses: list[str], rules_text: str, client: genai.Client) -> dict:
    system_prompt = (
        "You are FinePrint Agent, an autonomous Financial Compliance Auditor. "
        "Your job is to read draft financial contracts, evaluate clauses, "
        "and audit them strictly against current regulatory guardrails. You must provide an audit trail for your reasoning."
    )
    
    user_prompt = f"""
    Here are your specific regulatory guardrails to enforce:
    {rules_text}
    
    Here is the extracted text split into clauses from the financial contract under review:
    {json.dumps(clauses)}
    
    Analyze the clauses. Return the data in the exact following JSON format:
    {{
        "evaluations": [
            {{
                "clause_text": "Exact text from contract...",
                "is_compliant": true or false,
                "violation_reason": "Explain exactly why it violates a rule, or null if compliant",
                "regulatory_citation": "Cite the specific rule/guardrail broken (e.g. RBI Fair Practices Code), or null",
                "severity": "major, medium, minor, or null"
            }}
        ]
    }}
    """
    
    full_prompt = system_prompt + "\n\n---\n\n" + user_prompt
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=full_prompt,
        config=types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type="application/json"
        )
    )
    
    try:
        parsed_data = json.loads(response.text)
        return parsed_data
    except Exception as e:
        print(f"Error parsing Gemini response: {e}")
        return {"evaluations": []}
