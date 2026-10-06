import pandas as pd

from src.scoring_engine import (
    score_need,
    score_budget,
    score_timeline,
    score_authority,
    score_company_fit,
    score_engagement,
    score_intent,
    get_priority,
    get_score_breakdown,
)


def test_need_score():
    assert score_need("High") == 25
    assert score_need("Medium") == 15
    assert score_need("Low") == 5


def test_budget_score():
    assert score_budget(50000) == 20
    assert score_budget(20000) == 15
    assert score_budget(10000) == 10
    assert score_budget(5000) == 5
    assert score_budget(1000) == 0


def test_timeline_score():
    assert score_timeline("0-3 months") == 15
    assert score_timeline("3-6 months") == 10
    assert score_timeline("6-12 months") == 5
    assert score_timeline("Unknown") == 0


def test_authority_score():
    assert score_authority("CEO") == 15
    assert score_authority("Operations Manager") == 10
    assert score_authority("Sales Executive") == 5


def test_company_fit():
    assert score_company_fit("201-500", "SaaS") == 10
    assert score_company_fit("11-50", "Other Industry") == 0


def test_engagement_score():
    assert score_engagement(25, "High") == 10
    assert score_engagement(12, "Medium") == 6
    assert score_engagement(2, "Low") == 1


def test_intent_score():
    assert score_intent("Yes", "Yes") == 5
    assert score_intent("Yes", "No") == 3
    assert score_intent("No", "No") == 0


def test_priority_boundaries():
    assert get_priority(80) == "Hot"
    assert get_priority(79) == "Warm"
    assert get_priority(50) == "Warm"
    assert get_priority(49) == "Cold"


def test_score_breakdown():
    lead = {
        "need_level": "High",
        "budget": 50000,
        "timeline": "0-3 months",
        "job_title": "CEO",
        "company_size": "201-500",
        "industry": "SaaS",
        "website_visits": 25,
        "email_engagement": "High",
        "demo_requested": "Yes",
        "pricing_interest": "Yes",
    }

    breakdown = get_score_breakdown(lead)

    assert breakdown["Need"] == 25
    assert breakdown["Budget"] == 20
    assert breakdown["Timeline"] == 15
    assert breakdown["Authority"] == 15
    assert breakdown["Company Fit"] == 10
    assert breakdown["Engagement"] == 10
    assert breakdown["Intent"] == 5

    assert sum(breakdown.values()) == 100