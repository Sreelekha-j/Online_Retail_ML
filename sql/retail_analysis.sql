-- =====================================================================
-- retail_analysis.sql
-- Phase 8: SQL Analysis of the Online Retail II data
--
-- The tables "sales" and "customers" were loaded into the retail_db
-- database from Python (see Notebooks/07_sql_analysis.ipynb).
-- To run a query in MySQL Workbench: click inside it and press Ctrl+Enter.
-- =====================================================================

USE retail_db;


-- ---------------------------------------------------------------------
-- Setup and checks
-- ---------------------------------------------------------------------

-- Check that all the rows were loaded (expected: 776,594 and 5,852)
SELECT COUNT(*) AS sales_rows FROM sales;
SELECT COUNT(*) AS customer_rows FROM customers;

-- Index on CustomerID, so the JOIN in Q6 runs faster (run only once)
-- ALTER TABLE sales ADD INDEX idx_customer (CustomerID);


-- ---------------------------------------------------------------------
-- Q1. KPI numbers
-- Expected: 36,592 orders, 5,852 customers, about 16,822,930 revenue
-- ---------------------------------------------------------------------
SELECT COUNT(DISTINCT Invoice)    AS orders,
       COUNT(DISTINCT CustomerID) AS customers,
       ROUND(SUM(Revenue), 0)     AS revenue
FROM sales;


-- ---------------------------------------------------------------------
-- Q2. Revenue by month
-- Revenue goes up every year from September to November.
-- ---------------------------------------------------------------------
SELECT DATE_FORMAT(InvoiceDate, '%Y-%m') AS month,
       COUNT(DISTINCT Invoice)           AS orders,
       ROUND(SUM(Revenue), 0)            AS revenue
FROM sales
GROUP BY month
ORDER BY month;


-- ---------------------------------------------------------------------
-- Q3. Top 10 countries by revenue
-- The UK has 91% of customers and about 83% of revenue.
-- ---------------------------------------------------------------------
SELECT Country,
       COUNT(DISTINCT CustomerID) AS customers,
       ROUND(SUM(Revenue), 0)     AS revenue
FROM sales
GROUP BY Country
ORDER BY revenue DESC
LIMIT 10;


-- ---------------------------------------------------------------------
-- Q4. Revenue by day of the week
-- Thursday is the best day, and Saturday has almost no sales.
-- ---------------------------------------------------------------------
SELECT DAYNAME(InvoiceDate)   AS day,
       ROUND(SUM(Revenue), 0) AS revenue
FROM sales
GROUP BY DAYOFWEEK(InvoiceDate), day
ORDER BY DAYOFWEEK(InvoiceDate);


-- ---------------------------------------------------------------------
-- Q5. RFM calculated in SQL (top 10 customers by spend)
-- Recency = days between 10 Dec 2011 and the customer's last order
-- ---------------------------------------------------------------------
SELECT CustomerID,
       DATEDIFF('2011-12-10', MAX(InvoiceDate)) AS Recency,
       COUNT(DISTINCT Invoice)                  AS Frequency,
       ROUND(SUM(Revenue), 2)                   AS Monetary
FROM sales
GROUP BY CustomerID
ORDER BY Monetary DESC
LIMIT 10;

-- Check: the same customer in my customers table (RFM made with pandas)
SELECT CustomerID, Recency, Frequency, Monetary
FROM customers
WHERE CustomerID = 18102;

-- Check for all customers: SQL RFM vs pandas RFM (expected: 0 mismatches)
SELECT COUNT(*)                                  AS customers_checked,
       SUM(r.Frequency <> c.Frequency)           AS frequency_mismatches,
       SUM(ABS(r.Monetary - c.Monetary) > 0.01)  AS monetary_mismatches,
       SUM(ABS(r.Recency - c.Recency) > 1)       AS recency_mismatches
FROM (
    SELECT CustomerID,
           DATEDIFF('2011-12-10', MAX(InvoiceDate)) AS Recency,
           COUNT(DISTINCT Invoice)                  AS Frequency,
           SUM(Revenue)                             AS Monetary
    FROM sales
    GROUP BY CustomerID
) r
JOIN customers c ON r.CustomerID = c.CustomerID;


-- ---------------------------------------------------------------------
-- Q6. Revenue per customer group (JOIN)
-- Same as Phase 3: Champions bring 73.5% of revenue.
-- ---------------------------------------------------------------------
SELECT c.ClusterName,
       COUNT(DISTINCT s.CustomerID) AS customers,
       ROUND(SUM(s.Revenue), 0)     AS revenue,
       ROUND(SUM(s.Revenue) * 100 / (SELECT SUM(Revenue) FROM sales), 1) AS revenue_share
FROM sales s
JOIN customers c ON s.CustomerID = c.CustomerID
GROUP BY c.ClusterName
ORDER BY revenue DESC;


-- ---------------------------------------------------------------------
-- Q7. Best customer in each country (window function)
-- RANK() ranks customers inside each country; rnk = 1 keeps the best one.
-- ---------------------------------------------------------------------
SELECT Country, CustomerID, revenue
FROM (
    SELECT Country, CustomerID,
           ROUND(SUM(Revenue), 0) AS revenue,
           RANK() OVER (PARTITION BY Country ORDER BY SUM(Revenue) DESC) AS rnk
    FROM sales
    GROUP BY Country, CustomerID
) ranked
WHERE rnk = 1
ORDER BY revenue DESC
LIMIT 10;


-- ---------------------------------------------------------------------
-- Q8. How many customers bought more than once?
-- Result: 72.3% of customers bought more than once.
-- ---------------------------------------------------------------------
SELECT ROUND(SUM(orders > 1) * 100 / COUNT(*), 1) AS repeat_customer_pct
FROM (
    SELECT CustomerID, COUNT(DISTINCT Invoice) AS orders
    FROM sales
    GROUP BY CustomerID
) per_customer;
