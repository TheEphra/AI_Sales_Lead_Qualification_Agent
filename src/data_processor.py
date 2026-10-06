import pandas as pd


REQUIRED_COLUMNS = [
    "lead_id",
    "name",
    "company",
    "industry",
    "company_size",
    "job_title",
    "location",
    "budget",
    "timeline",
    "need_level",
    "product_interest",
    "website_visits",
    "email_engagement",
    "demo_requested",
    "pricing_interest",
    "previous_contact",
    "pain_point",
    "notes",
]


TEXT_COLUMNS = [
    "name",
    "company",
    "industry",
    "company_size",
    "job_title",
    "location",
    "timeline",
    "need_level",
    "product_interest",
    "email_engagement",
    "demo_requested",
    "pricing_interest",
    "previous_contact",
    "pain_point",
    "notes",
]


NUMERIC_COLUMNS = [
    "budget",
    "website_visits",
]


def validate_columns(df: pd.DataFrame) -> None:
    """Validate that the uploaded dataset contains all required columns."""

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )


def clean_leads(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and normalize lead data."""

    df = df.copy()

    for column in TEXT_COLUMNS:
        df[column] = (
            df[column]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
        )

    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    return df


def load_leads(file) -> pd.DataFrame:
    """Load, validate, and clean a lead CSV file."""

    df = pd.read_csv(file)

    validate_columns(df)

    return clean_leads(df)