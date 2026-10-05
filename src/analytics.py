import os
import sqlite3
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from scipy.stats import mannwhitneyu, chi2_contingency
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

warnings.filterwarnings("ignore")


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(
    BASE_DIR,
    "database",
    "banking_analytics.db"
)

REPORT_DIR = os.path.join(
    BASE_DIR,
    "reports"
)

CHART_DIR = os.path.join(
    REPORT_DIR,
    "charts"
)

os.makedirs(REPORT_DIR, exist_ok=True)
os.makedirs(CHART_DIR, exist_ok=True)


# ============================================================
# DATABASE CONNECTION
# ============================================================

print("=" * 70)
print("BANKING CUSTOMER CHURN ANALYTICS")
print("=" * 70)

print("\nConnecting to database...")

conn = sqlite3.connect(DB_PATH)

print("Database connected successfully.")


# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading datasets...")

customers = pd.read_sql_query(
    "SELECT * FROM customers",
    conn
)

accounts = pd.read_sql_query(
    "SELECT * FROM accounts",
    conn
)

transactions = pd.read_sql_query(
    "SELECT * FROM transactions",
    conn
)

loans = pd.read_sql_query(
    "SELECT * FROM loans",
    conn
)

credit_cards = pd.read_sql_query(
    "SELECT * FROM credit_cards",
    conn
)

interactions = pd.read_sql_query(
    "SELECT * FROM interactions",
    conn
)

conn.close()

print(f"Customers:     {len(customers):,}")
print(f"Accounts:      {len(accounts):,}")
print(f"Transactions:  {len(transactions):,}")
print(f"Loans:         {len(loans):,}")
print(f"Credit Cards:  {len(credit_cards):,}")
print(f"Interactions:  {len(interactions):,}")


# ============================================================
# DATA PREPARATION
# ============================================================

print("\nPreparing analytical dataset...")


# ------------------------------------------------------------
# DATE CONVERSION
# ------------------------------------------------------------

customers["customer_join_date"] = pd.to_datetime(
    customers["customer_join_date"],
    errors="coerce"
)

transactions["transaction_date"] = pd.to_datetime(
    transactions["transaction_date"],
    errors="coerce"
)

loans["start_date"] = pd.to_datetime(
    loans["start_date"],
    errors="coerce"
)

credit_cards["issue_date"] = pd.to_datetime(
    credit_cards["issue_date"],
    errors="coerce"
)

interactions["interaction_date"] = pd.to_datetime(
    interactions["interaction_date"],
    errors="coerce"
)


# ============================================================
# ACCOUNT AGGREGATION
# ============================================================

account_summary = (
    accounts
    .groupby("customer_id")
    .agg(
        account_count=("account_id", "count"),
        total_account_balance=("balance", "sum"),
        avg_account_balance=("balance", "mean"),
        active_account_count=(
            "status",
            lambda x: (x == "Active").sum()
        )
    )
    .reset_index()
)


# ============================================================
# TRANSACTION AGGREGATION
# ============================================================

transaction_summary = (
    transactions
    .groupby("customer_id")
    .agg(
        transaction_count=("transaction_id", "count"),
        total_transaction_amount=("amount", "sum"),
        avg_transaction_amount=("amount", "mean"),
        median_transaction_amount=("amount", "median"),
        transaction_std=("amount", "std"),
        active_transaction_days=(
            "transaction_date",
            lambda x: x.dt.date.nunique()
        )
    )
    .reset_index()
)

transaction_summary["transaction_std"] = (
    transaction_summary["transaction_std"]
    .fillna(0)
)


# ============================================================
# TRANSACTION TYPE SUMMARY
# ============================================================

transaction_type = pd.crosstab(
    transactions["customer_id"],
    transactions["transaction_type"]
)

transaction_type = transaction_type.reset_index()

transaction_type.columns = [
    "customer_id"
    if col == "customer_id"
    else f"transaction_type_{str(col).lower().replace(' ', '_')}"
    for col in transaction_type.columns
]


# ============================================================
# LOAN AGGREGATION
# ============================================================

loan_summary = (
    loans
    .groupby("customer_id")
    .agg(
        loan_count=("loan_id", "count"),
        total_loan_amount=("loan_amount", "sum"),
        avg_loan_amount=("loan_amount", "mean"),
        avg_interest_rate=("interest_rate", "mean"),
        active_loan_count=(
            "status",
            lambda x: (x == "Active").sum()
        )
    )
    .reset_index()
)


