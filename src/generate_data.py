import os
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# BANKING CUSTOMER CHURN & RETENTION ANALYTICS
# Synthetic Data Generator
# ============================================================

SEED = 42

random.seed(SEED)
np.random.seed(SEED)

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
DATABASE_DIR = BASE_DIR / "database"

DATA_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = DATABASE_DIR / "banking_analytics.db"


# ============================================================
# CONFIGURATION
# ============================================================

NUMBER_OF_CUSTOMERS = 10000
NUMBER_OF_TRANSACTIONS = 200000
NUMBER_OF_INTERACTIONS = 50000
NUMBER_OF_LOANS = 7000
NUMBER_OF_CREDIT_CARDS = 8500

START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 12, 31)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def random_date(start_date, end_date):
    days = (end_date - start_date).days
    return start_date + timedelta(days=random.randint(0, days))


def sigmoid(value):
    return 1 / (1 + np.exp(-value))


def create_customer_code(customer_id):
    return f"CUST{customer_id:06d}"


# ============================================================
# MASTER DATA
# ============================================================

FIRST_NAMES = [
    "Aarav",
    "Vivaan",
    "Aditya",
    "Arjun",
    "Kabir",
    "Rohan",
    "Rahul",
    "Ishaan",
    "Karan",
    "Ankit",
    "Raj",
    "Dev",
    "Varun",
    "Manish",
    "Siddharth",
    "Ananya",
    "Diya",
    "Aanya",
    "Meera",
    "Priya",
    "Ira",
    "Nisha",
    "Sara",
    "Riya",
    "Kavya",
]

LAST_NAMES = [
    "Sharma",
    "Singh",
    "Kumar",
    "Patel",
    "Gupta",
    "Verma",
    "Malhotra",
    "Kapoor",
    "Mehta",
    "Bansal",
    "Joshi",
    "Arora",
    "Khanna",
    "Sethi",
    "Chopra",
]

CITIES = [
    "Delhi",
    "Mumbai",
    "Bengaluru",
    "Hyderabad",
    "Pune",
    "Chandigarh",
    "Ludhiana",
    "Jaipur",
    "Kolkata",
    "Chennai",
    "Ahmedabad",
    "Lucknow",
]

STATES = {
    "Delhi": "Delhi",
    "Mumbai": "Maharashtra",
    "Bengaluru": "Karnataka",
    "Hyderabad": "Telangana",
    "Pune": "Maharashtra",
    "Chandigarh": "Chandigarh",
    "Ludhiana": "Punjab",
    "Jaipur": "Rajasthan",
    "Kolkata": "West Bengal",
    "Chennai": "Tamil Nadu",
    "Ahmedabad": "Gujarat",
    "Lucknow": "Uttar Pradesh",
}

OCCUPATIONS = [
    "Salaried",
    "Self Employed",
    "Business Owner",
    "Student",
    "Retired",
]

CUSTOMER_SEGMENTS = [
    "Mass",
    "Affluent",
    "Premium",
]

ACCOUNT_TYPES = [
    "Savings",
    "Current",
    "Salary",
    "Premium Savings",
]

ACCOUNT_STATUSES = [
    "Active",
    "Active",
    "Active",
    "Dormant",
]

TRANSACTION_TYPES = [
    "Purchase",
    "Cash Withdrawal",
    "Transfer",
    "Bill Payment",
    "Salary Credit",
    "Deposit",
    "Fee",
    "Refund",
]

TRANSACTION_CHANNELS = [
    "Mobile App",
    "Internet Banking",
    "ATM",
    "POS",
    "Branch",
]

LOAN_TYPES = [
    "Personal Loan",
    "Home Loan",
    "Auto Loan",
    "Education Loan",
]

LOAN_STATUSES = [
    "Active",
    "Active",
    "Active",
    "Closed",
    "Overdue",
]

CARD_TYPES = [
    "Classic",
    "Gold",
    "Platinum",
    "Signature",
]

CARD_STATUSES = [
    "Active",
    "Active",
    "Active",
    "Blocked",
    "Closed",
]

INTERACTION_TYPES = [
    "Complaint",
    "Service Request",
    "Branch Visit",
    "Call",
    "Chat",
    "Email",
]

SENTIMENTS = [
    "Positive",
    "Neutral",
    "Negative",
]

