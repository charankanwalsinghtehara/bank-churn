-- ============================================================
-- BANKING CUSTOMER CHURN & RETENTION ANALYTICS
-- SQL ANALYTICS LAYER
-- Database: SQLite
-- ============================================================


-- ============================================================
-- 1. DATABASE VALIDATION
-- ============================================================

SELECT 'customers' AS table_name, COUNT(*) AS row_count
FROM customers

UNION ALL

SELECT 'accounts', COUNT(*)
FROM accounts

UNION ALL

SELECT 'transactions', COUNT(*)
FROM transactions

UNION ALL

SELECT 'loans', COUNT(*)
FROM loans

UNION ALL

SELECT 'credit_cards', COUNT(*)
FROM credit_cards

UNION ALL

SELECT 'interactions', COUNT(*)
FROM interactions;


-- ============================================================
-- 2. EXECUTIVE KPI SUMMARY
-- ============================================================

SELECT
    COUNT(*) AS total_customers,

    SUM(churned) AS churned_customers,

    COUNT(*) - SUM(churned) AS retained_customers,

    ROUND(
        100.0 * SUM(churned) / COUNT(*),
        2
    ) AS churn_rate_pct,

    ROUND(
        AVG(annual_income),
        2
    ) AS average_annual_income,

    ROUND(
        AVG(satisfaction_score),
        2
    ) AS average_satisfaction,

    ROUND(
        AVG(credit_score),
        2
    ) AS average_credit_score,

    ROUND(
        AVG(digital_engagement),
        3
    ) AS average_digital_engagement,

    ROUND(
        AVG(product_count),
        2
    ) AS average_products_per_customer

FROM customers;


-- ============================================================
-- 3. CUSTOMER SEGMENT ANALYSIS
-- ============================================================

SELECT

    segment,

    COUNT(*) AS total_customers,

    SUM(churned) AS churned_customers,

    COUNT(*) - SUM(churned)
        AS retained_customers,

    ROUND(
        100.0 * SUM(churned) / COUNT(*),
        2
    ) AS churn_rate_pct,

    ROUND(
        AVG(annual_income),
        2
    ) AS average_income,

    ROUND(
        AVG(satisfaction_score),
        2
    ) AS average_satisfaction,

    ROUND(
        AVG(product_count),
        2
    ) AS average_products

FROM customers

GROUP BY segment

ORDER BY churn_rate_pct DESC;


-- ============================================================
-- 4. CHURN BY CITY
-- ============================================================

SELECT

    city,

    state,

    COUNT(*) AS customers,

    SUM(churned) AS churned_customers,

    ROUND(
        100.0 * SUM(churned) / COUNT(*),
        2
    ) AS churn_rate_pct

FROM customers

GROUP BY
    city,
    state

ORDER BY
    churn_rate_pct DESC;


-- ============================================================
-- 5. CHURN BY OCCUPATION
-- ============================================================

SELECT

    occupation,

    COUNT(*) AS customers,

    SUM(churned) AS churned_customers,

    ROUND(
        100.0 * SUM(churned) / COUNT(*),
        2
    ) AS churn_rate_pct,

    ROUND(
        AVG(annual_income),
        2
    ) AS average_income

FROM customers

GROUP BY occupation

ORDER BY churn_rate_pct DESC;


-- ============================================================
-- 6. CHURN BY AGE GROUP
-- ============================================================

WITH age_groups AS (

    SELECT

        customer_id,

        churned,

        CASE

            WHEN age < 25
                THEN '18-24'

            WHEN age < 35
                THEN '25-34'

            WHEN age < 45
                THEN '35-44'

            WHEN age < 55
                THEN '45-54'

            WHEN age < 65
                THEN '55-64'

            ELSE '65+'

        END AS age_group

    FROM customers
)

SELECT

    age_group,

    COUNT(*) AS customers,

    SUM(churned) AS churned_customers,

    ROUND(
        100.0 * SUM(churned) / COUNT(*),
        2
    ) AS churn_rate_pct

FROM age_groups

