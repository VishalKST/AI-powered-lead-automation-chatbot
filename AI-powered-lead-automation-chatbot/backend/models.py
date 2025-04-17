# models.py
def score_lead(lead_data):
    score = 0

    # Rule-based scoring
    budget = int(lead_data.get("budget", 0))
    industry = lead_data.get("industry", "").lower()
    service = lead_data.get("service", "").lower()

    if budget >= 100000:
        score += 40
    elif budget >= 50000:
        score += 25
    else:
        score += 10

    if service in ["website", "mobile app"]:
        score += 30
    elif service in ["seo", "branding", "marketing"]:
        score += 20

    if industry in ["tech", "ecommerce", "finance"]:
        score += 30
    else:
        score += 10

    return min(score, 100)
