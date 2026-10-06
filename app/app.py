from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.action_engine import get_recommended_action
from src.analytics import (
    get_budget_analysis,
    get_industry_analysis,
    get_pipeline_summary,
    get_priority_distribution,
    get_score_distribution,
)
from src.data_processor import load_leads
from src.llm_service import analyze_lead
from src.scoring_engine import get_score_breakdown, score_all_leads


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="LeadIQ | AI Sales Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# DARK PROFESSIONAL THEME
# ============================================================

st.markdown(
    """
    <style>

    @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
    );

    html,
    body,
    [class*="css"] {
        font-family: "Inter", "Segoe UI", sans-serif;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 75% 0%,
                rgba(99, 102, 241, 0.10),
                transparent 28%
            ),
            radial-gradient(
                circle at 10% 30%,
                rgba(139, 92, 246, 0.05),
                transparent 25%
            ),
            #090b10;
        color: #f8fafc;
    }

    .main {
        background: transparent;
    }

    .block-container {
        max-width: 1400px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    #MainMenu,
    footer {
        visibility: hidden;
    }

    header {
        background: transparent !important;
    }

    [data-testid="stDecoration"] {
        display: none;
    }

    /* ========================================================
       TYPOGRAPHY
       ======================================================== */

    h1 {
        color: #f8fafc !important;
        font-size: 2.35rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.045em !important;
    }

    h2 {
        color: #f1f5f9 !important;
        font-size: 1.5rem !important;
        font-weight: 750 !important;
        letter-spacing: -0.025em !important;
    }

    h3 {
        color: #e2e8f0 !important;
        font-weight: 700 !important;
    }

    p {
        color: #94a3b8;
    }

    .stCaption {
        color: #64748b !important;
    }

    /* ========================================================
       NAVIGATION
       ======================================================== */

    [data-testid="stRadio"] > div {
        gap: 0.25rem;
    }

    [data-testid="stRadio"] label {
        border-radius: 8px;
        padding: 0.45rem 0.8rem;
        color: #94a3b8;
        font-weight: 600;
    }

    [data-testid="stRadio"] label:hover {
        background: #171a23;
        color: #c4b5fd;
    }

    [data-testid="stRadio"] label:has(input:checked) {
        background: #1e1b4b;
        color: #a78bfa;
    }

    /* ========================================================
       METRICS
       ======================================================== */

    [data-testid="stMetric"] {
        background: linear-gradient(
            145deg,
            #141720,
            #101219
        );

        border: 1px solid #252a36;
        border-radius: 14px;
        padding: 1.15rem 1.25rem;

        box-shadow:
            0 10px 30px rgba(0, 0, 0, 0.18);
    }

    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-weight: 600 !important;
        font-size: 0.78rem !important;
    }

    [data-testid="stMetricValue"] {
        color: #f8fafc !important;
        font-weight: 800 !important;
    }

    /* ========================================================
       BUTTONS
       ======================================================== */

    .stButton > button {
        border-radius: 9px;
        border: 1px solid #2b3140;
        background: #151821;
        color: #dbe3ef;
        font-weight: 600;
        min-height: 2.45rem;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        background: #1d2130;
        border-color: #6366f1;
        color: #c4b5fd;
    }

    .stButton > button[kind="primary"] {
        background: #4f46e5;
        border-color: #6366f1;
        color: white;

        box-shadow:
            0 6px 20px rgba(79, 70, 229, 0.22);
    }

    .stButton > button[kind="primary"]:hover {
        background: #6366f1;
        color: white;
    }

    /* ========================================================
       INPUTS
       ======================================================== */

    .stTextInput input,
    .stNumberInput input {
        background: #11141b !important;
        color: #f1f5f9 !important;
        border: 1px solid #2b3140 !important;
        border-radius: 9px !important;
    }

    div[data-baseweb="select"] > div {
        background: #11141b !important;
        border-color: #2b3140 !important;
        border-radius: 9px !important;
    }

    /* ========================================================
       FILE UPLOADER
       ======================================================== */

    [data-testid="stFileUploader"] {
        background: #11141b;
        border: 1px dashed #3b4252;
        border-radius: 12px;
        padding: 0.7rem;
    }

    /* ========================================================
       CARDS
       ======================================================== */

    [data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(
            145deg,
            rgba(20, 23, 32, 0.96),
            rgba(15, 17, 24, 0.96)
        );

        border: 1px solid #252a36 !important;
        border-radius: 14px !important;

        box-shadow:
            0 12px 35px rgba(0, 0, 0, 0.16);
    }

    /* ========================================================
       TABLES
       ======================================================== */

    [data-testid="stDataFrame"] {
        border: 1px solid #252a36;
        border-radius: 12px;
        overflow: hidden;
    }

    /* ========================================================
       ALERTS
       ======================================================== */

    [data-testid="stAlert"] {
        border-radius: 10px;
    }

    /* ========================================================
       DIVIDERS
       ======================================================== */

    hr {
        border-color: #202532 !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "leads_df" not in st.session_state:
    st.session_state.leads_df = None

if "ai_analyses" not in st.session_state:
    st.session_state.ai_analyses = {}

if "selected_lead_id" not in st.session_state:
    st.session_state.selected_lead_id = None

if "page" not in st.session_state:
    st.session_state.page = "Overview"


# ============================================================
# HELPERS
# ============================================================

def load_uploaded_dataset(uploaded_file):

    try:

        uploaded_df = load_leads(
            uploaded_file
        )

        scored_df = score_all_leads(
            uploaded_df
        )

        st.session_state.leads_df = scored_df
        st.session_state.ai_analyses = {}
        st.session_state.selected_lead_id = None
        st.session_state.page = "Overview"

        return True

    except Exception as error:

        st.error(
            f"Unable to process the CSV: {error}"
        )

        return False


def open_lead(lead_id):

    st.session_state.selected_lead_id = lead_id
    st.session_state.page = "Intelligence"


def priority_label(priority):

    if priority == "Hot":
        return "🔥 HOT"

    if priority == "Warm":
        return "🟡 WARM"

    return "🔵 COLD"


# ============================================================
# HEADER
# ============================================================

brand_col, nav_col = st.columns(
    [1.25, 4.75]
)

with brand_col:

    st.markdown("### ◈ LeadIQ")

    st.caption(
        "AI SALES INTELLIGENCE"
    )


# ============================================================
# EMPTY START SCREEN
# ============================================================

if st.session_state.leads_df is None:

    with nav_col:

        st.caption(
            "Secure · AI-assisted · Data-driven"
        )


    st.divider()

    st.write("")
    st.write("")
    st.write("")


    # --------------------------------------------------------
    # HERO
    # --------------------------------------------------------

    hero_left, hero_right = st.columns(
        [1.4, 1]
    )


    with hero_left:

        st.caption(
            "AI SALES QUALIFICATION PLATFORM"
        )

        st.title(
            "Turn raw leads into\nsales intelligence."
        )

        st.write(
            "LeadIQ analyzes your B2B leads, "
            "scores their buying potential, "
            "and helps sales teams decide "
            "who to contact first."
        )

        st.write("")

        st.markdown(
            "**Deterministic scoring**  ·  "
            "**AI-powered analysis**  ·  "
            "**Actionable recommendations**"
        )


    with hero_right:

        with st.container(border=True):

            st.subheader(
                "Start with your lead data"
            )

            st.write(
                "Upload a CSV file to begin. "
                "No sample records are loaded automatically."
            )

            st.write("")

            uploaded_file = st.file_uploader(
                "Upload your CSV",
                type=["csv"],
                label_visibility="collapsed",
            )

            if uploaded_file is not None:

                if load_uploaded_dataset(
                    uploaded_file
                ):

                    st.success(
                        "Dataset loaded successfully."
                    )

                    st.rerun()


    st.write("")
    st.write("")


    # --------------------------------------------------------
    # PRODUCT FEATURES
    # --------------------------------------------------------

    st.subheader(
        "Built for modern sales teams"
    )

    feature1, feature2, feature3 = st.columns(
        3
    )


    with feature1:

        with st.container(border=True):

            st.markdown(
                "### 🎯 Smart qualification"
            )

            st.write(
                "Evaluate every lead using "
                "need, budget, timeline, authority, "
                "company fit, engagement, and intent."
            )


    with feature2:

        with st.container(border=True):

            st.markdown(
                "### ✦ AI sales intelligence"
            )

            st.write(
                "Generate grounded summaries, "
                "evidence-based reasons, and "
                "practical next actions."
            )


    with feature3:

        with st.container(border=True):

            st.markdown(
                "### ◫ Pipeline analytics"
            )

            st.write(
                "Understand lead quality, priority "
                "distribution, industries, budgets, "
                "and overall pipeline health."
            )


    st.write("")
    st.write("")


    # --------------------------------------------------------
    # HOW IT WORKS
    # --------------------------------------------------------

    st.subheader(
        "How LeadIQ works"
    )

    step1, step2, step3, step4 = st.columns(
        4
    )


    with step1:

        st.markdown(
            "**01 · Upload**"
        )

        st.caption(
            "Import your lead CSV."
        )


    with step2:

        st.markdown(
            "**02 · Qualify**"
        )

        st.caption(
            "Calculate a consistent score."
        )


    with step3:

        st.markdown(
            "**03 · Analyze**"
        )

        st.caption(
            "Generate AI sales intelligence."
        )


    with step4:

        st.markdown(
            "**04 · Act**"
        )

        st.caption(
            "Prioritize the right prospects."
        )


    st.divider()

    st.caption(
        "◈ LeadIQ · AI Sales Intelligence Platform"
    )

    st.stop()


# ============================================================
# DATA EXISTS — APPLICATION NAVIGATION
# ============================================================

df = st.session_state.leads_df


selected_page = st.radio(
    "Navigation",
    [
        "Overview",
        "Pipeline",
        "Intelligence",
        "Analytics",
        "Export",
    ],
    horizontal=True,
    label_visibility="collapsed",
    index=[
        "Overview",
        "Pipeline",
        "Intelligence",
        "Analytics",
        "Export",
    ].index(
        st.session_state.page
    ),
)


if selected_page != st.session_state.page:

    st.session_state.page = selected_page

    st.rerun()


st.divider()


# ============================================================
# DATASET HEADER
# ============================================================

data_col, upload_col = st.columns(
    [4, 1]
)

with data_col:

    st.caption(
        f"● Active dataset · {len(df):,} leads"
    )


with upload_col:

    new_file = st.file_uploader(
        "Replace",
        type=["csv"],
        key="replace_dataset",
        label_visibility="collapsed",
    )

    if new_file is not None:

        if load_uploaded_dataset(
            new_file
        ):

            st.rerun()


# ============================================================
# OVERVIEW
# ============================================================

if st.session_state.page == "Overview":

    st.title(
        "Sales intelligence, simplified."
    )

    st.write(
        "Your lead pipeline at a glance."
    )

    st.write("")


    summary = get_pipeline_summary(
        df
    )


    metric1, metric2, metric3, metric4, metric5 = (
        st.columns(5)
    )


    with metric1:

        st.metric(
            "Total Leads",
            f"{summary['total_leads']:,}",
        )


    with metric2:

        st.metric(
            "Hot Leads",
            f"{summary['hot_leads']:,}",
        )


    with metric3:

        st.metric(
            "Warm Leads",
            f"{summary['warm_leads']:,}",
        )


    with metric4:

        st.metric(
            "Cold Leads",
            f"{summary['cold_leads']:,}",
        )


    with metric5:

        st.metric(
            "Average Score",
            f"{summary['average_score']}/100",
        )


    st.write("")


    chart_left, chart_right = st.columns(
        2
    )


    with chart_left:

        st.subheader(
            "Pipeline distribution"
        )

        priority_df = get_priority_distribution(
            df
        )

        fig = px.bar(
            priority_df,
            x="priority",
            y="leads",
            text="leads",
        )

        fig.update_layout(
            height=340,
            margin=dict(
                l=10,
                r=10,
                t=20,
                b=10,
            ),
            plot_bgcolor="#141720",
            paper_bgcolor="#141720",
            showlegend=False,
            font=dict(
                family="Inter",
                color="#cbd5e1",
            ),
            xaxis_title=None,
            yaxis_title="Leads",
        )

        fig.update_xaxes(
            gridcolor="#252a36"
        )

        fig.update_yaxes(
            gridcolor="#252a36"
        )

        fig.update_traces(
            marker_color="#6366f1",
            textposition="outside",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )


    with chart_right:

        st.subheader(
            "Qualification score"
        )

        score_df = get_score_distribution(
            df
        )

        fig = px.bar(
            score_df,
            x="score_range",
            y="leads",
            text="leads",
        )

        fig.update_layout(
            height=340,
            margin=dict(
                l=10,
                r=10,
                t=20,
                b=10,
            ),
            plot_bgcolor="#141720",
            paper_bgcolor="#141720",
            showlegend=False,
            font=dict(
                family="Inter",
                color="#cbd5e1",
            ),
            xaxis_title=None,
            yaxis_title="Leads",
        )

        fig.update_xaxes(
            gridcolor="#252a36"
        )

        fig.update_yaxes(
            gridcolor="#252a36"
        )

        fig.update_traces(
            marker_color="#8b5cf6",
            textposition="outside",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )


    st.divider()


    st.subheader(
        "Priority opportunities"
    )


    top_leads = (
        df.sort_values(
            "qualification_score",
            ascending=False,
        )
        .head(6)
    )


    for _, lead in top_leads.iterrows():

        with st.container(border=True):

            col1, col2, col3, col4 = st.columns(
                [2.3, 1.5, 1, 1]
            )


            with col1:

                st.markdown(
                    f"**{lead['name']}**"
                )

                st.caption(
                    f"{lead['company']} · "
                    f"{lead['job_title']}"
                )


            with col2:

                st.write(
                    priority_label(
                        lead["priority"]
                    )
                )


            with col3:

                st.metric(
                    "Score",
                    f"{lead['qualification_score']}/100",
                )


            with col4:

                if st.button(
                    "View",
                    key=f"overview_{lead['lead_id']}",
                    use_container_width=True,
                ):

                    open_lead(
                        lead["lead_id"]
                    )

                    st.rerun()


# ============================================================
# PIPELINE
# ============================================================

elif st.session_state.page == "Pipeline":

    st.title(
        "Lead pipeline"
    )

    st.write(
        "Search and filter your qualified prospects."
    )

    st.write("")


    search_col, priority_col, industry_col = (
        st.columns([2, 1, 1])
    )


    with search_col:

        search = st.text_input(
            "Search leads",
            placeholder=(
                "Search name, company, industry..."
            ),
        )


    with priority_col:

        priority_filter = st.selectbox(
            "Priority",
            [
                "All",
                "Hot",
                "Warm",
                "Cold",
            ],
        )


    with industry_col:

        industries = [
            "All"
        ] + sorted(
            df["industry"]
            .dropna()
            .unique()
            .tolist()
        )

        industry_filter = st.selectbox(
            "Industry",
            industries,
        )


    filtered_df = df.copy()


    if search:

        search_lower = search.lower()

        mask = (
            filtered_df["name"]
            .astype(str)
            .str.lower()
            .str.contains(
                search_lower,
                na=False,
            )
            |
            filtered_df["company"]
            .astype(str)
            .str.lower()
            .str.contains(
                search_lower,
                na=False,
            )
            |
            filtered_df["industry"]
            .astype(str)
            .str.lower()
            .str.contains(
                search_lower,
                na=False,
            )
        )

        filtered_df = filtered_df[
            mask
        ]


    if priority_filter != "All":

        filtered_df = filtered_df[
            filtered_df["priority"]
            == priority_filter
        ]


    if industry_filter != "All":

        filtered_df = filtered_df[
            filtered_df["industry"]
            == industry_filter
        ]


    st.caption(
        f"Showing {len(filtered_df):,} "
        f"of {len(df):,} leads"
    )


    display_columns = [
        "lead_id",
        "name",
        "company",
        "industry",
        "job_title",
        "budget",
        "timeline",
        "need_level",
        "qualification_score",
        "priority",
    ]


    pipeline_display = (
        filtered_df[
            display_columns
        ]
        .copy()
        .rename(
            columns={
                "lead_id": "Lead ID",
                "name": "Name",
                "company": "Company",
                "industry": "Industry",
                "job_title": "Job Title",
                "budget": "Budget",
                "timeline": "Timeline",
                "need_level": "Need",
                "qualification_score": "Score",
                "priority": "Priority",
            }
        )
    )


    st.dataframe(
        pipeline_display,
        use_container_width=True,
        hide_index=True,
    )


    st.write("")


    if not filtered_df.empty:

        selected_id = st.selectbox(
            "Select a lead",
            filtered_df["lead_id"].tolist(),
            format_func=lambda lead_id: (
                f"{lead_id} — "
                f"{filtered_df.loc[filtered_df['lead_id'] == lead_id, 'name'].iloc[0]}"
                f" · "
                f"{filtered_df.loc[filtered_df['lead_id'] == lead_id, 'company'].iloc[0]}"
            ),
        )


        if st.button(
            "Open Lead Intelligence",
            type="primary",
        ):

            open_lead(
                selected_id
            )

            st.rerun()


# ============================================================
# INTELLIGENCE
# ============================================================

elif st.session_state.page == "Intelligence":

    st.title(
        "Lead intelligence"
    )

    st.write(
        "Understand why a lead matters and what to do next."
    )

    st.write("")


    lead_ids = df[
        "lead_id"
    ].tolist()


    default_index = 0


    if (
        st.session_state.selected_lead_id
        in lead_ids
    ):

        default_index = lead_ids.index(
            st.session_state.selected_lead_id
        )


    selected_id = st.selectbox(
        "Choose lead",
        lead_ids,
        index=default_index,
        format_func=lambda lead_id: (
            f"{lead_id} — "
            f"{df.loc[df['lead_id'] == lead_id, 'name'].iloc[0]}"
            f" · "
            f"{df.loc[df['lead_id'] == lead_id, 'company'].iloc[0]}"
        ),
    )


    st.session_state.selected_lead_id = (
        selected_id
    )


    lead = df[
        df["lead_id"]
        == selected_id
    ].iloc[0]


    score = int(
        lead["qualification_score"]
    )

    priority = lead["priority"]


    recommended_action = (
        get_recommended_action(
            lead,
            score,
            priority,
        )
    )


    with st.container(border=True):

        identity_col, score_col, priority_col = (
            st.columns([3, 1, 1])
        )


        with identity_col:

            st.markdown(
                f"## {lead['name']}"
            )

            st.write(
                f"**{lead['company']}** · "
                f"{lead['job_title']}"
            )

            st.caption(
                f"{lead['industry']} · "
                f"{lead['location']}"
            )


        with score_col:

            st.metric(
                "Qualification",
                f"{score}/100",
            )


        with priority_col:

            st.metric(
                "Priority",
                priority,
            )


    st.write("")


    st.subheader(
        "Qualification signals"
    )


    signal1, signal2, signal3, signal4 = (
        st.columns(4)
    )


    with signal1:

        st.metric(
            "Need",
            str(
                lead["need_level"]
            ),
        )


    with signal2:

        budget_value = lead["budget"]

        if pd.isna(
            budget_value
        ):

            budget_text = "Unknown"

        else:

            budget_text = (
                f"${float(budget_value):,.0f}"
            )

        st.metric(
            "Budget",
            budget_text,
        )


    with signal3:

        st.metric(
            "Timeline",
            str(
                lead["timeline"]
            ),
        )


    with signal4:

        st.metric(
            "Engagement",
            str(
                lead["email_engagement"]
            ),
        )


    st.write("")


    breakdown_col, profile_col = (
        st.columns([1.3, 1])
    )


    with breakdown_col:

        st.subheader(
            "Score breakdown"
        )

        breakdown = (
            get_score_breakdown(
                lead
            )
        )

        breakdown_df = pd.DataFrame(
            {
                "Factor": list(
                    breakdown.keys()
                ),
                "Points": list(
                    breakdown.values()
                ),
            }
        )


        fig = px.bar(
            breakdown_df,
            x="Points",
            y="Factor",
            orientation="h",
            text="Points",
        )


        fig.update_layout(
            height=370,
            margin=dict(
                l=10,
                r=10,
                t=15,
                b=10,
            ),
            plot_bgcolor="#141720",
            paper_bgcolor="#141720",
            showlegend=False,
            font=dict(
                family="Inter",
                color="#cbd5e1",
            ),
            xaxis_title="Points",
            yaxis_title=None,
        )


        fig.update_xaxes(
            gridcolor="#252a36"
        )

        fig.update_yaxes(
            gridcolor="#252a36"
        )


        fig.update_traces(
            marker_color="#8b5cf6",
            textposition="outside",
        )


        st.plotly_chart(
            fig,
            use_container_width=True,
        )


    with profile_col:

        st.subheader(
            "Lead profile"
        )


        with st.container(
            border=True
        ):

            st.write(
                f"**Company size:** "
                f"{lead['company_size']}"
            )

            st.write(
                f"**Product interest:** "
                f"{lead['product_interest']}"
            )

            st.write(
                f"**Demo requested:** "
                f"{lead['demo_requested']}"
            )

            st.write(
                f"**Pricing interest:** "
                f"{lead['pricing_interest']}"
            )

            st.write(
                f"**Previous contact:** "
                f"{lead['previous_contact']}"
            )

            st.write(
                f"**Website visits:** "
                f"{lead['website_visits']}"
            )


    st.divider()


    st.subheader(
        "Lead context"
    )


    context_col1, context_col2 = (
        st.columns(2)
    )


    with context_col1:

        with st.container(
            border=True
        ):

            st.markdown(
                "**Pain point**"
            )

            st.write(
                str(
                    lead["pain_point"]
                )
            )


    with context_col2:

        with st.container(
            border=True
        ):

            st.markdown(
                "**Notes**"
            )

            st.write(
                str(
                    lead["notes"]
                )
            )


    st.write("")


    st.subheader(
        "Recommended sales action"
    )


    with st.container(
        border=True
    ):

        st.write(
            recommended_action
        )


    st.write("")


    st.subheader(
        "AI sales intelligence"
    )


    cache_key = str(
        selected_id
    )


    if cache_key in st.session_state.ai_analyses:

        st.success(
            "AI analysis available"
        )

        st.write(
            st.session_state.ai_analyses[
                cache_key
            ]
        )


        if st.button(
            "Regenerate AI Analysis",
            key="regenerate_analysis",
        ):

            with st.spinner(
                "Generating updated sales intelligence..."
            ):

                try:

                    result = analyze_lead(
                        lead,
                        score,
                        priority,
                        recommended_action,
                    )

                    st.session_state.ai_analyses[
                        cache_key
                    ] = result

                    st.rerun()

                except Exception as error:

                    st.error(
                        f"AI analysis failed: {error}"
                    )


    else:

        st.info(
            "Generate an AI analysis to receive "
            "a concise summary, evidence-based reasons, "
            "next action, and missing information."
        )


        if st.button(
            "Generate AI Intelligence",
            type="primary",
            key="generate_analysis",
        ):

            with st.spinner(
                "Analyzing lead..."
            ):

                try:

                    result = analyze_lead(
                        lead,
                        score,
                        priority,
                        recommended_action,
                    )

                    st.session_state.ai_analyses[
                        cache_key
                    ] = result

                    st.rerun()

                except Exception as error:

                    st.error(
                        f"AI analysis failed: {error}"
                    )


# ============================================================
# ANALYTICS
# ============================================================

elif st.session_state.page == "Analytics":

    st.title(
        "Pipeline analytics"
    )

    st.write(
        "Understand the commercial profile "
        "and quality of your pipeline."
    )

    st.write("")


    budget = get_budget_analysis(
        df
    )


    metric1, metric2, metric3 = (
        st.columns(3)
    )


    with metric1:

        st.metric(
            "Average Budget",
            f"${budget['average_budget']:,.0f}",
        )


    with metric2:

        st.metric(
            "Maximum Budget",
            f"${budget['maximum_budget']:,.0f}",
        )


    with metric3:

        st.metric(
            "Pipeline Budget",
            f"${budget['total_budget']:,.0f}",
        )


    st.write("")


    industry_df = get_industry_analysis(
        df
    )


    left, right = st.columns(2)


    with left:

        st.subheader(
            "Average score by industry"
        )


        fig = px.bar(
            industry_df,
            x="industry",
            y="average_score",
            text_auto=".1f",
        )


        fig.update_layout(
            height=400,
            margin=dict(
                l=10,
                r=10,
                t=20,
                b=10,
            ),
            plot_bgcolor="#141720",
            paper_bgcolor="#141720",
            font=dict(
                family="Inter",
                color="#cbd5e1",
            ),
            xaxis_title=None,
            yaxis_title="Average Score",
        )


        fig.update_xaxes(
            gridcolor="#252a36"
        )

        fig.update_yaxes(
            gridcolor="#252a36"
        )


        fig.update_traces(
            marker_color="#6366f1"
        )


        st.plotly_chart(
            fig,
            use_container_width=True,
        )


    with right:

        st.subheader(
            "Industry performance"
        )


        industry_display = (
            industry_df.copy()
        )


        industry_display[
            "average_score"
        ] = (
            industry_display[
                "average_score"
            ].round(1)
        )


        industry_display = (
            industry_display.rename(
                columns={
                    "industry": "Industry",
                    "leads": "Leads",
                    "average_score": "Average Score",
                }
            )
        )


        st.dataframe(
            industry_display,
            use_container_width=True,
            hide_index=True,
        )


    st.write("")

    st.subheader(
        "Pipeline quality"
    )


    priority_df = (
        get_priority_distribution(
            df
        )
    )


    total = priority_df[
        "leads"
    ].sum()


    for _, row in priority_df.iterrows():

        percentage = (
            row["leads"] / total * 100
            if total
            else 0
        )


        st.write(
            f"**{row['priority']}** — "
            f"{row['leads']} leads "
            f"({percentage:.1f}%)"
        )


        st.progress(
            int(percentage)
        )


# ============================================================
# EXPORT
# ============================================================

elif st.session_state.page == "Export":

    st.title(
        "Export qualified leads"
    )

    st.write(
        "Download your scored pipeline."
    )

    st.write("")


    export_columns = [
        "lead_id",
        "name",
        "company",
        "industry",
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
        "qualification_score",
        "priority",
        "pain_point",
        "notes",
    ]


    export_df = df[
        [
            column
            for column in export_columns
            if column in df.columns
        ]
    ].copy()


    csv_data = (
        export_df
        .to_csv(index=False)
        .encode("utf-8")
    )


    metric1, metric2, metric3 = (
        st.columns(3)
    )


    with metric1:

        st.metric(
            "Leads",
            len(export_df),
        )


    with metric2:

        st.metric(
            "Hot",
            int(
                (
                    export_df["priority"]
                    == "Hot"
                ).sum()
            ),
        )


    with metric3:

        st.metric(
            "Average Score",
            f"{export_df['qualification_score'].mean():.1f}",
        )


    st.write("")


    st.download_button(
        label="Download Qualified Leads CSV",
        data=csv_data,
        file_name="leadiq_qualified_leads.csv",
        mime="text/csv",
        type="primary",
        use_container_width=True,
    )


    st.write("")


    st.subheader(
        "Export preview"
    )


    st.dataframe(
        export_df.head(20),
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

footer_left, footer_right = (
    st.columns([3, 1])
)

with footer_left:

    st.caption(
        "◈ LeadIQ · AI Sales Intelligence Platform"
    )

with footer_right:

    st.caption(
        "Python · Pandas · Hugging Face · Streamlit"
    )
