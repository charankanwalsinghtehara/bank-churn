import os
import sqlite3

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DB_PATH = os.path.join(
    BASE_DIR,
    "database",
    "banking_analytics.db"
)

REPORT_DIR = os.path.join(
    BASE_DIR,
    "reports"
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Banking Churn & Retention Analytics",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main {
        padding-top: 1rem;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    .metric-card {
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(128,128,128,0.25);
        background: rgba(128,128,128,0.06);
        min-height: 120px;
    }

    .metric-title {
        font-size: 14px;
        font-weight: 600;
        opacity: 0.75;
    }

    .metric-value {
        font-size: 28px;
        font-weight: 700;
        margin-top: 8px;
    }

    .section-title {
        font-size: 22px;
        font-weight: 700;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    .risk-critical {
        font-weight: 700;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data



def load_data():

    customer_360 = pd.read_csv(
        os.path.join(
            REPORT_DIR,
            "customer_360.csv"
        )
    )

    segment_analysis = pd.read_csv(
        os.path.join(
            REPORT_DIR,
            "segment_analysis.csv"
        )
    )

    churn_driver_summary = pd.read_csv(
        os.path.join(
            REPORT_DIR,
            "churn_driver_summary.csv"
        )
    )

    statistical_tests = pd.read_csv(
        os.path.join(
            REPORT_DIR,
            "statistical_tests.csv"
        )
    )

    retention_priority = pd.read_csv(
        os.path.join(
            REPORT_DIR,
            "retention_priority.csv"
        )
    )

    high_value_churned = pd.read_csv(
        os.path.join(
            REPORT_DIR,
            "high_value_churned_customers.csv"
        )
    )

    model_coefficients = pd.read_csv(
        os.path.join(
            REPORT_DIR,
            "churn_model_coefficients.csv"
        )
    )

    return (
        customer_360,
        segment_analysis,
        churn_driver_summary,
        statistical_tests,
        retention_priority,
        high_value_churned,
        model_coefficients
    )


(
    customer_360,
    segment_analysis,
    churn_driver_summary,
    statistical_tests,
    retention_priority,
    high_value_churned,
    model_coefficients
) = load_data()


# ============================================================
# DATA CLEANING
# ============================================================

customer_360["churned"] = pd.to_numeric(
    customer_360["churned"],
    errors="coerce"
).fillna(0)

customer_360["estimated_customer_value"] = pd.to_numeric(
    customer_360["estimated_customer_value"],
    errors="coerce"
).fillna(0)

customer_360["retention_risk_score"] = pd.to_numeric(
    customer_360["retention_risk_score"],
    errors="coerce"
).fillna(0)

customer_360["retention_priority_score"] = pd.to_numeric(
    customer_360["retention_priority_score"],
    errors="coerce"
).fillna(0)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def format_currency(value):
    return f"₹{value:,.0f}"


def format_number(value):
    return f"{value:,.0f}"


def format_percent(value):
    return f"{value:.2f}%"


def metric_card(title, value):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🏦 Banking Analytics")

st.sidebar.caption(
    "Customer Churn & Retention Intelligence"
)

st.sidebar.divider()

st.sidebar.subheader("Dashboard Filters")


# ------------------------------------------------------------
# SEGMENT
# ------------------------------------------------------------

segments = sorted(
    customer_360["segment"]
    .dropna()
    .astype(str)
    .unique()
)

selected_segments = st.sidebar.multiselect(
    "Customer Segment",
    segments,
    default=segments
)


# ------------------------------------------------------------
# CITY
# ------------------------------------------------------------

cities = sorted(
    customer_360["city"]
    .dropna()
    .astype(str)
    .unique()
)

selected_cities = st.sidebar.multiselect(
    "City",
    cities,
    default=[]
)


# ------------------------------------------------------------
# OCCUPATION
# ------------------------------------------------------------

occupations = sorted(
    customer_360["occupation"]
    .dropna()
    .astype(str)
    .unique()
)

selected_occupations = st.sidebar.multiselect(
    "Occupation",
    occupations,
    default=[]
)


# ------------------------------------------------------------
# RISK BAND
# ------------------------------------------------------------

risk_bands = [
    "Low Risk",
    "Medium Risk",
    "High Risk",
    "Critical Risk"
]

selected_risk = st.sidebar.multiselect(
    "Risk Band",
    risk_bands,
    default=risk_bands
)


# ------------------------------------------------------------
# CUSTOMER STATUS
# ------------------------------------------------------------

customer_status = st.sidebar.radio(
    "Customer Status",
    [
        "All Customers",
        "Churned",
        "Retained"
    ]
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_data = customer_360.copy()

if selected_segments:

    filtered_data = filtered_data[
        filtered_data["segment"].isin(
            selected_segments
        )
    ]

if selected_cities:

    filtered_data = filtered_data[
        filtered_data["city"].isin(
            selected_cities
        )
    ]

if selected_occupations:

    filtered_data = filtered_data[
        filtered_data["occupation"].isin(
            selected_occupations
        )
    ]

if selected_risk:

    filtered_data = filtered_data[
        filtered_data["risk_band"].isin(
            selected_risk
        )
    ]

if customer_status == "Churned":

    filtered_data = filtered_data[
        filtered_data["churned"] == 1
    ]

elif customer_status == "Retained":

    filtered_data = filtered_data[
        filtered_data["churned"] == 0
    ]


# ============================================================
# HEADER
# ============================================================

st.title(
    "🏦 Banking Customer Churn & Retention Analytics"
)

st.markdown(
    """
    **Executive dashboard for identifying churn drivers,
    customer value, retention risk, and high-priority
    customers requiring intervention.**
    """
)

st.divider()


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_customers = len(filtered_data)

churned_customers = int(
    filtered_data["churned"].sum()
)

retained_customers = (
    total_customers - churned_customers
)

churn_rate = (
    churned_customers / total_customers * 100
    if total_customers > 0
    else 0
)

avg_satisfaction = (
    filtered_data["satisfaction_score"].mean()
    if total_customers > 0
    else 0
)

avg_engagement = (
    filtered_data["digital_engagement"].mean()
    if total_customers > 0
    else 0
)

total_balance = (
    filtered_data["total_account_balance"].sum()
)

total_transaction_value = (
    filtered_data["total_transaction_amount"].sum()
)

high_risk_customers = len(
    filtered_data[
        filtered_data["risk_band"].isin(
            ["High Risk", "Critical Risk"]
        )
    ]
)

high_value_churned_count = len(
    filtered_data[
        (
            filtered_data["churned"] == 1
        )
        &
        (
            filtered_data["value_segment"].isin(
                ["High Value", "Very High Value"]
            )
        )
    ]
)


# ============================================================
# KPI ROW
# ============================================================

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    metric_card(
        "Total Customers",
        format_number(total_customers)
    )

with kpi2:
    metric_card(
        "Churn Rate",
        format_percent(churn_rate)
    )

with kpi3:
    metric_card(
        "High/Critical Risk",
        format_number(high_risk_customers)
    )

with kpi4:
    metric_card(
        "High-Value Churned",
        format_number(high_value_churned_count)
    )


st.write("")


kpi5, kpi6, kpi7, kpi8 = st.columns(4)

with kpi5:
    metric_card(
        "Retained Customers",
        format_number(retained_customers)
    )

with kpi6:
    metric_card(
        "Avg Satisfaction",
        f"{avg_satisfaction:.2f}/5"
    )

with kpi7:
    metric_card(
        "Avg Digital Engagement",
        f"{avg_engagement:.1f}"
    )

with kpi8:
    metric_card(
        "Account Balance",
        format_currency(total_balance)
    )


# ============================================================
# EXECUTIVE OVERVIEW
# ============================================================

st.markdown(
    '<div class="section-title">Executive Overview</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)


# ------------------------------------------------------------
# CHURN BY SEGMENT
# ------------------------------------------------------------

with col1:

    segment_chart = (
        filtered_data
        .groupby("segment")["churned"]
        .mean()
        .reset_index()
    )

    segment_chart["churned"] *= 100

    fig = px.bar(
        segment_chart,
        x="segment",
        y="churned",
        title="Churn Rate by Customer Segment",
        labels={
            "segment": "Segment",
            "churned": "Churn Rate (%)"
        },
        text_auto=".1f"
    )

    fig.update_layout(
        height=420,
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ------------------------------------------------------------
# RISK DISTRIBUTION
# ------------------------------------------------------------

with col2:

    risk_chart = (
        filtered_data
        .groupby("risk_band", observed=True)
        .size()
        .reset_index(
            name="customers"
        )
    )

    risk_chart["risk_band"] = pd.Categorical(
        risk_chart["risk_band"],
        categories=risk_bands,
        ordered=True
    )

    risk_chart = risk_chart.sort_values(
        "risk_band"
    )

    fig = px.bar(
        risk_chart,
        x="risk_band",
        y="customers",
        title="Customer Retention Risk Distribution",
        labels={
            "risk_band": "Risk Band",
            "customers": "Customers"
        },
        text_auto=True
    )

    fig.update_layout(
        height=420,
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# CHURN DRIVERS
# ============================================================

st.markdown(
    '<div class="section-title">Churn Drivers</div>',
    unsafe_allow_html=True
)

driver_col1, driver_col2 = st.columns(2)


# ------------------------------------------------------------
# SATISFACTION
# ------------------------------------------------------------

with driver_col1:

    satisfaction_chart = (
        filtered_data
        .groupby(
            "satisfaction_group",
            observed=True
        )["churned"]
        .mean()
        .reset_index()
    )

    satisfaction_chart["churned"] *= 100

    fig = px.bar(
        satisfaction_chart,
        x="satisfaction_group",
        y="churned",
        title="Churn vs Customer Satisfaction",
        labels={
            "satisfaction_group": "Satisfaction",
            "churned": "Churn Rate (%)"
        },
        text_auto=".1f"
    )

    fig.update_layout(
        height=420
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ------------------------------------------------------------
# DIGITAL ENGAGEMENT
# ------------------------------------------------------------

with driver_col2:

    engagement_chart = (
        filtered_data
        .groupby(
            "engagement_group",
            observed=True
        )["churned"]
        .mean()
        .reset_index()
    )

    engagement_chart["churned"] *= 100

    fig = px.bar(
        engagement_chart,
        x="engagement_group",
        y="churned",
        title="Churn vs Digital Engagement",
        labels={
            "engagement_group": "Digital Engagement",
            "churned": "Churn Rate (%)"
        },
        text_auto=".1f"
    )

    fig.update_layout(
        height=420
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# CUSTOMER BEHAVIOR
# ============================================================

st.markdown(
    '<div class="section-title">Customer Behavior</div>',
    unsafe_allow_html=True
)

behavior1, behavior2 = st.columns(2)


# ------------------------------------------------------------
# PRODUCTS
# ------------------------------------------------------------

with behavior1:

    product_chart = (
        filtered_data
        .groupby(
            "product_group",
            observed=True
        )["churned"]
        .mean()
        .reset_index()
    )

    product_chart["churned"] *= 100

    fig = px.bar(
        product_chart,
        x="product_group",
        y="churned",
        title="Churn vs Number of Products",
        labels={
            "product_group": "Products",
            "churned": "Churn Rate (%)"
        },
        text_auto=".1f"
    )

    fig.update_layout(
        height=420
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ------------------------------------------------------------
# TENURE
# ------------------------------------------------------------

with behavior2:

    tenure_chart = (
        filtered_data
        .groupby(
            "tenure_group",
            observed=True
        )["churned"]
        .mean()
        .reset_index()
    )

    tenure_chart["churned"] *= 100

    fig = px.bar(
        tenure_chart,
        x="tenure_group",
        y="churned",
        title="Churn vs Customer Tenure",
        labels={
            "tenure_group": "Tenure",
            "churned": "Churn Rate (%)"
        },
        text_auto=".1f"
    )

    fig.update_layout(
        height=420
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# CUSTOMER VALUE
# ============================================================

st.markdown(
    '<div class="section-title">Customer Value & Retention Opportunity</div>',
    unsafe_allow_html=True
)

value1, value2 = st.columns(2)


# ------------------------------------------------------------
# VALUE SEGMENT
# ------------------------------------------------------------

with value1:

    value_chart = (
        filtered_data
        .groupby(
            "value_segment",
            observed=True
        )
        .agg(
            customers=("customer_id", "count"),
            churn_rate=("churned", "mean"),
            customer_value=(
                "estimated_customer_value",
                "mean"
            )
        )
        .reset_index()
    )

    value_chart["churn_rate"] *= 100

    fig = px.bar(
        value_chart,
        x="value_segment",
        y="customer_value",
        title="Average Customer Value by Segment",
        labels={
            "value_segment": "Value Segment",
            "customer_value": "Average Customer Value"
        },
        text_auto=".2s"
    )

    fig.update_layout(
        height=420
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ------------------------------------------------------------
# CHURN VS VALUE
# ------------------------------------------------------------

with value2:

    value_churn_chart = (
        filtered_data
        .groupby(
            "value_segment",
            observed=True
        )["churned"]
        .mean()
        .reset_index()
    )

    value_churn_chart["churned"] *= 100

    fig = px.bar(
        value_churn_chart,
        x="value_segment",
        y="churned",
        title="Churn Rate by Customer Value",
        labels={
            "value_segment": "Value Segment",
            "churned": "Churn Rate (%)"
        },
        text_auto=".1f"
    )

    fig.update_layout(
        height=420
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# CITY ANALYSIS
# ============================================================

st.markdown(
    '<div class="section-title">Geographic Churn Analysis</div>',
    unsafe_allow_html=True
)

city_chart = (
    filtered_data
    .groupby("city")
    .agg(
        customers=("customer_id", "count"),
        churn_rate=("churned", "mean")
    )
    .reset_index()
)

city_chart["churn_rate"] *= 100

city_chart = city_chart[
    city_chart["customers"] >= 20
]

city_chart = city_chart.sort_values(
    "churn_rate",
    ascending=False
).head(15)

fig = px.bar(
    city_chart,
    x="churn_rate",
    y="city",
    orientation="h",
    title="Highest-Churn Cities",
    labels={
        "churn_rate": "Churn Rate (%)",
        "city": "City"
    },
    text_auto=".1f"
)

fig.update_layout(
    height=500
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# COMPLAINT ANALYSIS
# ============================================================

st.markdown(
    '<div class="section-title">Customer Experience Analysis</div>',
    unsafe_allow_html=True
)

complaint1, complaint2 = st.columns(2)


with complaint1:

    complaint_chart = (
        filtered_data
        .groupby(
            "complaint_group",
            observed=True
        )["churned"]
        .mean()
        .reset_index()
    )

    complaint_chart["churned"] *= 100

    fig = px.bar(
        complaint_chart,
        x="complaint_group",
        y="churned",
        title="Churn Rate by Complaint Frequency",
        labels={
            "complaint_group": "Complaint Frequency",
            "churned": "Churn Rate (%)"
        },
        text_auto=".1f"
    )

    fig.update_layout(
        height=420
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


with complaint2:

    channel_chart = (
        filtered_data
        .groupby("primary_channel")["churned"]
        .mean()
        .reset_index()
    )

    channel_chart["churned"] *= 100

    fig = px.bar(
        channel_chart,
        x="primary_channel",
        y="churned",
        title="Churn Rate by Primary Banking Channel",
        labels={
            "primary_channel": "Channel",
            "churned": "Churn Rate (%)"
        },
        text_auto=".1f"
    )

    fig.update_layout(
        height=420
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# CHURN DRIVER TABLE
# ============================================================

st.markdown(
    '<div class="section-title">Statistically Significant Churn Drivers</div>',
    unsafe_allow_html=True
)

significant_drivers = statistical_tests[
    statistical_tests["significant_5pct"] == True
].copy()

significant_drivers = significant_drivers.sort_values(
    "p_value"
)

if len(significant_drivers) > 0:

    display_drivers = significant_drivers[
        [
            "feature",
            "test",
            "statistic",
            "p_value"
        ]
    ].copy()

    display_drivers["p_value"] = (
        display_drivers["p_value"]
        .round(6)
    )

    st.dataframe(
        display_drivers.head(15),
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "No statistically significant drivers "
        "were identified at the 5% level."
    )


# ============================================================
# MODEL COEFFICIENTS
# ============================================================

st.markdown(
    '<div class="section-title">Churn Driver Importance</div>',
    unsafe_allow_html=True
)

coef_display = model_coefficients.copy()

coef_display = coef_display.sort_values(
    "absolute_importance",
    ascending=False
).head(12)

fig = px.bar(
    coef_display.sort_values(
        "coefficient"
    ),
    x="coefficient",
    y="feature",
    orientation="h",
    title="Interpretable Churn Driver Coefficients",
    labels={
        "coefficient": "Model Coefficient",
        "feature": "Feature"
    }
)

fig.update_layout(
    height=500
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# RETENTION PRIORITY
# ============================================================

st.markdown(
    '<div class="section-title">Retention Priority Customers</div>',
    unsafe_allow_html=True
)

priority_columns = [
    "customer_id",
    "customer_code",
    "first_name",
    "last_name",
    "city",
    "segment",
    "satisfaction_score",
    "digital_engagement",
    "complaint_count",
    "estimated_customer_value",
    "retention_risk_score",
    "risk_band",
    "retention_priority_score",
    "churned"
]

priority_display = (
    filtered_data[
        [
            column
            for column in priority_columns
            if column in filtered_data.columns
        ]
    ]
    .sort_values(
        "retention_priority_score",
        ascending=False
    )
    .head(50)
    .copy()
)

priority_display["estimated_customer_value"] = (
    priority_display[
        "estimated_customer_value"
    ].round(0)
)

priority_display["retention_priority_score"] = (
    priority_display[
        "retention_priority_score"
    ].round(2)
)

st.dataframe(
    priority_display,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# CUSTOMER 360 SEARCH
# ============================================================

st.markdown(
    '<div class="section-title">Customer 360 Lookup</div>',
    unsafe_allow_html=True
)

search_term = st.text_input(
    "Search by Customer ID, Customer Code, First Name or Last Name"
)

if search_term:

    search_term = search_term.lower().strip()

    search_results = customer_360[
        customer_360[
            [
                "customer_id",
                "customer_code",
                "first_name",
                "last_name"
            ]
        ]
        .astype(str)
        .apply(
            lambda row:
            row.str.lower()
            .str.contains(
                search_term,
                regex=False
            )
            .any(),
            axis=1
        )
    ]

    if len(search_results) == 0:

        st.warning(
            "No matching customer found."
        )

    else:

        for _, customer in search_results.head(10).iterrows():

            st.markdown(
                f"### {customer['first_name']} "
                f"{customer['last_name']}"
            )

            c1, c2, c3, c4 = st.columns(4)

            with c1:
                st.metric(
                    "Customer ID",
                    customer["customer_id"]
                )

            with c2:
                st.metric(
                    "Segment",
                    customer["segment"]
                )

            with c3:
                st.metric(
                    "Churn Status",
                    "Churned"
                    if customer["churned"] == 1
                    else "Retained"
                )

            with c4:
                st.metric(
                    "Risk",
                    customer["risk_band"]
                )

            c5, c6, c7, c8 = st.columns(4)

            with c5:
                st.metric(
                    "Satisfaction",
                    f"{customer['satisfaction_score']:.1f}/5"
                )

            with c6:
                st.metric(
                    "Digital Engagement",
                    f"{customer['digital_engagement']:.1f}"
                )

            with c7:
                st.metric(
                    "Customer Value",
                    format_currency(
                        customer[
                            "estimated_customer_value"
                        ]
                    )
                )

            with c8:
                st.metric(
                    "Risk Score",
                    f"{customer['retention_risk_score']:.0f}"
                )

            st.divider()


# ============================================================
# BUSINESS RECOMMENDATIONS
# ============================================================

st.markdown(
    '<div class="section-title">Management Recommendations</div>',
    unsafe_allow_html=True
)

recommendation_col1, recommendation_col2 = st.columns(2)


with recommendation_col1:

    st.markdown(
        """
        **1. Prioritize high-value churners**

        Focus retention campaigns on customers who combine
        high customer value with high or critical retention risk.

        **2. Improve customer satisfaction**

        Customers with low satisfaction should receive
        proactive service recovery and relationship-management
        interventions.

        **3. Increase digital engagement**

        Low-engagement customers can be targeted with digital
        onboarding, personalized offers and mobile-banking
        engagement campaigns.
        """
    )


with recommendation_col2:

    st.markdown(
        """
        **4. Reduce complaint-driven churn**

        Customers with repeated complaints should receive
        faster resolution and proactive follow-up.

        **5. Increase product penetration**

        Customers with fewer products may have weaker
        relationships with the bank and should be evaluated
        for relevant cross-sell opportunities.

        **6. Build a retention early-warning system**

        Use the retention risk score to identify customers
        before churn occurs rather than reacting after churn.
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Banking Customer Churn & Retention Analytics | "
    "Python + SQL + SQLite + Streamlit + Plotly"
)