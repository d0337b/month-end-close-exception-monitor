import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import random

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "practice.db"

random.seed(42)


def to_date_str(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")


def create_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def drop_tables(cur: sqlite3.Cursor) -> None:
    cur.executescript(
        """
        DROP TABLE IF EXISTS close_exceptions;
        DROP TABLE IF EXISTS close_tasks;
        DROP TABLE IF EXISTS task_owners;
        DROP TABLE IF EXISTS entities;
        """
    )


def create_tables(cur: sqlite3.Cursor) -> None:
    cur.executescript(
        """
        CREATE TABLE entities (
            entity_id INTEGER PRIMARY KEY,
            entity_name TEXT NOT NULL,
            region TEXT NOT NULL,
            business_unit TEXT NOT NULL,
            entity_priority TEXT NOT NULL
        );

        CREATE TABLE task_owners (
            owner_id INTEGER PRIMARY KEY,
            owner_name TEXT NOT NULL,
            team_name TEXT NOT NULL,
            manager_name TEXT NOT NULL
        );

        CREATE TABLE close_tasks (
            task_id INTEGER PRIMARY KEY,
            entity_id INTEGER NOT NULL,
            task_name TEXT NOT NULL,
            task_category TEXT NOT NULL,
            owner_id INTEGER NOT NULL,
            scheduled_close_date TEXT NOT NULL,
            actual_close_date TEXT,
            task_status TEXT NOT NULL,
            requires_approval TEXT NOT NULL,
            approval_due_date TEXT,
            approval_completed_date TEXT,
            approval_status TEXT NOT NULL,
            priority_level TEXT NOT NULL,
            FOREIGN KEY (entity_id) REFERENCES entities(entity_id),
            FOREIGN KEY (owner_id) REFERENCES task_owners(owner_id)
        );

        CREATE TABLE close_exceptions (
            exception_id INTEGER PRIMARY KEY,
            task_id INTEGER NOT NULL,
            exception_type TEXT NOT NULL,
            exception_severity TEXT NOT NULL,
            identified_date TEXT NOT NULL,
            resolved_date TEXT,
            exception_status TEXT NOT NULL,
            root_cause TEXT NOT NULL,
            FOREIGN KEY (task_id) REFERENCES close_tasks(task_id)
        );
        """
    )


def insert_entities(cur: sqlite3.Cursor) -> None:
    entities = [
        (1, "Korea HQ", "APAC", "Consumer", "High"),
        (2, "Japan Subsidiary", "APAC", "Enterprise", "Medium"),
        (3, "Singapore Services", "APAC", "Platform", "Medium"),
        (4, "US West Entity", "North America", "Platform", "High"),
        (5, "US East Entity", "North America", "Consumer", "High"),
        (6, "Germany GmbH", "Europe", "Enterprise", "Medium"),
        (7, "UK Services", "Europe", "Platform", "Low"),
        (8, "Australia Branch", "APAC", "Consumer", "Low"),
    ]
    cur.executemany(
        """
        INSERT INTO entities (
            entity_id, entity_name, region, business_unit, entity_priority
        ) VALUES (?, ?, ?, ?, ?)
        """,
        entities,
    )


def insert_task_owners(cur: sqlite3.Cursor) -> None:
    owners = [
        (101, "Minji Kim", "Close Ops", "Daniel Park"),
        (102, "Jisoo Lee", "Financial Reporting", "Daniel Park"),
        (103, "Hyunwoo Choi", "Controllership", "Sarah Han"),
        (104, "Soojin Park", "Intercompany", "Sarah Han"),
        (105, "Yuna Jung", "Reconciliation", "Chris Yoo"),
        (106, "Jihoon Seo", "Close Ops", "Chris Yoo"),
        (107, "Hyejin Kwon", "Financial Reporting", "Mina Lim"),
        (108, "Donghyun Ahn", "Controllership", "Mina Lim"),
    ]
    cur.executemany(
        """
        INSERT INTO task_owners (
            owner_id, owner_name, team_name, manager_name
        ) VALUES (?, ?, ?, ?)
        """,
        owners,
    )


def generate_close_tasks() -> list[tuple]:
    categories = [
        ("Journal Entry Review", "Journal Entry"),
        ("Account Reconciliation", "Reconciliation"),
        ("Accrual Validation", "Accrual Review"),
        ("Intercompany Tie-out", "Intercompany"),
        ("Financial Statement Draft", "Financial Reporting"),
        ("Variance Analysis Review", "Variance Analysis"),
    ]

    tasks = []
    task_id = 1001

    # reporting month close cycle example
    # scheduled dates mostly around Apr 1 ~ Apr 8
    base_date = datetime(2026, 4, 1)

    for entity_id in range(1, 9):
        for idx, (task_name, task_category) in enumerate(categories):
            owner_id = 101 + ((entity_id + idx - 1) % 8)

            scheduled_close_date = base_date + timedelta(days=idx)

            # entity-based pattern to create visible risk clusters
            # entity 1, 4, 5 intentionally riskier
            if entity_id in {1, 4, 5}:
                if idx in {0, 1, 3}:
                    # overdue / incomplete
                    actual_close_date = None
                    task_status = "In Progress" if idx != 3 else "Not Started"
                elif idx == 4:
                    # completed late
                    actual_close_date = scheduled_close_date + timedelta(days=3)
                    task_status = "Completed"
                else:
                    actual_close_date = scheduled_close_date
                    task_status = "Completed"
            elif entity_id in {2, 6}:
                if idx in {1, 2}:
                    actual_close_date = scheduled_close_date + timedelta(days=1)
                    task_status = "Completed"
                elif idx == 5:
                    actual_close_date = None
                    task_status = "In Progress"
                else:
                    actual_close_date = scheduled_close_date
                    task_status = "Completed"
            else:
                if idx == 2 and entity_id == 3:
                    actual_close_date = scheduled_close_date + timedelta(days=2)
                    task_status = "Completed"
                elif idx == 4 and entity_id == 7:
                    actual_close_date = None
                    task_status = "In Progress"
                else:
                    actual_close_date = scheduled_close_date
                    task_status = "Completed"

            requires_approval = "Yes" if idx in {0, 1, 4} else "No"

            if requires_approval == "Yes":
                approval_due_date = scheduled_close_date + timedelta(days=1)

                if task_status == "Completed" and actual_close_date is not None:
                    # approval can be on time or late
                    if entity_id in {1, 4, 5} and idx in {0, 4}:
                        approval_completed_date = approval_due_date + timedelta(days=2)
                        approval_status = "Approved"
                    else:
                        approval_completed_date = approval_due_date
                        approval_status = "Approved"
                else:
                    approval_completed_date = None
                    approval_status = "Pending"
            else:
                approval_due_date = None
                approval_completed_date = None
                approval_status = "Not Required"

            if entity_id in {1, 4, 5} and idx in {0, 1, 4}:
                priority_level = "High"
            elif idx in {1, 4}:
                priority_level = "Medium"
            else:
                priority_level = "Low"

            tasks.append(
                (
                    task_id,
                    entity_id,
                    task_name,
                    task_category,
                    owner_id,
                    to_date_str(scheduled_close_date),
                    to_date_str(actual_close_date) if actual_close_date else None,
                    task_status,
                    requires_approval,
                    to_date_str(approval_due_date) if approval_due_date else None,
                    to_date_str(approval_completed_date) if approval_completed_date else None,
                    approval_status,
                    priority_level,
                )
            )
            task_id += 1

    return tasks


def insert_close_tasks(cur: sqlite3.Cursor, tasks: list[tuple]) -> None:
    cur.executemany(
        """
        INSERT INTO close_tasks (
            task_id,
            entity_id,
            task_name,
            task_category,
            owner_id,
            scheduled_close_date,
            actual_close_date,
            task_status,
            requires_approval,
            approval_due_date,
            approval_completed_date,
            approval_status,
            priority_level
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        tasks,
    )


def generate_close_exceptions(tasks: list[tuple]) -> list[tuple]:
    exceptions = []
    exception_id = 5001

    high_risk_task_ids = []
    medium_risk_task_ids = []

    for row in tasks:
        task_id, entity_id, task_name, task_category, owner_id, scheduled_close_date, actual_close_date, task_status, requires_approval, approval_due_date, approval_completed_date, approval_status, priority_level = row

        if entity_id in {1, 4, 5} and task_category in {
            "Journal Entry",
            "Reconciliation",
            "Financial Reporting",
            "Intercompany",
        }:
            high_risk_task_ids.append(task_id)
        elif entity_id in {2, 6, 7} and task_category in {
            "Accrual Review",
            "Financial Reporting",
            "Reconciliation",
        }:
            medium_risk_task_ids.append(task_id)

    # High-risk tasks: more open and severe exceptions
    for task_id in high_risk_task_ids[:12]:
        exceptions.append(
            (
                exception_id,
                task_id,
                random.choice(
                    ["Balance Mismatch", "Missing Support", "Approval Delay"]
                ),
                random.choice(["High", "High", "Medium"]),
                "2026-04-08",
                None,
                "Open",
                random.choice(
                    [
                        "Manual Delay",
                        "Reviewer Bottleneck",
                        "Missing Documentation",
                        "Source Data Issue",
                    ]
                ),
            )
        )
        exception_id += 1

    # Medium-risk tasks: mix of resolved / open
    for task_id in medium_risk_task_ids[:10]:
        is_open = task_id % 2 == 0
        exceptions.append(
            (
                exception_id,
                task_id,
                random.choice(
                    ["Late Journal", "Mapping Error", "Missing Support"]
                ),
                random.choice(["Medium", "Low", "Medium"]),
                "2026-04-09",
                None if is_open else "2026-04-12",
                "Open" if is_open else "Resolved",
                random.choice(
                    [
                        "System Mapping",
                        "Manual Delay",
                        "Source Data Issue",
                    ]
                ),
            )
        )
        exception_id += 1

    # Add a few multiple exceptions on same tasks for realism
    duplicate_target_ids = high_risk_task_ids[:4]
    for task_id in duplicate_target_ids:
        exceptions.append(
            (
                exception_id,
                task_id,
                "Missing Support",
                "Medium",
                "2026-04-10",
                None,
                "Open",
                "Missing Documentation",
            )
        )
        exception_id += 1

    return exceptions


def insert_close_exceptions(cur: sqlite3.Cursor, exceptions: list[tuple]) -> None:
    cur.executemany(
        """
        INSERT INTO close_exceptions (
            exception_id,
            task_id,
            exception_type,
            exception_severity,
            identified_date,
            resolved_date,
            exception_status,
            root_cause
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        exceptions,
    )


def main() -> None:
    conn = create_connection()
    cur = conn.cursor()

    drop_tables(cur)
    create_tables(cur)
    insert_entities(cur)
    insert_task_owners(cur)

    tasks = generate_close_tasks()
    insert_close_tasks(cur, tasks)

    exceptions = generate_close_exceptions(tasks)
    insert_close_exceptions(cur, exceptions)

    conn.commit()

    entity_count = cur.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
    owner_count = cur.execute("SELECT COUNT(*) FROM task_owners").fetchone()[0]
    task_count = cur.execute("SELECT COUNT(*) FROM close_tasks").fetchone()[0]
    exception_count = cur.execute("SELECT COUNT(*) FROM close_exceptions").fetchone()[0]

    conn.close()

    print("practice.db created successfully.")
    print(f"entities: {entity_count}")
    print(f"task_owners: {owner_count}")
    print(f"close_tasks: {task_count}")
    print(f"close_exceptions: {exception_count}")


if __name__ == "__main__":
    main()