# ============================================================
# CREDIT CARD AGGREGATION
# ============================================================

credit_card_summary = (
    credit_cards
    .groupby("customer_id")
    .agg(
        credit_card_count=("card_id", "count"),
        total_credit_limit=("credit_limit", "sum"),
        total_card_balance=("current_balance", "sum"),
        avg_utilization_ratio=("utilization_ratio", "mean"),
        max_utilization_ratio=("utilization_ratio", "max")
    )
    .reset_index()
)


# ============================================================
# INTERACTION AGGREGATION
# ============================================================

interaction_summary = (
    interactions
    .groupby("customer_id")
    .agg(
        interaction_count=("interaction_id", "count"),
        avg_resolution_days=("resolution_days", "mean"),
        complaint_interactions=(
            "interaction_type",
            lambda x: (x == "Complaint").sum()
        ),
        negative_interactions=(
            "sentiment",
            lambda x: (x == "Negative").sum()
        ),
        positive_interactions=(
            "sentiment",
            lambda x: (x == "Positive").sum()
        )
    )
    .reset_index()
)


# ============================================================
# CUSTOMER 360 DATASET
# ============================================================

customer_360 = customers.copy()

customer_360 = customer_360.merge(
    account_summary,
    on="customer_id",
    how="left"
)

customer_360 = customer_360.merge(
    transaction_summary,
    on="customer_id",
    how="left"
)

customer_360 = customer_360.merge(
    transaction_type,
    on="customer_id",
    how="left"
)

customer_360 = customer_360.merge(
    loan_summary,
    on="customer_id",
    how="left"
)

customer_360 = customer_360.merge(
    credit_card_summary,
    on="customer_id",
    how="left"
)

customer_360 = customer_360.merge(
    interaction_summary,
    on="customer_id",
    how="left"
)


# ============================================================
# FILL MISSING VALUES
# ============================================================

numeric_columns = customer_360.select_dtypes(
    include=np.number
).columns

customer_360[numeric_columns] = (
    customer_360[numeric_columns]
    .fillna(0)
)


# ============================================================
# DERIVED BUSINESS FEATURES
# ============================================================

customer_360["age_group"] = pd.cut(
    customer_360["age"],
    bins=[0, 25, 35, 45, 55, 65, 100],
    labels=[
        "18-25",
        "26-35",
        "36-45",
        "46-55",
        "56-65",
        "66+"
    ]
)

customer_360["tenure_group"] = pd.cut(
    customer_360["tenure_years"],
    bins=[-1, 1, 3, 5, 10, 100],
    labels=[
        "0-1 Years",
        "2-3 Years",
        "4-5 Years",
        "6-10 Years",
        "10+ Years"
    ]
)

customer_360["product_group"] = pd.cut(
    customer_360["product_count"],
    bins=[-1, 1, 2, 3, 4, 100],
    labels=[
        "1 Product",
        "2 Products",
        "3 Products",
        "4 Products",
        "5+ Products"
    ]
)

customer_360["credit_score_group"] = pd.cut(
    customer_360["credit_score"],
    bins=[0, 580, 670, 740, 800, 900],
    labels=[
        "Poor",
        "Fair",
        "Good",
        "Very Good",
        "Excellent"
    ]
)

customer_360["satisfaction_group"] = pd.cut(
    customer_360["satisfaction_score"],
    bins=[0, 2, 3, 4, 5],
    labels=[
        "Low",
        "Below Average",
        "Good",
        "Excellent"
    ],
    include_lowest=True
)

customer_360["engagement_group"] = pd.cut(
    customer_360["digital_engagement"],
    bins=[-1, 20, 40, 60, 80, 100],
    labels=[
        "Very Low",
        "Low",
        "Medium",
        "High",
        "Very High"
    ]
)

customer_360["complaint_group"] = pd.cut(
    customer_360["complaint_count"],
    bins=[-1, 0, 1, 3, 5, 100],
    labels=[
        "No Complaints",
        "1 Complaint",
        "2-3 Complaints",
        "4-5 Complaints",
        "6+ Complaints"
    ]
)


# ============================================================
# CUSTOMER VALUE
# ============================================================