RESOLUTIONS = [
    "Resolved",
    "Resolved",
    "Resolved",
    "Pending",
    "Escalated",
]

CHANNELS = [
    "Branch",
    "Mobile App",
    "Internet Banking",
    "ATM",
    "Call Center",
]


# ============================================================
# 1. CUSTOMERS
# ============================================================

print("\n[1/6] Generating customers...")

customers = []

for customer_id in range(1, NUMBER_OF_CUSTOMERS + 1):

    age = int(
        np.clip(
            np.random.normal(
                loc=38,
                scale=11,
            ),
            18,
            75,
        )
    )

    annual_income = int(
        np.clip(
            np.random.lognormal(
                mean=13.0,
                sigma=0.55,
            ),
            180000,
            7000000,
        )
    )

    if annual_income >= 2000000:
        segment = "Premium"
    elif annual_income >= 800000:
        segment = "Affluent"
    else:
        segment = "Mass"

    tenure_years = int(
        np.clip(
            np.random.gamma(
                shape=3.0,
                scale=2.0,
            ),
            0,
            20,
        )
    )

    product_count = int(
        np.clip(
            np.random.poisson(
                lam=2.0
            ) + 1,
            1,
            6,
        )
    )

    credit_score = int(
        np.clip(
            np.random.normal(
                loc=710,
                scale=55,
            ),
            300,
            850,
        )
    )

    digital_engagement = round(
        float(
            np.clip(
                np.random.beta(
                    4,
                    2,
                ),
                0,
                1,
            )
        ),
        3,
    )

    complaint_count = int(
        np.random.poisson(
            0.35
        )
    )

    satisfaction_score = int(
        np.clip(
            round(
                np.random.normal(
                    loc=4.0 - complaint_count * 0.25,
                    scale=0.7,
                )
            ),
            1,
            5,
        )
    )

    primary_channel = random.choice(
        CHANNELS
    )

    city = random.choice(
        CITIES
    )

    state = STATES[city]

    occupation = random.choice(
        OCCUPATIONS
    )

    first_name = random.choice(
        FIRST_NAMES
    )

    last_name = random.choice(
        LAST_NAMES
    )

    # --------------------------------------------------------
    # Churn probability
    # --------------------------------------------------------

    churn_score = (
        -3.0

        + 0.75 * (
            product_count <= 1
        )

        + 0.75 * (
            satisfaction_score <= 2
        )

        + 0.55 * (
            complaint_count >= 2
        )

        + 0.65 * (
            digital_engagement < 0.35
        )

        + 0.60 * (
            tenure_years <= 1
        )

        + 0.40 * (
            credit_score < 580
        )

        + 0.35 * (
            age > 60
        )

        + 0.35 * (
            segment == "Mass"
        )

        + 0.25 * (
            annual_income < 350000
        )
    )

    churn_probability = sigmoid(
        churn_score
    )

    churned = int(
        np.random.random()
        < churn_probability
    )

    # --------------------------------------------------------
    # Customer date
    # --------------------------------------------------------

    customer_join_date = (
        END_DATE
        - timedelta(
            days=random.randint(
                30,
                365 * 15,
            )
        )
    )

    customers.append(
        {
            "customer_id": customer_id,
            "customer_code": create_customer_code(
                customer_id
            ),
            "first_name": first_name,
            "last_name": last_name,
            "age": age,
            "city": city,
            "state": state,
            "occupation": occupation,
            "annual_income": annual_income,
            "segment": segment,
            "customer_join_date": customer_join_date.date(),
            "tenure_years": tenure_years,
            "product_count": product_count,
            "credit_score": credit_score,
            "digital_engagement": digital_engagement,
            "complaint_count": complaint_count,
            "satisfaction_score": satisfaction_score,
            "primary_channel": primary_channel,
            "churn_probability": round(
                churn_probability,
                4,
            ),
            "churned": churned,
        }
    )

customers_df = pd.DataFrame(
    customers
)

print(
    f"Customers generated: "
    f"{len(customers_df):,}"
)


# ============================================================
# 2. ACCOUNTS
# ============================================================

print("\n[2/6] Generating accounts...")

accounts = []

account_id = 1

