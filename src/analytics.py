import pandas as pd


def get_pipeline_summary(df: pd.DataFrame) -> dict:
    """Return high-level sales pipeline metrics."""

    total_leads = len(df)

    hot_leads = int(
        (df["priority"] == "Hot").sum()
    )

    warm_leads = int(
        (df["priority"] == "Warm").sum()
    )

    cold_leads = int(
        (df["priority"] == "Cold").sum()
    )

    average_score = (
        round(df["qualification_score"].mean(), 1)
        if total_leads
        else 0
    )

    return {
        "total_leads": total_leads,
        "hot_leads": hot_leads,
        "warm_leads": warm_leads,
        "cold_leads": cold_leads,
        "average_score": average_score,
    }


def get_priority_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Return lead counts grouped by priority."""

    return (
        df["priority"]
        .value_counts()
        .reindex(
            ["Hot", "Warm", "Cold"],
            fill_value=0,
        )
        .rename_axis("priority")
        .reset_index(name="leads")
    )


def get_score_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Return lead counts grouped into score ranges."""

    bins = [0, 49, 64, 79, 100]

    labels = [
        "0-49",
        "50-64",
        "65-79",
        "80-100",
    ]

    distribution = pd.cut(
        df["qualification_score"],
        bins=bins,
        labels=labels,
        include_lowest=True,
    )

    return (
        distribution
        .value_counts()
        .sort_index()
        .rename_axis("score_range")
        .reset_index(name="leads")
    )


def get_industry_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Return lead count and average score by industry."""

    return (
        df.groupby("industry")
        .agg(
            leads=("lead_id", "count"),
            average_score=("qualification_score", "mean"),
        )
        .reset_index()
        .sort_values(
            "average_score",
            ascending=False,
        )
    )


def get_budget_analysis(df: pd.DataFrame) -> dict:
    """Return basic budget statistics."""

    budgets = pd.to_numeric(
        df["budget"],
        errors="coerce",
    ).dropna()

    if budgets.empty:
        return {
            "average_budget": 0,
            "maximum_budget": 0,
            "total_budget": 0,
        }

    return {
        "average_budget": round(budgets.mean(), 0),
        "maximum_budget": round(budgets.max(), 0),
        "total_budget": round(budgets.sum(), 0),
    }