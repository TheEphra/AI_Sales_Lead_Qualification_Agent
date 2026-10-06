import pandas as pd


def score_need(need_level):
    """Score the urgency/severity of the lead's business need."""

    scores = {
        "High": 25,
        "Medium": 15,
        "Low": 5,
    }

    return scores.get(str(need_level).strip(), 0)


def score_budget(budget):
    """Score the lead according to available purchase budget."""

    if pd.isna(budget):
        return 0

    if budget >= 50000:
        return 20
    if budget >= 20000:
        return 15
    if budget >= 10000:
        return 10
    if budget >= 5000:
        return 5

    return 0


def score_timeline(timeline):
    """Score purchasing urgency based on expected implementation timeline."""

    scores = {
        "0-3 months": 15,
        "3-6 months": 10,
        "6-12 months": 5,
    }

    return scores.get(str(timeline).strip(), 0)


def score_authority(job_title):
    """Score decision-making authority based on job title."""

    title = str(job_title).lower()

    decision_maker_keywords = [
        "ceo",
        "founder",
        "co-founder",
        "chief",
        "vp",
        "vice president",
        "director",
        "head",
    ]

    manager_keywords = [
        "manager",
        "lead",
    ]

    if any(keyword in title for keyword in decision_maker_keywords):
        return 15

    if any(keyword in title for keyword in manager_keywords):
        return 10

    return 5


def score_company_fit(company_size, industry):
    """Score how well the company matches the target customer profile."""

    size = str(company_size).strip()
    industry = str(industry).strip()

    score = 0

    suitable_sizes = [
        "51-200",
        "201-500",
        "501-1000",
        "1001-5000",
    ]

    target_industries = [
        "SaaS",
        "Software",
        "IT Services",
        "FinTech",
        "E-commerce",
        "Retail",
        "Logistics",
        "Healthcare",
        "Education",
    ]

    if size in suitable_sizes:
        score += 5

    if industry in target_industries:
        score += 5

    return min(score, 10)


def score_engagement(website_visits, email_engagement):
    """Score behavioral engagement with the product/business."""

    score = 0

    if pd.notna(website_visits):
        if website_visits >= 20:
            score += 5
        elif website_visits >= 10:
            score += 3
        elif website_visits >= 5:
            score += 1

    engagement = str(email_engagement).strip().lower()

    if engagement == "high":
        score += 5
    elif engagement == "medium":
        score += 3
    elif engagement == "low":
        score += 1

    return min(score, 10)


def score_intent(demo_requested, pricing_interest):
    """Score explicit purchase intent."""

    score = 0

    if str(demo_requested).strip().lower() == "yes":
        score += 3

    if str(pricing_interest).strip().lower() == "yes":
        score += 2

    return score


def get_priority(score):
    """Convert the qualification score into a priority tier."""

    if score >= 80:
        return "Hot"

    if score >= 50:
        return "Warm"

    return "Cold"


def get_score_breakdown(lead):
    """
    Return the individual qualification factors.

    Maximum possible score:
        Need       = 25
        Budget     = 20
        Timeline   = 15
        Authority  = 15
        Company Fit = 10
        Engagement = 10
        Intent     = 5
        ----------------
        Total      = 100
    """

    return {
        "Need": score_need(lead["need_level"]),
        "Budget": score_budget(lead["budget"]),
        "Timeline": score_timeline(lead["timeline"]),
        "Authority": score_authority(lead["job_title"]),
        "Company Fit": score_company_fit(
            lead["company_size"],
            lead["industry"],
        ),
        "Engagement": score_engagement(
            lead["website_visits"],
            lead["email_engagement"],
        ),
        "Intent": score_intent(
            lead["demo_requested"],
            lead["pricing_interest"],
        ),
    }


def calculate_lead_score(lead):
    """Calculate the complete deterministic qualification score."""

    breakdown = get_score_breakdown(lead)

    return sum(breakdown.values())


def score_all_leads(df):
    """Score every lead and assign a priority tier."""

    df = df.copy()

    df["qualification_score"] = df.apply(
        calculate_lead_score,
        axis=1,
    )

    df["priority"] = df["qualification_score"].apply(
        get_priority
    )

    return df