customer_360["estimated_customer_value"] = (
    customer_360["total_account_balance"]
    + customer_360["total_transaction_amount"] * 0.02
    + customer_360["total_loan_amount"] * 0.01
    + customer_360["total_credit_limit"] * 0.01
)


customer_360["value_segment"] = pd.qcut(
    customer_360["estimated_customer_value"].rank(
        method="first"
    ),
    q=4,
    labels=[
        "Low Value",
        "Medium Value",
        "High Value",
        "Very High Value"
    ]
)


# ============================================================
# RETENTION RISK SCORE
# ============================================================

customer_360["retention_risk_score"] = 0


# Low satisfaction
customer_360["retention_risk_score"] += np.where(
    customer_360["satisfaction_score"] <= 2,
    25,
    np.where(
        customer_360["satisfaction_score"] == 3,
        10,
        0
    )
)

# Low digital engagement
customer_360["retention_risk_score"] += np.where(
    customer_360["digital_engagement"] < 30,
    20,
    np.where(
        customer_360["digital_engagement"] < 50,
        10,
        0
    )
)

# Complaints
customer_360["retention_risk_score"] += np.where(
    customer_360["complaint_count"] >= 5,
    20,
    np.where(
        customer_360["complaint_count"] >= 2,
        10,
        0
    )
)

# Low credit score
customer_360["retention_risk_score"] += np.where(
    customer_360["credit_score"] < 600,
    15,
    np.where(
        customer_360["credit_score"] < 680,
        5,
        0
    )
)

# Low transaction activity
customer_360["retention_risk_score"] += np.where(
    customer_360["transaction_count"] < 10,
    10,
    0
)

# High card utilization
customer_360["retention_risk_score"] += np.where(
    customer_360["avg_utilization_ratio"] > 0.80,
    10,
    np.where(
        customer_360["avg_utilization_ratio"] > 0.60,
        5,
        0
    )
)


customer_360["risk_band"] = pd.cut(
    customer_360["retention_risk_score"],
    bins=[-1, 20, 40, 60, 100],
    labels=[
        "Low Risk",
        "Medium Risk",
        "High Risk",
        "Critical Risk"
    ]
)


# ============================================================
# RETENTION PRIORITY SCORE
# ============================================================

customer_360["retention_priority_score"] = (
    customer_360["retention_risk_score"]
    * (
        1
        + customer_360["estimated_customer_value"]
        / max(
            customer_360["estimated_customer_value"].median(),
            1
        )
    )
)


# ============================================================
# SAVE CUSTOMER 360
# ============================================================

customer_360.to_csv(
    os.path.join(
        REPORT_DIR,
        "customer_360.csv"
    ),
    index=False
)

print("\nCustomer 360 created.")


# ============================================================
# EXECUTIVE KPI SUMMARY
# ============================================================

total_customers = len(customer_360)

churned_customers = int(
    customer_360["churned"].sum()
)

churn_rate = (
    churned_customers
    / total_customers
    * 100
)

avg_satisfaction = (
    customer_360["satisfaction_score"].mean()
)

avg_engagement = (
    customer_360["digital_engagement"].mean()
)

total_balance = (
    customer_360["total_account_balance"].sum()
)

total_transaction_value = (
    customer_360["total_transaction_amount"].sum()
)

total_loan_exposure = (
    customer_360["total_loan_amount"].sum()
)

total_credit_limit = (
    customer_360["total_credit_limit"].sum()
)


kpi_summary = pd.DataFrame({
    "metric": [
        "Total Customers",
        "Churned Customers",
        "Churn Rate %",
        "Average Satisfaction",
        "Average Digital Engagement",
        "Total Account Balance",
        "Total Transaction Value",
        "Total Loan Exposure",
        "Total Credit Limit"
    ],
    "value": [
        total_customers,
        churned_customers,
        churn_rate,
        avg_satisfaction,
        avg_engagement,
        total_balance,
        total_transaction_value,
        total_loan_exposure,
        total_credit_limit
    ]
})

kpi_summary.to_csv(
    os.path.join(
        REPORT_DIR,
        "kpi_summary.csv"
    ),
    index=False
)


# ============================================================
# SEGMENT ANALYSIS
# ============================================================

