import sqlite3
from pathlib import Path


# ============================================================
# BANKING ANALYTICS
# SQL RUNNER
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = (
    BASE_DIR
    / "database"
    / "banking_analytics.db"
)

SQL_PATH = (
    BASE_DIR
    / "sql"
    / "banking_analytics.sql"
)

REPORTS_DIR = (
    BASE_DIR
    / "reports"
)

REPORTS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# CHECK FILES
# ============================================================

if not DATABASE_PATH.exists():

    raise FileNotFoundError(
        f"Database not found: {DATABASE_PATH}"
    )

if not SQL_PATH.exists():

    raise FileNotFoundError(
        f"SQL file not found: {SQL_PATH}"
    )


# ============================================================
# READ SQL
# ============================================================

sql_script = SQL_PATH.read_text(
    encoding="utf-8"
)


# ============================================================
# CONNECT DATABASE
# ============================================================

connection = sqlite3.connect(
    DATABASE_PATH
)

cursor = connection.cursor()


# ============================================================
# RUN SCRIPT
# ============================================================

print("\nRunning SQL analytics...\n")

try:

    cursor.executescript(
        sql_script
    )

    connection.commit()

    print(
        "SQL script executed successfully."
    )

except sqlite3.Error as error:

    connection.rollback()

    print(
        "\nSQL execution failed:"
    )

    print(error)

    connection.close()

    raise


# ============================================================
# DATABASE VALIDATION
# ============================================================

tables = cursor.execute(
    """
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name
    """
).fetchall()

print("\nDatabase tables:")

for table in tables:

    print(
        f"  - {table[0]}"
    )


# ============================================================
# KPI CHECK
# ============================================================

result = cursor.execute(
    """
    SELECT
        COUNT(*) AS total_customers,
        SUM(churned) AS churned_customers,
        ROUND(
            100.0 * SUM(churned)
            / COUNT(*),
            2
        ) AS churn_rate
    FROM customers
    """
).fetchone()

print("\nKPI CHECK")
print("-" * 40)

print(
    f"Total Customers : {result[0]:,}"
)

print(
    f"Churned         : {result[1]:,}"
)

print(
    f"Churn Rate      : {result[2]:.2f}%"
)


# ============================================================
# TOP SEGMENTS
# ============================================================

segments = cursor.execute(
    """
    SELECT
        segment,
        COUNT(*) AS customers,
        ROUND(
            100.0 * SUM(churned)
            / COUNT(*),
            2
        ) AS churn_rate
    FROM customers
    GROUP BY segment
    ORDER BY churn_rate DESC
    """
).fetchall()

print("\nCHURN BY SEGMENT")
print("-" * 40)

for segment in segments:

    print(
        f"{segment[0]:10} | "
        f"{segment[1]:5} customers | "
        f"{segment[2]:6.2f}% churn"
    )


# ============================================================
# HIGH-PRIORITY CUSTOMERS
# ============================================================

priority_customers = cursor.execute(
    """
    SELECT
        customer_code,
        segment,
        satisfaction_score,
        digital_engagement,
        complaint_count,
        product_count,
        churned,

        (
            CASE
                WHEN churned = 1
                    THEN 30
                ELSE 0
            END

            +

            CASE
                WHEN satisfaction_score <= 2
                    THEN 20
                ELSE 0
            END

            +

            CASE
                WHEN digital_engagement < 0.35
                    THEN 15
                ELSE 0
            END

            +

            CASE
                WHEN complaint_count >= 2
                    THEN 15
                ELSE 0
            END

            +

            CASE
                WHEN product_count = 1
                    THEN 10
                ELSE 0
            END

            +

            CASE
                WHEN tenure_years <= 1
                    THEN 10
                ELSE 0
            END

        ) AS priority_score

    FROM customers

    ORDER BY priority_score DESC

    LIMIT 10
    """
).fetchall()

print(
    "\nTOP 10 RETENTION PRIORITY CUSTOMERS"
)

print("-" * 70)

for row in priority_customers:

    print(
        f"{row[0]} | "
        f"{row[1]} | "
        f"Score: {row[7]}"
    )


# ============================================================
# SAVE SQL EXECUTION LOG
# ============================================================

log_file = (
    REPORTS_DIR
    / "sql_execution_log.txt"
)

with open(
    log_file,
    "w",
    encoding="utf-8",
) as file:

    file.write(
        "BANKING ANALYTICS SQL EXECUTION LOG\n"
    )

    file.write(
        "=" * 60
        + "\n\n"
    )

    file.write(
        f"Database: {DATABASE_PATH}\n"
    )

    file.write(
        f"SQL file: {SQL_PATH}\n\n"
    )

    file.write(
        f"Total customers: {result[0]:,}\n"
    )

    file.write(
        f"Churned customers: {result[1]:,}\n"
    )

    file.write(
        f"Churn rate: {result[2]:.2f}%\n"
    )


connection.close()

print(
    f"\nSQL execution log saved to:"
)

print(
    log_file
)

print(
    "\nSQL ANALYTICS COMPLETE."
)