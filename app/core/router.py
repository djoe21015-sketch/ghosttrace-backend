from app.models.target import Target

# Placeholder routing logic
def route_scan(target: Target):
    ttype = target.target_type.lower()

    if ttype == "email":
        return ["email_scraper"]
    elif ttype == "domain":
        return ["domain_scraper"]
    elif ttype == "ip":
        return ["ip_scraper"]
    elif ttype == "phone":
        return ["phone_scraper"]
    elif ttype == "username":
        return ["username_scraper"]
    else:
        return ["basic_scraper"]