segment_analysis = (
    customer_360
    .groupby("segment", observed=True)
    .agg(
        customers=("customer_id", "count"),
        churned_customers=("churned", "sum"),
        churn_rate=("churned", "mean"),
        avg_satisfaction=("satisfaction_score", "mean"),
        avg_engagement=("digital_engagement", "mean"),
        avg_income=("annual_income", "mean"),
        avg_customer_value=("estimated_customer_value", "mean")
    )
    .reset_index()
)

segment_analysis["churn_rate"] *= 100

segment_analysis.to_csv(
    os.path.join(
        REPORT_DIR,
        "segment_analysis.csv"
    ),
    index=False
)


# ============================================================
# CHURN DRIVER SUMMARIES
# ============================================================

driver_columns = [
    "age_group",
    "tenure_group",
    "product_group",
    "credit_score_group",
    "satisfaction_group",
    "engagement_group",
    "complaint_group",
    "value_segment",
    "risk_band"
]


driver_results = []

for column in driver_columns:

    temp = (
        customer_360
        .groupby(column, observed=True)
        .agg(
            customers=("customer_id", "count"),
            churned=("churned", "sum"),
            churn_rate=("churned", "mean")
        )
        .reset_index()
    )

    temp["churn_rate"] *= 100

    for _, row in temp.iterrows():

        driver_results.append({
            "driver": column,
            "category": str(row[column]),
            "customers": row["customers"],
            "churned": row["churned"],
            "churn_rate": row["churn_rate"]
        })


churn_driver_summary = pd.DataFrame(
    driver_results
)

churn_driver_summary.to_csv(
    os.path.join(
        REPORT_DIR,
        "churn_driver_summary.csv"
    ),
    index=False
)


# ============================================================
# STATISTICAL TESTING
# ============================================================

print("\nRunning statistical tests...")

statistical_results = []


# ------------------------------------------------------------
# NUMERIC VARIABLES
# ------------------------------------------------------------

numeric_test_columns = [
    "age",
    "annual_income",
    "tenure_years",
    "product_count",
    "credit_score",
    "digital_engagement",
    "complaint_count",
    "satisfaction_score",
    "account_count",
    "total_account_balance",
    "transaction_count",
    "total_transaction_amount",
    "avg_transaction_amount",
    "loan_count",
    "total_loan_amount",
    "credit_card_count",
    "avg_utilization_ratio",
    "interaction_count",
    "estimated_customer_value"
]


for column in numeric_test_columns:

    if column not in customer_360.columns:
        continue

    churn_group = customer_360.loc[
        customer_360["churned"] == 1,
        column
    ].dropna()

    retained_group = customer_360.loc[
        customer_360["churned"] == 0,
        column
    ].dropna()

    if len(churn_group) < 2 or len(retained_group) < 2:
        continue

    statistic, p_value = mannwhitneyu(
        churn_group,
        retained_group,
        alternative="two-sided"
    )

    churn_mean = churn_group.mean()
    retained_mean = retained_group.mean()

    statistical_results.append({
        "feature": column,
        "test": "Mann-Whitney U",
        "churn_mean": churn_mean,
        "retained_mean": retained_mean,
        "difference": churn_mean - retained_mean,
        "statistic": statistic,
        "p_value": p_value,
        "significant_5pct": p_value < 0.05
    })


# ============================================================
# CATEGORICAL CHI-SQUARE TESTS
# ============================================================

categorical_test_columns = [
    "segment",
    "city",
    "occupation",
    "age_group",
    "tenure_group",
    "product_group",
    "credit_score_group",
    "satisfaction_group",
    "engagement_group",
    "complaint_group",
    "primary_channel",
    "value_segment"
]


for column in categorical_test_columns:

    if column not in customer_360.columns:
        continue

    contingency = pd.crosstab(
        customer_360[column],
        customer_360["churned"]
    )

    if contingency.shape[0] < 2:
        continue

    chi2, p_value, dof, expected = chi2_contingency(
        contingency
    )

    statistical_results.append({
        "feature": column,
        "test": "Chi-Square",
        "churn_mean": np.nan,
        "retained_mean": np.nan,
        "difference": np.nan,
        "statistic": chi2,
        "p_value": p_value,
        "significant_5pct": p_value < 0.05
    })


statistical_tests = pd.DataFrame(
    statistical_results
)

statistical_tests = statistical_tests.sort_values(
    by="p_value"
)

statistical_tests.to_csv(
    os.path.join(
        REPORT_DIR,
        "statistical_tests.csv"
    ),
    index=False
)