GROUP BY age_group

ORDER BY age_group;


-- ============================================================
-- 7. CHURN BY TENURE
-- ============================================================

SELECT

    tenure_years,

    COUNT(*) AS customers,

    SUM(churned) AS churned_customers,

    ROUND(
        100.0 * SUM(churned) / COUNT(*),
        2
    ) AS churn_rate_pct

FROM customers

GROUP BY tenure_years

ORDER BY tenure_years;


-- ============================================================
-- 8. TENURE BUCKET ANALYSIS
-- ============================================================

WITH tenure_groups AS (

    SELECT

        customer_id,

        churned,

        CASE

            WHEN tenure_years <= 1
                THEN '0-1 Years'

            WHEN tenure_years <= 3
                THEN '2-3 Years'

            WHEN tenure_years <= 5
                THEN '4-5 Years'

            WHEN tenure_years <= 10
                THEN '6-10 Years'

            ELSE '10+ Years'

        END AS tenure_group

    FROM customers
)

SELECT

    tenure_group,

    COUNT(*) AS customers,

    SUM(churned) AS churned_customers,

    ROUND(
        100.0 * SUM(churned) / COUNT(*),
        2
    ) AS churn_rate_pct

FROM tenure_groups

GROUP BY tenure_group

ORDER BY churn_rate_pct DESC;


-- ============================================================
-- 9. CHURN BY NUMBER OF PRODUCTS
-- ============================================================

SELECT

    product_count,

    COUNT(*) AS customers,

    SUM(churned) AS churned_customers,

    ROUND(
        100.0 * SUM(churned) / COUNT(*),
        2
    ) AS churn_rate_pct

FROM customers

GROUP BY product_count

ORDER BY product_count;


-- ============================================================
-- 10. PRODUCT PENETRATION
-- ============================================================

SELECT

    product_count,

    COUNT(*) AS customers,

    ROUND(
        100.0 * COUNT(*) /
        SUM(COUNT(*)) OVER (),
        2
    ) AS customer_share_pct

FROM customers

GROUP BY product_count

ORDER BY product_count;


-- ============================================================
-- 11. SATISFACTION VS CHURN
-- ============================================================

SELECT

    satisfaction_score,

    COUNT(*) AS customers,

    SUM(churned) AS churned_customers,

    ROUND(
        100.0 * SUM(churned) / COUNT(*),
        2
    ) AS churn_rate_pct

FROM customers

GROUP BY satisfaction_score

ORDER BY satisfaction_score;


-- ============================================================
-- 12. DIGITAL ENGAGEMENT VS CHURN
-- ============================================================

WITH engagement_groups AS (

    SELECT

        customer_id,

        churned,

        digital_engagement,

        CASE

            WHEN digital_engagement < 0.35
                THEN 'Low'

            WHEN digital_engagement < 0.65
                THEN 'Medium'

            ELSE 'High'

        END AS engagement_group

    FROM customers
)

SELECT

    engagement_group,

    COUNT(*) AS customers,

    SUM(churned) AS churned_customers,

    ROUND(
        100.0 * SUM(churned) / COUNT(*),
        2
    ) AS churn_rate_pct,

    ROUND(
        AVG(digital_engagement),
        3
    ) AS average_engagement

FROM engagement_groups

GROUP BY engagement_group

ORDER BY churn_rate_pct DESC;


-- ============================================================
-- 13. COMPLAINTS VS CHURN
-- ============================================================

SELECT

    complaint_count,

    COUNT(*) AS customers,

    SUM(churned) AS churned_customers,

    ROUND(
        100.0 * SUM(churned) / COUNT(*),
        2
    ) AS churn_rate_pct

FROM customers

GROUP BY complaint_count

ORDER BY complaint_count;


-- ============================================================
-- 14. PRIMARY CHANNEL VS CHURN
-- ============================================================

SELECT

    primary_channel,

    COUNT(*) AS customers,

    SUM(churned) AS churned_customers,

    ROUND(
        100.0 * SUM(churned) / COUNT(*),
        2
    ) AS churn_rate_pct

