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
    FROM close_tasks AS t
    LEFT JOIN close_exceptions AS e
    ON t.task_id = e.task_id
    LEFT JOIN entities AS n
    ON t.entity_id = n.entity_id
    GROUP BY t.task_id
),
--task level
task_final_summary AS(
    SELECT task_id, entity_id, task_status, priority_level,
    entity_name, region, business_unit,
    task_delay_days, overdue_task_flag, approval_delay_flag, unresolved_exception_count,
    CASE
        WHEN overdue_task_flag = 'Yes' OR
        approval_delay_flag = 'Yes' OR
        unresolved_exception_count >= 1 OR
        highest_exception_severity = 'High'
        THEN 'Yes'
        ELSE 'No'
    END AS priority_review_flag
    FROM task_summary
),

--entity level
entity_summary AS (
    SELECT entity_id,
    SUM(CASE
        WHEN overdue_task_flag = 'Yes' THEN 1
        ELSE 0
    END) AS overdue_task_count,
    SUM(unresolved_exception_count) AS unresolved_exception_count,
    SUM(CASE
        WHEN approval_delay_flag = 'Yes' THEN 1
        ELSE 0
    END) AS delayed_approval_count,
    CASE 
        WHEN SUM(CASE
            WHEN overdue_task_flag = 'Yes' THEN 1
            ELSE 0
        END) >= 3 OR
        SUM(unresolved_exception_count) >= 2 OR
        SUM(CASE
            WHEN approval_delay_flag = 'Yes' THEN 1
            ELSE 0
        END) >= 2
        THEN 'High Risk'
        WHEN SUM(CASE
            WHEN overdue_task_flag = 'Yes' THEN 1
            ELSE 0
        END) >= 1 OR
        SUM(unresolved_exception_count) >= 1
        THEN 'Medium Risk'
        ELSE 'Low Risk'
    END AS entity_risk_flag
    FROM task_final_summary
    GROUP BY entity_id
),

-- manager level
manager_summary AS(
    SELECT COUNT(task_id) AS total_task_count,
    SUM(CASE
        WHEN task_status = 'Completed' THEN 1
        ELSE 0
    END) AS completed_task_count,
    SUM(CASE
        WHEN task_status != 'Completed' THEN 1
        ELSE 0
    END) AS open_task_count,
    SUM(CASE
        WHEN overdue_task_flag = 'Yes' THEN 1
        ELSE 0
    END) AS overdue_task_count,
    ROUND(CAST(SUM(CASE
        WHEN overdue_task_flag = 'Yes' THEN 1
        ELSE 0
    END) AS REAL) / COUNT(task_id),3) AS overdue_task_ratio,
    SUM(unresolved_exception_count) AS unresolved_exception_count,
    SUM(CASE 
        WHEN approval_delay_flag = 'Yes' Then 1
        ELSE 0
    END) AS delayed_approval_count,
    ( 
        SELECT COUNT(*)
        FROM entity_summary
        WHERE entity_risk_flag = 'High Risk'
    ) AS high_risk_entity_count,
    ROUND(AVG(task_delay_days),3) AS avg_task_delay_days,
    SUM(CASE
        WHEN overdue_task_flag = 'Yes' OR
        approval_delay_flag = 'Yes' OR
        unresolved_exception_count >= 1
        THEN 1
        ELSE 0
    END) AS priority_review_task_count 
    FROM task_final_summary
)
SELECT total_task_count,
completed_task_count,
open_task_count,
overdue_task_count,
overdue_task_ratio,
unresolved_exception_count,
delayed_approval_count,
high_risk_entity_count,
avg_task_delay_days,
priority_review_task_count
FROM manager_summary