# ============================================================
# NUMERIC CORRELATIONS
# ============================================================

correlation_columns = [
    "age",
    "annual_income",
    "tenure_years",
    "product_count",
    "credit_score",
    "digital_engagement",
    "complaint_count",
    "satisfaction_score",
    "account_count",
    "total_account_balance",
    "transaction_count",
    "total_transaction_amount",
    "loan_count",
    "total_loan_amount",
    "credit_card_count",
    "avg_utilization_ratio",
    "interaction_count",
    "estimated_customer_value",
    "retention_risk_score",
    "churned"
]

correlation_data = customer_360[
    [
        column
        for column in correlation_columns
        if column in customer_360.columns
    ]
].corr()

correlation_data.to_csv(
    os.path.join(
        REPORT_DIR,
        "numeric_correlations.csv"
    )
)


# ============================================================
# LOGISTIC REGRESSION
# ============================================================

print("\nRunning interpretable churn model...")

model_features = [
    "age",
    "annual_income",
    "tenure_years",
    "product_count",
    "credit_score",
    "digital_engagement",
    "complaint_count",
    "satisfaction_score",
    "account_count",
    "total_account_balance",
    "transaction_count",
    "total_transaction_amount",
    "loan_count",
    "total_loan_amount",
    "credit_card_count",
    "avg_utilization_ratio",
    "interaction_count",
    "estimated_customer_value"
]

model_data = customer_360[
    model_features + ["churned"]
].copy()

model_data = model_data.replace(
    [np.inf, -np.inf],
    np.nan
)

model_data = model_data.fillna(0)

X = model_data[model_features]
y = model_data["churned"]

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)

model = LogisticRegression(
    max_iter=2000,
    random_state=42
)

model.fit(
    X_scaled,
    y
)

coefficients = pd.DataFrame({
    "feature": model_features,
    "coefficient": model.coef_[0]
})

coefficients["absolute_importance"] = (
    coefficients["coefficient"].abs()
)

coefficients["direction"] = np.where(
    coefficients["coefficient"] > 0,
    "Higher value associated with churn",
    "Higher value associated with retention"
)

coefficients = coefficients.sort_values(
    by="absolute_importance",
    ascending=False
)

coefficients.to_csv(
    os.path.join(
        REPORT_DIR,
        "churn_model_coefficients.csv"
    ),
    index=False
)


# ============================================================
# RETENTION PRIORITY CUSTOMERS
# ============================================================

retention_priority = (
    customer_360[
        [
            "customer_id",
            "customer_code",
            "first_name",
            "last_name",
            "city",
            "segment",
            "age",
            "tenure_years",
            "product_count",
            "credit_score",
            "digital_engagement",
            "complaint_count",
            "satisfaction_score",
            "transaction_count",
            "total_account_balance",
            "total_loan_amount",
            "avg_utilization_ratio",
            "estimated_customer_value",
            "retention_risk_score",
            "risk_band",
            "retention_priority_score",
            "churned"
        ]
    ]
    .sort_values(
        by="retention_priority_score",
        ascending=False
    )
)

retention_priority.to_csv(
    os.path.join(
        REPORT_DIR,
        "retention_priority.csv"
    ),
    index=False
)


# ============================================================
# HIGH-VALUE CHURNED CUSTOMERS
# ============================================================

high_value_churned = customer_360[
    (
        customer_360["churned"] == 1
    )
    &
    (
        customer_360["value_segment"].isin(
            ["High Value", "Very High Value"]
        )
    )
].sort_values(
    by="estimated_customer_value",
    ascending=False
)

high_value_churned.to_csv(
    os.path.join(
        REPORT_DIR,
        "high_value_churned_customers.csv"
    ),
    index=False
)


# ============================================================
# CHART FUNCTION
# ============================================================

def save_bar_chart(
    dataframe,
    x,
    y,
    title,
    filename,
    xlabel=None,
    ylabel=None,
    rotation=0
):

    plt.figure(figsize=(11, 6))

    sns.barplot(
        data=dataframe,
        x=x,
        y=y
    )

    plt.title(title)
    plt.xlabel(xlabel if xlabel else x)
    plt.ylabel(ylabel if ylabel else y)

    plt.xticks(rotation=rotation)

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            CHART_DIR,
            filename
        ),
        dpi=160
    )

    plt.close()