FROM customers

GROUP BY primary_channel

ORDER BY churn_rate_pct DESC;


-- ============================================================
-- 15. CREDIT SCORE GROUP VS CHURN
-- ============================================================

WITH credit_groups AS (

    SELECT

        customer_id,

        churned,

        CASE

            WHEN credit_score < 580
                THEN 'Poor'

            WHEN credit_score < 670
                THEN 'Fair'

            WHEN credit_score < 740
                THEN 'Good'

            WHEN credit_score < 800
                THEN 'Very Good'

            ELSE 'Excellent'

        END AS credit_group

    FROM customers
)

SELECT

    credit_group,

    COUNT(*) AS customers,

    SUM(churned) AS churned_customers,

    ROUND(
        100.0 * SUM(churned) / COUNT(*),
        2
    ) AS churn_rate_pct

FROM credit_groups

GROUP BY credit_group

ORDER BY churn_rate_pct DESC;


-- ============================================================
-- 16. ACCOUNT ANALYSIS
-- ============================================================

SELECT

    account_type,

    COUNT(*) AS accounts,

    COUNT(
        DISTINCT customer_id
    ) AS customers,

    ROUND(
        AVG(balance),
        2
    ) AS average_balance,

    ROUND(
        SUM(balance),
        2
    ) AS total_balance

FROM accounts

GROUP BY account_type

ORDER BY total_balance DESC;


-- ============================================================
-- 17. CUSTOMER ACCOUNT VALUE
-- ============================================================

SELECT

    c.customer_id,

    c.customer_code,

    c.segment,

    c.churned,

    COUNT(a.account_id)
        AS account_count,

    ROUND(
        SUM(a.balance),
        2
    ) AS total_balance

FROM customers c

LEFT JOIN accounts a

    ON c.customer_id = a.customer_id

GROUP BY

    c.customer_id,
    c.customer_code,
    c.segment,
    c.churned

ORDER BY total_balance DESC;


-- ============================================================
-- 18. TRANSACTION KPIs
-- ============================================================

SELECT

    COUNT(*) AS total_transactions,

    ROUND(
        SUM(amount),
        2
    ) AS total_transaction_value,

    ROUND(
        AVG(amount),
        2
    ) AS average_transaction_value,

    COUNT(
        DISTINCT customer_id
    ) AS active_transaction_customers

FROM transactions;


-- ============================================================
-- 19. TRANSACTION TYPE ANALYSIS
-- ============================================================

SELECT

    transaction_type,

    COUNT(*) AS transaction_count,

    ROUND(
        SUM(amount),
        2
    ) AS transaction_value,

    ROUND(
        AVG(amount),
        2
    ) AS average_transaction_value

FROM transactions

GROUP BY transaction_type

ORDER BY transaction_value DESC;


-- ============================================================
-- 20. TRANSACTION CHANNEL ANALYSIS
-- ============================================================

SELECT

    channel,

    COUNT(*) AS transactions,

    ROUND(
        SUM(amount),
        2
    ) AS transaction_value,

    ROUND(
        AVG(amount),
        2
    ) AS average_transaction_value

FROM transactions

GROUP BY channel

ORDER BY transaction_value DESC;


-- ============================================================
-- 21. CUSTOMER TRANSACTION ACTIVITY
-- ============================================================

WITH customer_transactions AS (

    SELECT

        customer_id,

        COUNT(*) AS transaction_count,

        SUM(amount) AS transaction_value,

        AVG(amount) AS average_transaction_value

    FROM transactions

    GROUP BY customer_id
)

SELECT

    c.customer_id,

    c.customer_code,

    c.segment,

    c.churned,

    COALESCE(
        ct.transaction_count,
        0
    ) AS transaction_count,

    ROUND(
        COALESCE(
            ct.transaction_value,
            0
        ),
        2
    ) AS transaction_value,

    ROUND(
        COALESCE(
            ct.average_transaction_value,
            0
        ),
        2
    ) AS average_transaction_value

FROM customers c