for _, customer in customers_df.iterrows():

    number_of_accounts = int(
        np.clip(
            np.random.poisson(
                1.3
            ) + 1,
            1,
            5,
        )
    )

    for _ in range(
        number_of_accounts
    ):

        account_type = random.choice(
            ACCOUNT_TYPES
        )

        balance = max(
            100,
            np.random.lognormal(
                mean=10.2
                if customer["segment"] == "Mass"
                else 11.2,
                sigma=1.0,
            ),
        )

        opened_date = (
            END_DATE
            - timedelta(
                days=random.randint(
                    60,
                    365 * 12,
                )
            )
        )

        status = random.choice(
            ACCOUNT_STATUSES
        )

        accounts.append(
            {
                "account_id": account_id,
                "customer_id": customer[
                    "customer_id"
                ],
                "account_type": account_type,
                "balance": round(
                    balance,
                    2,
                ),
                "opened_date": opened_date.date(),
                "status": status,
            }
        )

        account_id += 1

accounts_df = pd.DataFrame(
    accounts
)

print(
    f"Accounts generated: "
    f"{len(accounts_df):,}"
)


# ============================================================
# 3. TRANSACTIONS
# ============================================================

print("\n[3/6] Generating transactions...")

customer_ids = customers_df[
    "customer_id"
].values

transactions = []

for transaction_id in range(
    1,
    NUMBER_OF_TRANSACTIONS + 1,
):

    customer_id = int(
        np.random.choice(
            customer_ids
        )
    )

    transaction_type = random.choices(
        TRANSACTION_TYPES,
        weights=[
            0.36,
            0.10,
            0.15,
            0.12,
            0.07,
            0.10,
            0.04,
            0.06,
        ],
    )[0]

    transaction_channel = random.choice(
        TRANSACTION_CHANNELS
    )

    transaction_date = random_date(
        START_DATE,
        END_DATE,
    )

    amount = np.random.lognormal(
        mean=7.0,
        sigma=1.0,
    )

    if transaction_type == "Salary Credit":
        amount *= 8

    elif transaction_type == "Deposit":
        amount *= 3

    elif transaction_type == "Fee":
        amount = np.random.uniform(
            50,
            500,
        )

    elif transaction_type == "Refund":
        amount *= 0.5

    elif transaction_type == "Cash Withdrawal":
        amount *= 0.8

    transactions.append(
        {
            "transaction_id": transaction_id,
            "customer_id": customer_id,
            "transaction_date": transaction_date.date(),
            "transaction_type": transaction_type,
            "amount": round(
                amount,
                2,
            ),
            "channel": transaction_channel,
        }
    )

transactions_df = pd.DataFrame(
    transactions
)

print(
    f"Transactions generated: "
    f"{len(transactions_df):,}"
)


# ============================================================
# 4. LOANS
# ============================================================

print("\n[4/6] Generating loans...")

loans = []

loan_principal = {
    "Personal Loan": 250000,
    "Home Loan": 2500000,
    "Auto Loan": 700000,
    "Education Loan": 500000,
}

for loan_id in range(
    1,
    NUMBER_OF_LOANS + 1,
):

    customer_id = random.randint(
        1,
        NUMBER_OF_CUSTOMERS,
    )

    loan_type = random.choice(
        LOAN_TYPES
    )

    base_amount = loan_principal[
        loan_type
    ]

    loan_amount = max(
        50000,
        np.random.normal(
            base_amount,
            base_amount * 0.35,
        ),
    )

    interest_rate = round(
        np.clip(
            np.random.normal(
                10.5,
                2.0,
            ),
            6,
            18,
        ),
        2,
    )

    loan_status = random.choice(
        LOAN_STATUSES
    )

    start_date = random_date(
        datetime(2022, 1, 1),
        END_DATE,
    )

    loans.append(
        {
            "loan_id": loan_id,
            "customer_id": customer_id,
            "loan_type": loan_type,
            "loan_amount": round(
                loan_amount,
                2,
            ),
            "interest_rate": interest_rate,
            "status": loan_status,
            "start_date": start_date.date(),
        }
    )

loans_df = pd.DataFrame(
    loans
)

print(
    f"Loans generated: "
    f"{len(loans_df):,}"
)


# ============================================================
# 5. CREDIT CARDS
# ============================================================

print("\n[5/6] Generating credit cards...")

credit_cards = []

