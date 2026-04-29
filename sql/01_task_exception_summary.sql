-- task level
WITH exception_summary AS (
    SELECT task_id, 
    SUM(CASE
        WHEN exception_status = 'Open' THEN 1
        ELSE 0
    END) AS unresolved_exception_count,
    CASE
        WHEN
        MAX(CASE
            WHEN exception_status = 'Open' AND exception_severity = 'High' THEN 3
            WHEN exception_status = 'Open' AND exception_severity = 'Medium' THEN 2
            WHEN exception_status = 'Open' AND exception_severity = 'Low' THEN 1
            ELSE 0
        END) = 3 THEN 'High'
        WHEN
        MAX(CASE
            WHEN exception_status = 'Open' AND exception_severity = 'High' THEN 3
            WHEN exception_status = 'Open' AND exception_severity = 'Medium' THEN 2
            WHEN exception_status = 'Open' AND exception_severity = 'Low' THEN 1
            ELSE 0
        END) = 2 THEN 'Medium'
        WHEN
        MAX(CASE
            WHEN exception_status = 'Open' AND exception_severity = 'High' THEN 3
            WHEN exception_status = 'Open' AND exception_severity = 'Medium' THEN 2
            WHEN exception_status = 'Open' AND exception_severity = 'Low' THEN 1
            ELSE 0
        END) = 1 THEN 'Low'
        ELSE 'None'
    END AS highest_exception_severity
    FROM close_exceptions
    GROUP BY task_id
),
-- task level
task_base AS (
    SELECT c.task_id, c.task_name, c.task_category, c.scheduled_close_date, c.actual_close_date,
    c.task_status, c.requires_approval, c.approval_status, c.approval_due_date, c.approval_completed_date,
    c.entity_id, c.owner_id,
    e.entity_name, e.region, e.business_unit,
    t.owner_name, t.team_name,
    CASE 
        WHEN c.task_status = 'Completed' 
        THEN julianday(c.actual_close_date) - julianday(c.scheduled_close_date)
        ELSE julianday('2026-04-15') - julianday(c.scheduled_close_date)
    END AS task_delay_days,
    CASE
        WHEN (c.actual_close_date IS NULL AND c.scheduled_close_date < '2026-04-15') OR
        c.actual_close_date > c.scheduled_close_date
        THEN 'Yes'
        ELSE 'No'
    END AS overdue_task_flag,
    CASE
        WHEN c.requires_approval = 'Yes' AND(
        (c.approval_status = 'Pending' AND c.approval_due_date < '2026-04-15') OR
        c.approval_completed_date > c.approval_due_date) THEN 'Yes'
        ELSE 'No'
    END AS approval_delay_flag
    FROM close_tasks AS c
    LEFT JOIN entities AS e
    ON c.entity_id = e.entity_id
    LEFT JOIN task_owners AS t
    ON c.owner_id = t.owner_id
),
final_summary AS(
    SELECT
    t.task_id,
    entity_name,
    region,
    business_unit,
    task_name,
    task_category,
    owner_name,
    team_name,
    scheduled_close_date,
    actual_close_date,
    task_status,
    task_delay_days,
    overdue_task_flag,
    requires_approval,
    approval_status,
    approval_delay_flag,
    COALESCE(unresolved_exception_count,0) AS unresolved_exception_count,
    COALESCE(highest_exception_severity,'None') AS highest_exception_severity,

    CASE
        WHEN overdue_task_flag = 'Yes' OR
        approval_delay_flag = 'Yes' OR
        unresolved_exception_count >= 1 OR
        highest_exception_severity = 'High'
        THEN 'Yes'
        ELSE 'No'
    END AS priority_review_flag
    FROM task_base AS t
    LEFT JOIN exception_summary AS e
    ON t.task_id = e.task_id
)
SELECT task_id,
entity_name,
region,
business_unit,
task_name,
task_category,
owner_name,
team_name,
scheduled_close_date,
actual_close_date,
task_status,
task_delay_days,
overdue_task_flag,
requires_approval,
approval_status,
approval_delay_flag,
unresolved_exception_count,
highest_exception_severity,
priority_review_flag
FROM final_summary
ORDER BY priority_review_flag DESC, task_delay_days DESC, entity_name ASC, task_id ASC