LEFT JOIN customer_transactions ct

    ON c.customer_id = ct.customer_id;


-- ============================================================
-- 22. TRANSACTION ACTIVITY VS CHURN
-- ============================================================

WITH customer_transactions AS (

    SELECT

        customer_id,

        COUNT(*) AS transaction_count

    FROM transactions

    GROUP BY customer_id
),

activity_groups AS (

    SELECT

        c.customer_id,

        c.churned,

        COALESCE(
            ct.transaction_count,
            0
        ) AS transaction_count

    FROM customers c

    LEFT JOIN customer_transactions ct

        ON c.customer_id = ct.customer_id
)

SELECT

    CASE

        WHEN transaction_count < 10
            THEN 'Low Activity'

        WHEN transaction_count < 25
            THEN 'Medium Activity'

        WHEN transaction_count < 50
            THEN 'High Activity'

        ELSE 'Very High Activity'

    END AS activity_group,

    COUNT(*) AS customers,

    SUM(churned) AS churned_customers,

    ROUND(
        100.0 * SUM(churned) / COUNT(*),
        2
    ) AS churn_rate_pct

FROM activity_groups

GROUP BY activity_group

ORDER BY churn_rate_pct DESC;


-- ============================================================
-- 23. LOAN PORTFOLIO ANALYSIS
-- ============================================================

SELECT

    loan_type,

    COUNT(*) AS loan_count,

    COUNT(
        DISTINCT customer_id
    ) AS customers,

    ROUND(
        SUM(loan_amount),
        2
    ) AS total_loan_value,

    ROUND(
        AVG(loan_amount),
        2
    ) AS average_loan_value,

    ROUND(
        AVG(interest_rate),
        2
    ) AS average_interest_rate

FROM loans

GROUP BY loan_type

ORDER BY total_loan_value DESC;


-- ============================================================
-- 24. LOAN STATUS ANALYSIS
-- ============================================================

SELECT

    status,

    COUNT(*) AS loans,

    ROUND(
        SUM(loan_amount),
        2
    ) AS loan_value

FROM loans

GROUP BY status

ORDER BY loan_value DESC;


-- ============================================================
-- 25. CUSTOMER LOAN EXPOSURE
-- ============================================================

SELECT

    c.customer_id,

    c.customer_code,

    c.segment,

    c.churned,

    COUNT(l.loan_id)
        AS loan_count,

    ROUND(
        COALESCE(
            SUM(l.loan_amount),
            0
        ),
        2
    ) AS total_loan_exposure

FROM customers c

LEFT JOIN loans l

    ON c.customer_id = l.customer_id

GROUP BY

    c.customer_id,

    c.customer_code,

    c.segment,

    c.churned

ORDER BY total_loan_exposure DESC;


-- ============================================================
-- 26. CREDIT CARD ANALYSIS
-- ============================================================

SELECT

    card_type,

    COUNT(*) AS cards,

    COUNT(
        DISTINCT customer_id
    ) AS customers,

    ROUND(
        AVG(credit_limit),
        2
    ) AS average_credit_limit,

    ROUND(
        AVG(utilization_ratio),
        3
    ) AS average_utilization,

    ROUND(
        SUM(current_balance),
        2
    ) AS total_card_balance

FROM credit_cards

GROUP BY card_type

ORDER BY total_card_balance DESC;


-- ============================================================
-- 27. CREDIT CARD UTILIZATION VS CHURN
-- ============================================================

WITH customer_cards AS (

    SELECT

        customer_id,

        AVG(utilization_ratio)
            AS avg_utilization

    FROM credit_cards

    GROUP BY customer_id
)

SELECT

    CASE

        WHEN avg_utilization < 0.30
            THEN 'Low Utilization'

        WHEN avg_utilization < 0.60
            THEN 'Medium Utilization'

        WHEN avg_utilization < 0.80
            THEN 'High Utilization'

        ELSE 'Very High Utilization'

    END AS utilization_group,

    COUNT(*) AS customers,

    SUM(c.churned)
        AS churned_customers,

    ROUND(
        100.0 * SUM(c.churned)
        / COUNT(*),
        2
    ) AS churn_rate_pct