for card_id in range(
    1,
    NUMBER_OF_CREDIT_CARDS + 1,
):

    customer_id = random.randint(
        1,
        NUMBER_OF_CUSTOMERS,
    )

    card_type = random.choice(
        CARD_TYPES
    )

    credit_limit = {
        "Classic": 100000,
        "Gold": 250000,
        "Platinum": 500000,
        "Signature": 1000000,
    }[card_type]

    credit_limit = round(
        np.random.uniform(
            credit_limit * 0.7,
            credit_limit * 1.3,
        ),
        2,
    )

    utilization = round(
        np.random.beta(
            2,
            5,
        ),
        3,
    )

    current_balance = round(
        credit_limit * utilization,
        2,
    )

    card_status = random.choice(
        CARD_STATUSES
    )

    issue_date = random_date(
        datetime(2021, 1, 1),
        END_DATE,
    )

    credit_cards.append(
        {
            "card_id": card_id,
            "customer_id": customer_id,
            "card_type": card_type,
            "credit_limit": credit_limit,
            "utilization_ratio": utilization,
            "current_balance": current_balance,
            "status": card_status,
            "issue_date": issue_date.date(),
        }
    )

credit_cards_df = pd.DataFrame(
    credit_cards
)

print(
    f"Credit cards generated: "
    f"{len(credit_cards_df):,}"
)


# ============================================================
# 6. CUSTOMER INTERACTIONS
# ============================================================

print(
    "\n[6/6] Generating customer interactions..."
)

interactions = []

for interaction_id in range(
    1,
    NUMBER_OF_INTERACTIONS + 1,
):

    customer_id = random.randint(
        1,
        NUMBER_OF_CUSTOMERS,
    )

    interaction_type = random.choice(
        INTERACTION_TYPES
    )

    sentiment = random.choices(
        SENTIMENTS,
        weights=[
            0.42,
            0.35,
            0.23,
        ],
    )[0]

    resolution = random.choice(
        RESOLUTIONS
    )

    interaction_date = random_date(
        START_DATE,
        END_DATE,
    )

    resolution_days = np.random.randint(
        1,
        8,
    )

    interactions.append(
        {
            "interaction_id": interaction_id,
            "customer_id": customer_id,
            "interaction_date": interaction_date.date(),
            "interaction_type": interaction_type,
            "sentiment": sentiment,
            "resolution": resolution,
            "resolution_days": resolution_days,
        }
    )

interactions_df = pd.DataFrame(
    interactions
)

print(
    f"Interactions generated: "
    f"{len(interactions_df):,}"
)


# ============================================================
# SAVE CSV FILES
# ============================================================

print("\nSaving CSV files...")

datasets = {
    "customers": customers_df,
    "accounts": accounts_df,
    "transactions": transactions_df,
    "loans": loans_df,
    "credit_cards": credit_cards_df,
    "interactions": interactions_df,
}

for name, dataframe in datasets.items():

    file_path = (
        DATA_DIR
        / f"{name}.csv"
    )

    dataframe.to_csv(
        file_path,
        index=False,
    )

    print(
        f"Saved: {file_path}"
    )


# ============================================================
# CREATE SQLITE DATABASE
# ============================================================

print("\nCreating SQLite database...")

if DATABASE_PATH.exists():
    DATABASE_PATH.unlink()

connection = sqlite3.connect(
    DATABASE_PATH
)

for table_name, dataframe in datasets.items():

    dataframe.to_sql(
        table_name,
        connection,
        if_exists="replace",
        index=False,
    )

connection.commit()
connection.close()


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("BANKING DATA GENERATION COMPLETE")
print("=" * 60)

print(
    f"Customers       : {len(customers_df):,}"
)

print(
    f"Accounts        : {len(accounts_df):,}"
)

print(
    f"Transactions    : {len(transactions_df):,}"
)

print(
    f"Loans           : {len(loans_df):,}"
)

print(
    f"Credit Cards    : {len(credit_cards_df):,}"
)

print(
    f"Interactions    : {len(interactions_df):,}"
)

print(
    f"Churned         : "
    f"{customers_df['churned'].sum():,}"
)

print(
    f"Churn Rate      : "
    f"{customers_df['churned'].mean():.2%}"
)

print(
    f"\nDatabase       : "
    f"{DATABASE_PATH}"
)

print(
    f"CSV Directory  : "
    f"{DATA_DIR}"
)

print("=" * 60)