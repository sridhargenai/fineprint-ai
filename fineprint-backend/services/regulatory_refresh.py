import os
import json
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel
from typing import List
import google.genai as genai

class Rule(BaseModel):
    id: str
    law: str
    rule: str
    severity: str

class RuleList(BaseModel):
    rules: List[Rule]

def run_refresh(client) -> dict:
    url = "https://www.rbi.org.in/Scripts/BS_CircularIndexDisplay.aspx"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Scrape 10 recent circulars
        circulars = []
        # Typically the table contains class 'tablebg'
        table = soup.find('table', class_='tablebg')
        if not table:
            # Fallback for dynamic layout changes
            links = soup.find_all('a', class_='link2')
        else:
            links = table.find_all('a', class_='link2')

        for link in links:
            title = link.get_text(strip=True)
            href = link.get('href')
            if title and href:
                # Basic filter to ignore generic nav links
                circulars.append({"title": title, "url": f"https://www.rbi.org.in/Scripts/{href}"})
                if len(circulars) >= 10:
                    break

        new_extracted_rules = []

        # Gemini Prompting for each circular
        prompt_instruction = (
            "You are a regulatory expert. Read this RBI circular title and extract any new lending "
            "compliance rules it implies. Return a JSON array of objects, each with fields: "
            "id (format RBI_LIVE_001 incrementing), law, rule, severity (major or minor). "
            "If no actionable lending rules are found, return an empty array."
        )

        for circ in circulars:
            full_prompt = f"{prompt_instruction}\n\nTitle: {circ['title']}"
            
            try:
                ai_response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=full_prompt,
                    config=genai.types.GenerateContentConfig(
                        temperature=0.1,
                        response_mime_type="application/json",
                        response_schema=RuleList,
                    ),
                )
                
                data = json.loads(ai_response.text)
                for r in data.get("rules", []):
                    # Ensure rule format is clean
                    new_extracted_rules.append({
                        "id": r.get("id"),
                        "law": r.get("law"),
                        "rule": r.get("rule"),
                        "severity": r.get("severity", "minor")
                    })
            except Exception as e:
                print(f"Failed to process circular '{circ['title']}': {e}")
                continue

        # Load existing rules
        rules_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'compliance_rules.json')
        existing_rules = []
        if os.path.exists(rules_path):
            with open(rules_path, 'r', encoding='utf-8') as f:
                try:
                    existing_data = json.load(f)
                    existing_rules = existing_data.get("rules", [])
                except json.JSONDecodeError:
                    existing_rules = []

        existing_rule_texts = {r.get('rule', '').lower().strip() for r in existing_rules}
        
        added_rules_count = 0
        added_texts = []

        # Deduplicate and append
        for rule in new_extracted_rules:
            rule_text = rule.get('rule', '').lower().strip()
            if rule_text and rule_text not in existing_rule_texts:
                existing_rules.append(rule)
                existing_rule_texts.add(rule_text)
                added_texts.append(rule.get('rule'))
                added_rules_count += 1

        # Save back to file
        with open(rules_path, 'w', encoding='utf-8') as f:
            json.dump({"rules": existing_rules}, f, indent=4)

        return {
            "circulars_scanned": len(circulars),
            "new_rules_added": added_rules_count,
            "added_rule_details": added_texts
        }

    except Exception as network_e:
        print(f"Network error during scraping: {network_e}")
        return {"error": str(network_e)}