FROM customer_cards cc

JOIN customers c

    ON cc.customer_id = c.customer_id

GROUP BY utilization_group

ORDER BY churn_rate_pct DESC;


-- ============================================================
-- 28. CUSTOMER INTERACTION ANALYSIS
-- ============================================================

SELECT

    interaction_type,

    COUNT(*) AS interaction_count,

    ROUND(
        AVG(resolution_days),
        2
    ) AS average_resolution_days

FROM interactions

GROUP BY interaction_type

ORDER BY interaction_count DESC;


-- ============================================================
-- 29. SENTIMENT ANALYSIS
-- ============================================================

SELECT

    sentiment,

    COUNT(*) AS interactions,

    ROUND(
        AVG(resolution_days),
        2
    ) AS average_resolution_days

FROM interactions

GROUP BY sentiment

ORDER BY interactions DESC;


-- ============================================================
-- 30. SENTIMENT VS CUSTOMER CHURN
-- ============================================================

SELECT

    i.sentiment,

    COUNT(
        DISTINCT i.customer_id
    ) AS customers,

    COUNT(*) AS interactions,

    SUM(
        CASE
            WHEN c.churned = 1
            THEN 1
            ELSE 0
        END
    ) AS interactions_from_churned_customers

FROM interactions i

JOIN customers c

    ON i.customer_id = c.customer_id

GROUP BY i.sentiment

ORDER BY interactions_from_churned_customers DESC;


-- ============================================================
-- 31. CUSTOMER 360
-- ============================================================

WITH account_summary AS (

    SELECT

        customer_id,

        COUNT(*) AS account_count,

        SUM(balance) AS total_balance

    FROM accounts

    GROUP BY customer_id
),

transaction_summary AS (

    SELECT

        customer_id,

        COUNT(*) AS transaction_count,

        SUM(amount) AS transaction_value,

        AVG(amount) AS average_transaction

    FROM transactions

    GROUP BY customer_id
),

loan_summary AS (

    SELECT

        customer_id,

        COUNT(*) AS loan_count,

        SUM(loan_amount) AS loan_exposure

    FROM loans

    GROUP BY customer_id
),

card_summary AS (

    SELECT

        customer_id,

        COUNT(*) AS card_count,

        AVG(utilization_ratio)
            AS average_card_utilization,

        SUM(current_balance)
            AS card_balance

    FROM credit_cards

    GROUP BY customer_id
),

interaction_summary AS (

    SELECT

        customer_id,

        COUNT(*) AS interaction_count,

        SUM(
            CASE
                WHEN sentiment = 'Negative'
                THEN 1
                ELSE 0
            END
        ) AS negative_interactions

    FROM interactions

    GROUP BY customer_id
)

SELECT

    c.customer_id,

    c.customer_code,

    c.first_name,

    c.last_name,

    c.age,

    c.city,

    c.state,

    c.occupation,

    c.annual_income,

    c.segment,

    c.tenure_years,

    c.product_count,

    c.credit_score,

    c.digital_engagement,

    c.complaint_count,

    c.satisfaction_score,

    c.primary_channel,

    c.churn_probability,

    c.churned,

    COALESCE(
        a.account_count,
        0
    ) AS account_count,

    ROUND(
        COALESCE(
            a.total_balance,
            0
        ),
        2
    ) AS total_balance,

    COALESCE(
        t.transaction_count,
        0
    ) AS transaction_count,

    ROUND(
        COALESCE(
            t.transaction_value,
            0
        ),
        2
    ) AS transaction_value,

    ROUND(
        COALESCE(
            t.average_transaction,
            0
        ),
        2
    ) AS average_transaction,

    COALESCE(
        l.loan_count,
        0
    ) AS loan_count,

    ROUND(
        COALESCE(
            l.loan_exposure,
            0
        ),
        2
    ) AS loan_exposure,

    COALESCE(
        cs.card_count,
        0
    ) AS card_count,

    ROUND(
        COALESCE(
            cs.average_card_utilization,
            0
        ),
        3
    ) AS average_card_utilization,

    ROUND(
        COALESCE(
            cs.card_balance,
            0
        ),
        2
    ) AS card_balance,

    COALESCE(
        i.interaction_count,
        0
    ) AS interaction_count,

    COALESCE(
        i.negative_interactions,
        0
    ) AS negative_interactions

