from google import genai
from google.genai import types
import json

def generate_rewrites(violations: list[dict], client: genai.Client) -> list[dict]:
    if not violations:
        return []

    system_prompt = (
        "You are a Legal Compliance Assistant. Your job is to rewrite the given violating clauses "
        "to comply with the cited regulations."
    )
    
    # We only need to send the required context to save tokens and avoid confusion
    context = [{"clause": v["clause_text"], "reason": v["violation_reason"], "citation": v["regulatory_citation"]} for v in violations]
    
    user_prompt = f"""
    Please provide an improved rewrite for each of the following violations to make them completely compliant.
    Return the data in the exact following JSON format:
    {{
      "rewrites": [
        "compliant rewritten clause 1",
        "... and so on matching the length of the violations array"
      ]
    }}
    
    Violations:
    {json.dumps(context)}
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=system_prompt + "\n\n" + user_prompt,
        config=types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type="application/json"
        )
    )
    
    try:
        rewrites_data = json.loads(response.text).get("rewrites", [])
        for chunk, rewrite_text in zip(violations, rewrites_data):
            chunk["suggested_rewrite"] = rewrite_text
    except Exception as e:
        print(f"Error generating rewrites: {e}")
        for chunk in violations:
            chunk["suggested_rewrite"] = "Error generating rewrite."
            
    return violations
