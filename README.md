# 🏦 Banking Customer Churn & Retention Analytics

An end-to-end Data Analytics project that analyzes banking customer behavior,
identifies churn drivers, segments customers by value and retention risk,
and provides an interactive executive dashboard for retention decision-making.

---

## 📌 Business Problem

Customer churn is one of the major challenges for banking organizations.

The objective of this project is to answer:

- Which customers are most likely to churn?
- What factors are associated with customer churn?
- Which customer segments have the highest churn?
- How do satisfaction and digital engagement affect retention?
- Does product ownership influence churn?
- Which high-value customers are at risk?
- Which customers should the bank prioritize for retention?
- What business actions can reduce potential customer loss?

---

## 🎯 Project Objectives

1. Build a realistic banking customer dataset.
2. Store and analyze data using SQLite.
3. Perform SQL-based business analysis.
4. Build a Customer 360 analytical dataset.
5. Identify churn drivers using statistical analysis.
6. Develop an interpretable retention risk score.
7. Identify high-value customers at risk.
8. Build an interactive executive dashboard.
9. Provide actionable business recommendations.

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data generation and analytics |
| Pandas | Data manipulation |
| NumPy | Numerical analysis |
| SciPy | Statistical testing |
| Scikit-learn | Interpretable churn modeling |
| Matplotlib | Analytical visualizations |
| Seaborn | Statistical visualizations |
| Plotly | Interactive dashboard charts |
| SQLite | Relational database |
| SQL | Business analytics |
| Streamlit | Interactive dashboard |

---

## 📂 Project Structure

```text
Banking_Customer_Churn_Analytics
│
├── data
│   ├── customers.csv
│   ├── accounts.csv
│   ├── transactions.csv
│   ├── loans.csv
│   ├── credit_cards.csv
│   └── interactions.csv
│
├── database
│   └── banking_analytics.db
│
├── sql
│   └── banking_analytics.sql
│
├── src
│   ├── generate_data.py
│   ├── run_sql.py
│   └── analytics.py
│
├── dashboard
│   └── app.py
│
├── reports
│   ├── customer_360.csv
│   ├── kpi_summary.csv
│   ├── segment_analysis.csv
│   ├── churn_driver_summary.csv
│   ├── statistical_tests.csv
│   ├── numeric_correlations.csv
│   ├── churn_model_coefficients.csv
│   ├── retention_priority.csv
│   ├── high_value_churned_customers.csv
│   └── charts
│
├── docs
│
├── requirements.txt
├── .gitignore
└── README.md