FROM customers c

LEFT JOIN account_summary a
    ON c.customer_id = a.customer_id

LEFT JOIN transaction_summary t
    ON c.customer_id = t.customer_id

LEFT JOIN loan_summary l
    ON c.customer_id = l.customer_id

LEFT JOIN card_summary cs
    ON c.customer_id = cs.customer_id

LEFT JOIN interaction_summary i
    ON c.customer_id = i.customer_id;


-- ============================================================
-- 32. CUSTOMER VALUE SEGMENTATION
-- ============================================================

WITH customer_value AS (

    SELECT

        c.customer_id,

        c.customer_code,

        c.segment,

        c.churned,

        COALESCE(
            a.total_balance,
            0
        ) AS balance,

        COALESCE(
            t.transaction_value,
            0
        ) AS transaction_value,

        COALESCE(
            l.loan_exposure,
            0
        ) AS loan_exposure

    FROM customers c

    LEFT JOIN (

        SELECT
            customer_id,
            SUM(balance) AS total_balance
        FROM accounts
        GROUP BY customer_id

    ) a

        ON c.customer_id = a.customer_id

    LEFT JOIN (

        SELECT
            customer_id,
            SUM(amount) AS transaction_value
        FROM transactions
        GROUP BY customer_id

    ) t

        ON c.customer_id = t.customer_id

    LEFT JOIN (

        SELECT
            customer_id,
            SUM(loan_amount) AS loan_exposure
        FROM loans
        WHERE status = 'Active'
        GROUP BY customer_id

    ) l

        ON c.customer_id = l.customer_id
)

SELECT

    customer_id,

    customer_code,

    segment,

    churned,

    ROUND(
        balance,
        2
    ) AS balance,

    ROUND(
        transaction_value,
        2
    ) AS transaction_value,

    ROUND(
        loan_exposure,
        2
    ) AS loan_exposure,

    ROUND(
        balance
        + transaction_value
        + loan_exposure,
        2
    ) AS total_customer_value,

    CASE

        WHEN (
            balance
            + transaction_value
            + loan_exposure
        ) >= 5000000

            THEN 'Very High Value'

        WHEN (
            balance
            + transaction_value
            + loan_exposure
        ) >= 2000000

            THEN 'High Value'

        WHEN (
            balance
            + transaction_value
            + loan_exposure
        ) >= 750000

            THEN 'Medium Value'

        ELSE 'Low Value'

    END AS value_segment

FROM customer_value

ORDER BY total_customer_value DESC;


-- ============================================================
-- 33. RETENTION PRIORITY SCORE
-- ============================================================

WITH customer_value AS (

    SELECT

        c.*,

        COALESCE(
            a.total_balance,
            0
        ) AS total_balance,

        COALESCE(
            t.transaction_value,
            0
        ) AS transaction_value,

        COALESCE(
            l.loan_exposure,
            0
        ) AS loan_exposure

    FROM customers c

    LEFT JOIN (

        SELECT

            customer_id,

            SUM(balance)
                AS total_balance

        FROM accounts

        GROUP BY customer_id

    ) a

        ON c.customer_id = a.customer_id

    LEFT JOIN (

        SELECT

            customer_id,

            SUM(amount)
                AS transaction_value

        FROM transactions

        GROUP BY customer_id

    ) t

        ON c.customer_id = t.customer_id

    LEFT JOIN (

        SELECT

            customer_id,

            SUM(loan_amount)
                AS loan_exposure

        FROM loans

        WHERE status = 'Active'

        GROUP BY customer_id

    ) l

        ON c.customer_id = l.customer_id
)

