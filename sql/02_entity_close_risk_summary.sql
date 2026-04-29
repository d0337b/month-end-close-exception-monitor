-- task level
WITH task_summary AS(
    SELECT t.task_id, t.entity_id, t.task_status, t.priority_level,
    n.entity_name, n.region, n.business_unit,

    CASE 
        WHEN t.task_status = 'Completed' 
        THEN julianday(t.actual_close_date) - julianday(t.scheduled_close_date)
        ELSE julianday('2026-04-15') - julianday(t.scheduled_close_date)
    END AS task_delay_days,
    CASE
        WHEN (t.actual_close_date IS NULL AND t.scheduled_close_date < '2026-04-15') OR
        t.actual_close_date > t.scheduled_close_date
        THEN 'Yes'
        ELSE 'No'
    END AS overdue_task_flag,
    CASE
        WHEN t.requires_approval = 'Yes' AND(
        (t.approval_status = 'Pending' AND t.approval_due_date < '2026-04-15') OR
        t.approval_completed_date > t.approval_due_date) THEN 'Yes'
        ELSE 'No'
    END AS approval_delay_flag,
    SUM(CASE
        WHEN e.exception_status = 'Open' THEN 1
        ELSE 0
    END) AS unresolved_exception_count
    FROM close_tasks AS t
    LEFT JOIN close_exceptions AS e
    ON t.task_id = e.task_id
    LEFT JOIN entities AS n
    ON t.entity_id = n.entity_id
    GROUP BY t.task_id
),

--entity level
final_summary AS (
    SELECT entity_name, region, business_unit, 
    COUNT(*) AS total_task_count,
    SUM(CASE
        WHEN task_status = 'Completed' THEN 1
        ELSE 0
    END) AS completed_task_count,
    SUM(CASE
        WHEN overdue_task_flag = 'Yes' THEN 1
        ELSE 0
    END) AS overdue_task_count,
    SUM(unresolved_exception_count) AS unresolved_exception_count,
    SUM(CASE
        WHEN approval_delay_flag = 'Yes' THEN 1
        ELSE 0
    END) AS delayed_approval_count,
    SUM(CASE
        WHEN priority_level = 'High' THEN 1
        ELSE 0
    END) AS high_priority_task_count,
    ROUND(AVG(task_delay_days),3) AS avg_task_delay_days
    FROM task_summary
    GROUP BY entity_name, region, business_unit
)
SELECT entity_name,
region,
business_unit,
total_task_count,
completed_task_count,
overdue_task_count,
unresolved_exception_count,
delayed_approval_count,
avg_task_delay_days,
high_priority_task_count,
CASE 
    WHEN overdue_task_count >= 3 OR
    unresolved_exception_count >= 2 OR
    delayed_approval_count >= 2
    THEN 'High Risk'
    WHEN overdue_task_count >= 1 OR
    unresolved_exception_count >= 1
    THEN 'Medium Risk'
    ELSE 'Low Risk'
END AS entity_risk_flag
FROM final_summary
ORDER BY
    CASE
        WHEN entity_risk_flag = 'High Risk' THEN 3
        WHEN entity_risk_flag = 'Medium Risk' THEN 2
        ELSE 1
    END DESC,
    overdue_task_count DESC,
    entity_name ASC;