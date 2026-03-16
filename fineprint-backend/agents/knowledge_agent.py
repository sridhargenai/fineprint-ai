import os
import json

def load_rules() -> list[dict]:
    rules_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'compliance_rules.json')
    try:
        with open(rules_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("rules", [])
    except Exception as e:
        print(f"Error loading rules: {e}")
        return []

def get_formatted_rules() -> str:
    rules = load_rules()
    formatted = ""
    for r in rules:
        formatted += f"- ID: {r['id']} | Law: {r['law']} | Severity: {r['severity']} | Rule: {r['rule']}\n"
    return formatted
