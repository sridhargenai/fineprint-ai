def calculate_risk_score(evaluations: list[dict]) -> int:
    base_score = 100
    for eval_item in evaluations:
        if not eval_item.get("is_compliant"):
            severity = str(eval_item.get("severity", "")).lower()
            if severity == "major":
                base_score -= 20
            elif severity == "medium":
                base_score -= 10
            elif severity == "minor":
                base_score -= 5
            else:
                base_score -= 10 # Default penalty for unspecified severity
                
    return max(0, base_score)