# ============================================================
# CHART 1 — CHURN BY SEGMENT
# ============================================================

segment_chart = (
    customer_360
    .groupby("segment", observed=True)["churned"]
    .mean()
    .reset_index()
)

segment_chart["churned"] *= 100

save_bar_chart(
    segment_chart,
    "segment",
    "churned",
    "Customer Churn Rate by Segment",
    "churn_by_segment.png",
    ylabel="Churn Rate (%)"
)


# ============================================================
# CHART 2 — SATISFACTION
# ============================================================

satisfaction_chart = (
    customer_360
    .groupby(
        "satisfaction_group",
        observed=True
    )["churned"]
    .mean()
    .reset_index()
)

satisfaction_chart["churned"] *= 100

save_bar_chart(
    satisfaction_chart,
    "satisfaction_group",
    "churned",
    "Churn Rate by Satisfaction Level",
    "churn_by_satisfaction.png",
    ylabel="Churn Rate (%)"
)


# ============================================================
# CHART 3 — DIGITAL ENGAGEMENT
# ============================================================

engagement_chart = (
    customer_360
    .groupby(
        "engagement_group",
        observed=True
    )["churned"]
    .mean()
    .reset_index()
)

engagement_chart["churned"] *= 100

save_bar_chart(
    engagement_chart,
    "engagement_group",
    "churned",
    "Churn Rate by Digital Engagement",
    "churn_by_engagement.png",
    ylabel="Churn Rate (%)"
)


# ============================================================
# CHART 4 — PRODUCTS
# ============================================================

product_chart = (
    customer_360
    .groupby(
        "product_group",
        observed=True
    )["churned"]
    .mean()
    .reset_index()
)

product_chart["churned"] *= 100

save_bar_chart(
    product_chart,
    "product_group",
    "churned",
    "Churn Rate by Number of Products",
    "churn_by_products.png",
    ylabel="Churn Rate (%)"
)


# ============================================================
# CHART 5 — TENURE
# ============================================================

tenure_chart = (
    customer_360
    .groupby(
        "tenure_group",
        observed=True
    )["churned"]
    .mean()
    .reset_index()
)

tenure_chart["churned"] *= 100

save_bar_chart(
    tenure_chart,
    "tenure_group",
    "churned",
    "Churn Rate by Customer Tenure",
    "churn_by_tenure.png",
    ylabel="Churn Rate (%)"
)


# ============================================================
# CHART 6 — AGE
# ============================================================

age_chart = (
    customer_360
    .groupby(
        "age_group",
        observed=True
    )["churned"]
    .mean()
    .reset_index()
)

age_chart["churned"] *= 100

save_bar_chart(
    age_chart,
    "age_group",
    "churned",
    "Churn Rate by Age Group",
    "churn_by_age_group.png",
    ylabel="Churn Rate (%)"
)


# ============================================================
# CHART 7 — COMPLAINTS
# ============================================================

complaint_chart = (
    customer_360
    .groupby(
        "complaint_group",
        observed=True
    )["churned"]
    .mean()
    .reset_index()
)

complaint_chart["churned"] *= 100

save_bar_chart(
    complaint_chart,
    "complaint_group",
    "churned",
    "Churn Rate by Complaint Frequency",
    "churn_by_complaints.png",
    ylabel="Churn Rate (%)"
)


# ============================================================
# CHART 8 — TRANSACTION ACTIVITY
# ============================================================

customer_360["transaction_activity_group"] = pd.qcut(
    customer_360["transaction_count"].rank(
        method="first"
    ),
    q=5,
    labels=[
        "Very Low",
        "Low",
        "Medium",
        "High",
        "Very High"
    ]
)

transaction_activity_chart = (
    customer_360
    .groupby(
        "transaction_activity_group",
        observed=True
    )["churned"]
    .mean()
    .reset_index()
)

transaction_activity_chart["churned"] *= 100

save_bar_chart(
    transaction_activity_chart,
    "transaction_activity_group",
    "churned",
    "Churn Rate by Transaction Activity",
    "churn_by_transaction_activity.png",
    ylabel="Churn Rate (%)"
)


# ============================================================
# CHART 9 — CORRELATION HEATMAP
# ============================================================

