-- ============================================================================
-- Day 06: Financial Consulting Metrics Layer
-- ============================================================================
-- This SQL file creates views for key consulting metrics:
-- 1. Utilization Rate: % of billable hours vs total hours
-- 2. Project Profitability: Revenue minus costs per project
-- 3. Client ROI: Value delivered vs client investment
-- 4. Burn Rate: Spending rate vs billing rate
--
-- Uses CTEs and window functions for clear, maintainable logic
-- ============================================================================

-- ============================================================================
-- METRIC 1: Consultant Utilization Rate
-- ============================================================================
-- Business Logic: High-performing consultants should have 70-85% billable hours
-- Formula: (Billable Hours / Total Hours) * 100
-- ============================================================================

CREATE VIEW IF NOT EXISTS day06_utilization_rate AS
WITH day06_consultant_hours AS (
    -- Aggregate hours by consultant
    SELECT
        consultant_id,
        SUM(hours_worked) as total_hours,
        SUM(CASE WHEN is_billable = 1 THEN hours_worked ELSE 0 END) as billable_hours,
        COUNT(DISTINCT date) as days_worked,
        COUNT(DISTINCT project_id) as projects_worked
    FROM day06_timesheets
    GROUP BY consultant_id
),
day06_utilization_calc AS (
    -- Calculate utilization rate and categorize
    SELECT
        consultant_id,
        total_hours,
        billable_hours,
        days_worked,
        projects_worked,
        ROUND((billable_hours * 100.0) / NULLIF(total_hours, 0), 2) as utilization_rate,
        ROUND(total_hours / NULLIF(days_worked, 0), 2) as avg_hours_per_day
    FROM day06_consultant_hours
)
SELECT
    consultant_id,
    total_hours,
    billable_hours,
    days_worked,
    projects_worked,
    utilization_rate,
    avg_hours_per_day,
    -- Categorize performance
    CASE
        WHEN utilization_rate >= 80 THEN 'High Performer'
        WHEN utilization_rate >= 60 THEN 'Average'
        ELSE 'Below Target'
    END as performance_category,
    -- Rank consultants by utilization
    RANK() OVER (ORDER BY utilization_rate DESC) as utilization_rank
FROM day06_utilization_calc
ORDER BY utilization_rate DESC;

-- ============================================================================
-- METRIC 2: Project Profitability
-- ============================================================================
-- Business Logic: Revenue (billable hours * rates) - Costs (expenses + non-billable hours)
-- Identifies most/least profitable projects for resource allocation decisions
-- ============================================================================

CREATE VIEW IF NOT EXISTS day06_project_profitability AS
WITH day06_project_revenue AS (
    -- Calculate revenue from billable hours
    SELECT
        t.project_id,
        SUM(CASE WHEN t.is_billable = 1
            THEN t.hours_worked * t.hourly_rate_usd
            ELSE 0
        END) as billable_revenue,
        SUM(t.hours_worked) as total_hours,
        SUM(CASE WHEN t.is_billable = 1 THEN t.hours_worked ELSE 0 END) as billable_hours
    FROM day06_timesheets t
    GROUP BY t.project_id
),
day06_project_costs AS (
    -- Calculate costs: expenses + cost of non-billable hours
    SELECT
        t.project_id,
        COALESCE(SUM(e.amount_usd), 0) as total_expenses,
        SUM(CASE WHEN t.is_billable = 0
            THEN t.hours_worked * t.hourly_rate_usd
            ELSE 0
        END) as non_billable_cost
    FROM day06_timesheets t
    LEFT JOIN day06_expenses e ON t.project_id = e.project_id
    GROUP BY t.project_id
),
day06_profitability_calc AS (
    -- Calculate profitability metrics
    SELECT
        p.project_id,
        p.project_name,
        p.client_id,
        p.budget_usd,
        p.contract_type,
        p.status,
        r.billable_revenue,
        c.total_expenses,
        c.non_billable_cost,
        r.total_hours,
        r.billable_hours,
        -- Total cost = expenses + non-billable time cost
        (c.total_expenses + c.non_billable_cost) as total_cost,
        -- Profit = revenue - costs
        (r.billable_revenue - (c.total_expenses + c.non_billable_cost)) as profit,
        -- Margin = (profit / revenue) * 100
        ROUND(((r.billable_revenue - (c.total_expenses + c.non_billable_cost)) * 100.0)
            / NULLIF(r.billable_revenue, 0), 2) as profit_margin_pct
    FROM day06_projects p
    LEFT JOIN day06_project_revenue r ON p.project_id = r.project_id
    LEFT JOIN day06_project_costs c ON p.project_id = c.project_id
)
SELECT
    project_id,
    project_name,
    client_id,
    budget_usd,
    contract_type,
    status,
    billable_revenue,
    total_expenses,
    non_billable_cost,
    total_cost,
    profit,
    profit_margin_pct,
    total_hours,
    billable_hours,
    -- Categorize profitability
    CASE
        WHEN profit_margin_pct >= 30 THEN 'High Margin'
        WHEN profit_margin_pct >= 15 THEN 'Healthy'
        WHEN profit_margin_pct >= 0 THEN 'Break-even'
        ELSE 'Loss-making'
    END as profitability_category,
    -- Rank by profit
    RANK() OVER (ORDER BY profit DESC) as profit_rank,
    -- Calculate budget utilization
    ROUND((billable_revenue * 100.0) / NULLIF(budget_usd, 0), 2) as budget_utilization_pct
