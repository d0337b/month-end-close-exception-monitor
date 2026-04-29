from pathlib import Path
import sqlite3
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "practice.db"
SQL_DIR = BASE_DIR / "sql"
OUTPUT_DIR = BASE_DIR / "output"


def read_sql_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def export_query(conn, sql_file_name, output_file_name):
    sql_path = SQL_DIR / sql_file_name
    output_path = OUTPUT_DIR / output_file_name

    query = read_sql_file(sql_path)
    df = pd.read_sql_query(query, conn)
    df.to_csv(output_path, index=False)

    print(f"Exported: {output_path}")

    return df


def generate_management_summary(task_df, entity_df, manager_df):
    summary_path = OUTPUT_DIR / "management_summary.md"

    manager = manager_df.iloc[0]

    high_risk_entities = (
        entity_df[entity_df["entity_risk_flag"] == "High Risk"]
        .sort_values(
            by=["overdue_task_count", "unresolved_exception_count"],
            ascending=[False, False]
        )
        .head(5)
    )

    priority_tasks = (
        task_df[task_df["priority_review_flag"] == "Yes"]
        .sort_values(
            by=["task_delay_days", "unresolved_exception_count"],
            ascending=[False, False]
        )
        .head(5)
    )

    lines = []

    lines.append("# Management Summary")
    lines.append("")

    lines.append("## Overall Close Status")
    lines.append(f"- Total close tasks: {int(manager['total_task_count'])}")
    lines.append(f"- Completed tasks: {int(manager['completed_task_count'])}")
    lines.append(f"- Open tasks: {int(manager['open_task_count'])}")
    lines.append(f"- Overdue tasks: {int(manager['overdue_task_count'])}")
    lines.append(f"- Overdue task ratio: {manager['overdue_task_ratio']:.3f}")
    lines.append(f"- Unresolved exceptions: {int(manager['unresolved_exception_count'])}")
    lines.append(f"- Delayed approvals: {int(manager['delayed_approval_count'])}")
    lines.append(f"- High-risk entities: {int(manager['high_risk_entity_count'])}")
    lines.append(f"- Average task delay days: {manager['avg_task_delay_days']:.3f}")
    lines.append(f"- Priority review tasks: {int(manager['priority_review_task_count'])}")
    lines.append("")

    lines.append("## High-Risk Entities")
    if high_risk_entities.empty:
        lines.append("- No high-risk entities identified.")
    else:
        for _, row in high_risk_entities.iterrows():
            lines.append(
                f"- {row['entity_name']} ({row['region']}, {row['business_unit']}): "
                f"{int(row['overdue_task_count'])} overdue tasks, "
                f"{int(row['unresolved_exception_count'])} unresolved exceptions, "
                f"{int(row['delayed_approval_count'])} delayed approvals."
            )
    lines.append("")

    lines.append("## Priority Review Tasks")
    if priority_tasks.empty:
        lines.append("- No priority review tasks identified.")
    else:
        for _, row in priority_tasks.iterrows():
            lines.append(
                f"- Task {int(row['task_id'])} | {row['entity_name']} | {row['task_name']}: "
                f"{row['task_delay_days']:.1f} delay days, "
                f"{int(row['unresolved_exception_count'])} unresolved exceptions, "
                f"approval delay = {row['approval_delay_flag']}."
            )
    lines.append("")

    lines.append("## Recommended Management Actions")
    lines.append("1. Review high-risk entities before closing the reporting cycle.")
    lines.append("2. Prioritize tasks with unresolved exceptions and approval delays.")
    lines.append("3. Follow up with responsible teams for overdue high-priority tasks.")
    lines.append("4. Use the exported CSV files as dashboard-ready inputs for Power BI.")
    lines.append("")

    with open(summary_path, "w", encoding="utf-8") as file:
        file.write("\n".join(lines))

    print(f"Exported: {summary_path}")


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)

    task_df = export_query(
        conn,
        "01_task_exception_summary.sql",
        "task_exception_summary.csv"
    )

    entity_df = export_query(
        conn,
        "02_entity_close_risk_summary.sql",
        "entity_close_risk_summary.csv"
    )

    manager_df = export_query(
        conn,
        "03_manager_close_dashboard_summary.sql",
        "manager_close_dashboard_summary.csv"
    )

    generate_management_summary(task_df, entity_df, manager_df)

    conn.close()


if __name__ == "__main__":
    main()