heatmap_columns = [
    "age",
    "annual_income",
    "tenure_years",
    "product_count",
    "credit_score",
    "digital_engagement",
    "complaint_count",
    "satisfaction_score",
    "transaction_count",
    "loan_count",
    "credit_card_count",
    "avg_utilization_ratio",
    "interaction_count",
    "estimated_customer_value",
    "retention_risk_score",
    "churned"
]

heatmap_data = customer_360[
    [
        column
        for column in heatmap_columns
        if column in customer_360.columns
    ]
].corr()

plt.figure(
    figsize=(15, 11)
)

sns.heatmap(
    heatmap_data,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    center=0
)

plt.title(
    "Banking Customer Churn Correlation Heatmap"
)

plt.tight_layout()

plt.savefig(
    os.path.join(
        CHART_DIR,
        "correlation_heatmap.png"
    ),
    dpi=160
)

plt.close()


# ============================================================
# ANALYTICAL SUMMARY
# ============================================================

top_segment = (
    segment_analysis
    .sort_values(
        "churn_rate",
        ascending=False
    )
    .iloc[0]
)

top_statistical_drivers = (
    statistical_tests[
        statistical_tests["significant_5pct"] == True
    ]
    .head(10)
)

summary_lines = []

summary_lines.append(
    "BANKING CUSTOMER CHURN ANALYTICS SUMMARY"
)

summary_lines.append(
    "=" * 55
)

summary_lines.append(
    f"Total customers: {total_customers:,}"
)

summary_lines.append(
    f"Churned customers: {churned_customers:,}"
)

summary_lines.append(
    f"Overall churn rate: {churn_rate:.2f}%"
)

summary_lines.append(
    f"Average satisfaction score: {avg_satisfaction:.2f}"
)

summary_lines.append(
    f"Average digital engagement: {avg_engagement:.2f}"
)

summary_lines.append(
    f"Total account balance: {total_balance:,.2f}"
)

summary_lines.append(
    f"Total transaction value: {total_transaction_value:,.2f}"
)

summary_lines.append(
    f"Total loan exposure: {total_loan_exposure:,.2f}"
)

summary_lines.append(
    f"Total credit limit: {total_credit_limit:,.2f}"
)

summary_lines.append("")

summary_lines.append(
    f"Highest churn segment: "
    f"{top_segment['segment']} "
    f"({top_segment['churn_rate']:.2f}%)"
)

summary_lines.append("")

summary_lines.append(
    "Statistically significant drivers:"
)

for _, row in top_statistical_drivers.iterrows():

    summary_lines.append(
        f"- {row['feature']} | "
        f"{row['test']} | "
        f"p-value={row['p_value']:.6f}"
    )

summary_lines.append("")

summary_lines.append(
    "Analysis outputs saved under reports/."
)

summary_lines.append(
    "Dashboard charts saved under reports/charts/."
)


with open(
    os.path.join(
        REPORT_DIR,
        "analytics_summary.txt"
    ),
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "\n".join(summary_lines)
    )


# ============================================================
# FINAL OUTPUT
# ============================================================

print("\n" + "=" * 70)
print("PYTHON ANALYTICS COMPLETED")
print("=" * 70)

print(
    f"\nOverall churn rate: {churn_rate:.2f}%"
)

print(
    f"Highest churn segment: "
    f"{top_segment['segment']} "
    f"({top_segment['churn_rate']:.2f}%)"
)

print(
    "\nReports created:"
)

print(" - customer_360.csv")
print(" - kpi_summary.csv")
print(" - segment_analysis.csv")
print(" - churn_driver_summary.csv")
print(" - statistical_tests.csv")
print(" - numeric_correlations.csv")
print(" - churn_model_coefficients.csv")
print(" - retention_priority.csv")
print(" - high_value_churned_customers.csv")
print(" - analytics_summary.txt")

print(
    "\nCharts created in reports/charts/"
)

print(" - churn_by_segment.png")
print(" - churn_by_satisfaction.png")
print(" - churn_by_engagement.png")
print(" - churn_by_products.png")
print(" - churn_by_tenure.png")
print(" - churn_by_age_group.png")
print(" - churn_by_complaints.png")
print(" - churn_by_transaction_activity.png")
print(" - correlation_heatmap.png")

print("\n" + "=" * 70)
print("NEXT: BUILD THE STREAMLIT EXECUTIVE DASHBOARD")
print("=" * 70)