FROM day06_profitability_calc
ORDER BY profit DESC;

-- ============================================================================
-- METRIC 3: Client ROI
-- ============================================================================
-- Business Logic: For each client, calculate total value delivered vs investment
-- ROI = (Value Delivered - Investment) / Investment * 100
-- Higher ROI = better client relationship and pricing power
-- ============================================================================

CREATE VIEW IF NOT EXISTS day06_client_roi AS
WITH day06_client_projects AS (
    -- Aggregate all projects per client
    SELECT
        p.client_id,
        COUNT(DISTINCT p.project_id) as total_projects,
        SUM(p.budget_usd) as total_client_investment,
        SUM(prof.billable_revenue) as total_value_delivered,
        SUM(prof.total_cost) as total_costs,
        SUM(prof.profit) as total_profit,
        AVG(prof.profit_margin_pct) as avg_profit_margin,
        -- Calculate time span
        MIN(p.start_date) as first_project_date,
        MAX(p.end_date) as last_project_date
    FROM day06_projects p
    LEFT JOIN day06_project_profitability prof ON p.project_id = prof.project_id
    GROUP BY p.client_id
),
day06_roi_calc AS (
    SELECT
        client_id,
        total_projects,
        total_client_investment,
        total_value_delivered,
        total_costs,
        total_profit,
        avg_profit_margin,
        first_project_date,
        last_project_date,
        -- Calculate client ROI (from client's perspective)
        ROUND(((total_value_delivered - total_client_investment) * 100.0)
            / NULLIF(total_client_investment, 0), 2) as client_roi_pct,
        -- Calculate our ROI (from consulting firm's perspective)
        ROUND((total_profit * 100.0) / NULLIF(total_costs, 0), 2) as firm_roi_pct,
        -- Calculate relationship duration in days
        CAST((JULIANDAY(last_project_date) - JULIANDAY(first_project_date)) AS INTEGER) as relationship_days
    FROM day06_client_projects
)
SELECT
    client_id,
    total_projects,
    total_client_investment,
    total_value_delivered,
    total_costs,
    total_profit,
    avg_profit_margin,
    client_roi_pct,
    firm_roi_pct,
    relationship_days,
    ROUND(relationship_days / 30.0, 1) as relationship_months,
    -- Revenue per project
    ROUND(total_value_delivered / NULLIF(total_projects, 0), 2) as avg_revenue_per_project,
    -- Categorize client value
    CASE
        WHEN client_roi_pct >= 200 THEN 'Strategic Partner'
        WHEN client_roi_pct >= 100 THEN 'High Value'
        WHEN client_roi_pct >= 50 THEN 'Standard'
        ELSE 'Needs Attention'
    END as client_value_tier,
    -- Rank clients by ROI
    RANK() OVER (ORDER BY client_roi_pct DESC) as roi_rank,
    -- Rank by total profit contribution
    RANK() OVER (ORDER BY total_profit DESC) as profit_contribution_rank
FROM day06_roi_calc
ORDER BY client_roi_pct DESC;

-- ============================================================================
-- METRIC 4: Burn Rate Analysis
-- ============================================================================
-- Business Logic: Track spending rate vs billing rate over time
-- Helps identify cash flow issues and project timeline risks
-- Monthly burn rate = expenses + labor costs per month
-- ============================================================================

CREATE VIEW IF NOT EXISTS day06_burn_rate AS
WITH day06_monthly_timesheets AS (
    -- Aggregate timesheet costs by project and month
    SELECT
        project_id,
        strftime('%Y-%m', date) as month,
        SUM(hours_worked * hourly_rate_usd) as labor_cost,
        SUM(CASE WHEN is_billable = 1 THEN hours_worked * hourly_rate_usd ELSE 0 END) as billable_revenue,
        SUM(hours_worked) as hours_worked
    FROM day06_timesheets
    GROUP BY project_id, strftime('%Y-%m', date)
),
day06_monthly_expenses AS (
    -- Aggregate expenses by project and month
    SELECT
        project_id,
        strftime('%Y-%m', expense_date) as month,
        SUM(amount_usd) as expenses
    FROM day06_expenses
    GROUP BY project_id, strftime('%Y-%m', expense_date)
),
day06_monthly_burn AS (
    -- Combine costs and revenue by month
    SELECT
        COALESCE(t.project_id, e.project_id) as project_id,
        COALESCE(t.month, e.month) as month,
        COALESCE(t.labor_cost, 0) as labor_cost,
        COALESCE(e.expenses, 0) as expenses,
        COALESCE(t.billable_revenue, 0) as billable_revenue,
        COALESCE(t.hours_worked, 0) as hours_worked,
        -- Total burn = labor + expenses
        (COALESCE(t.labor_cost, 0) + COALESCE(e.expenses, 0)) as total_burn,
        -- Net cash flow = revenue - burn
        (COALESCE(t.billable_revenue, 0) - (COALESCE(t.labor_cost, 0) + COALESCE(e.expenses, 0))) as net_cash_flow
    FROM day06_monthly_timesheets t
    FULL OUTER JOIN day06_monthly_expenses e
        ON t.project_id = e.project_id AND t.month = e.month
),
day06_burn_with_cumulative AS (
    SELECT
        b.project_id,
        p.project_name,
        p.client_id,
        b.month,
        b.labor_cost,
        b.expenses,
        b.total_burn,
        b.billable_revenue,
        b.net_cash_flow,
        b.hours_worked,
        -- Running totals using window function
        SUM(b.total_burn) OVER (
            PARTITION BY b.project_id
            ORDER BY b.month
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) as cumulative_burn,
        SUM(b.billable_revenue) OVER (
            PARTITION BY b.project_id
            ORDER BY b.month
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) as cumulative_revenue,
        SUM(b.net_cash_flow) OVER (
            PARTITION BY b.project_id
            ORDER BY b.month
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) as cumulative_cash_flow,
        -- Compare to previous month using LAG
        LAG(b.total_burn) OVER (
            PARTITION BY b.project_id
            ORDER BY b.month
        ) as previous_month_burn,
        -- Budget tracking
        p.budget_usd
    FROM day06_monthly_burn b
    JOIN day06_projects p ON b.project_id = p.project_id
)
SELECT
    project_id,
    project_name,
    client_id,
    month,
    labor_cost,
    expenses,
    total_burn,
    billable_revenue,
    net_cash_flow,
    hours_worked,
    cumulative_burn,
    cumulative_revenue,
    cumulative_cash_flow,
    previous_month_burn,
    budget_usd,
    -- Budget burn rate
    ROUND((cumulative_burn * 100.0) / NULLIF(budget_usd, 0), 2) as budget_burn_pct,
    -- Month-over-month burn change
    ROUND(((total_burn - previous_month_burn) * 100.0) / NULLIF(previous_month_burn, 0), 2) as burn_change_pct,
    -- Cash flow status
    CASE
        WHEN net_cash_flow > 0 THEN 'Cash Positive'
        WHEN net_cash_flow = 0 THEN 'Break-even'
        ELSE 'Burning Cash'
    END as cash_flow_status,
    -- Budget alert
    CASE
        WHEN (cumulative_burn * 100.0) / NULLIF(budget_usd, 0) >= 90 THEN 'CRITICAL: >90% budget used'
        WHEN (cumulative_burn * 100.0) / NULLIF(budget_usd, 0) >= 75 THEN 'WARNING: >75% budget used'
        WHEN (cumulative_burn * 100.0) / NULLIF(budget_usd, 0) >= 50 THEN 'WATCH: >50% budget used'
        ELSE 'On Track'
    END as budget_alert
FROM day06_burn_with_cumulative
ORDER BY project_id, month;

-- ============================================================================
-- SUMMARY VIEW: Executive Dashboard
-- ============================================================================
-- Combines key metrics for executive-level overview
-- ============================================================================

CREATE VIEW IF NOT EXISTS day06_executive_summary AS
SELECT
    'Portfolio Overview' as metric_category,
    'Total Projects' as metric_name,
    COUNT(DISTINCT project_id) as metric_value,
    NULL as metric_unit
FROM day06_projects

UNION ALL

SELECT
    'Portfolio Overview',
    'Total Active Projects',
    COUNT(DISTINCT project_id),
    NULL
FROM day06_projects
WHERE status = 'Active'

UNION ALL

SELECT
    'Financial Performance',
    'Total Revenue',
    ROUND(SUM(billable_revenue), 2),
    'USD'
FROM day06_project_profitability

UNION ALL

SELECT
    'Financial Performance',
    'Total Profit',
    ROUND(SUM(profit), 2),
    'USD'
FROM day06_project_profitability

UNION ALL

SELECT
    'Financial Performance',
    'Average Profit Margin',
    ROUND(AVG(profit_margin_pct), 2),
    '%'
FROM day06_project_profitability

UNION ALL

SELECT
    'Team Performance',
    'Average Utilization Rate',
    ROUND(AVG(utilization_rate), 2),
    '%'
FROM day06_utilization_rate

UNION ALL

SELECT
    'Client Metrics',
    'Total Active Clients',
    COUNT(DISTINCT client_id),
    NULL
FROM day06_client_roi

UNION ALL

SELECT
    'Client Metrics',
    'Average Client ROI',
    ROUND(AVG(client_roi_pct), 2),
    '%'
FROM day06_client_roi;