SELECT

    customer_id,

    customer_code,

    segment,

    annual_income,

    satisfaction_score,

    digital_engagement,

    complaint_count,

    product_count,

    tenure_years,

    churned,

    ROUND(
        total_balance,
        2
    ) AS total_balance,

    ROUND(
        transaction_value,
        2
    ) AS transaction_value,

    ROUND(
        loan_exposure,
        2
    ) AS loan_exposure,

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
            WHEN satisfaction_score = 3
                THEN 10
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
            WHEN complaint_count = 1
                THEN 7
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

    ) AS retention_priority_score

FROM customer_value

ORDER BY
    retention_priority_score DESC;


-- ============================================================
-- 34. HIGH-VALUE CHURNED CUSTOMERS
-- ============================================================

WITH customer_value AS (

    SELECT

        c.customer_id,

        c.customer_code,

        c.segment,

        c.churned,

        COALESCE(
            SUM(a.balance),
            0
        ) AS total_balance

    FROM customers c

    LEFT JOIN accounts a

        ON c.customer_id = a.customer_id

    GROUP BY

        c.customer_id,

        c.customer_code,

        c.segment,

        c.churned
)

SELECT *

FROM customer_value

WHERE churned = 1

ORDER BY total_balance DESC

LIMIT 100;


-- ============================================================
-- 35. FINAL MANAGEMENT VIEW
-- ============================================================

WITH customer_transactions AS (

    SELECT

        customer_id,

        COUNT(*) AS transaction_count,

        SUM(amount) AS transaction_value

    FROM transactions

    GROUP BY customer_id
),

customer_accounts AS (

    SELECT

        customer_id,

        SUM(balance) AS total_balance

    FROM accounts

    GROUP BY customer_id
),

customer_loans AS (

    SELECT

        customer_id,

        SUM(
            CASE
                WHEN status = 'Active'
                THEN loan_amount
                ELSE 0
            END
        ) AS active_loan_exposure

    FROM loans

    GROUP BY customer_id
),

customer_cards AS (

    SELECT

        customer_id,

        AVG(utilization_ratio)
            AS card_utilization

    FROM credit_cards

    GROUP BY customer_id
)

SELECT

    c.customer_id,

    c.customer_code,

    c.segment,

    c.city,

    c.age,

    c.annual_income,

    c.tenure_years,

    c.product_count,

    c.satisfaction_score,

    c.digital_engagement,

    c.complaint_count,

    c.credit_score,

    c.churned,

    COALESCE(
        ca.total_balance,
        0
    ) AS total_balance,

    COALESCE(
        ct.transaction_count,
        0
    ) AS transaction_count,

    COALESCE(
        ct.transaction_value,
        0
    ) AS transaction_value,

    COALESCE(
        cl.active_loan_exposure,
        0
    ) AS active_loan_exposure,

    COALESCE(
        cc.card_utilization,
        0
    ) AS card_utilization,

    (

        CASE
            WHEN c.churned = 1
                THEN 30
            ELSE 0
        END

        +

        CASE
            WHEN c.satisfaction_score <= 2
                THEN 20
            ELSE 0
        END

        +

        CASE
            WHEN c.digital_engagement < 0.35
                THEN 15
            ELSE 0
        END

        +

        CASE
            WHEN c.complaint_count >= 2
                THEN 15
            ELSE 0
        END

        +

        CASE
            WHEN c.product_count = 1
                THEN 10
            ELSE 0
        END

        +

        CASE
            WHEN c.tenure_years <= 1
                THEN 10
            ELSE 0
        END

    ) AS retention_priority_score

FROM customers c

LEFT JOIN customer_transactions ct
    ON c.customer_id = ct.customer_id

LEFT JOIN customer_accounts ca
    ON c.customer_id = ca.customer_id

LEFT JOIN customer_loans cl
    ON c.customer_id = cl.customer_id

LEFT JOIN customer_cards cc
    ON c.customer_id = cc.customer_id

ORDER BY
    retention_priority_score DESC;