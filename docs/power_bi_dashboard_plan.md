# Power BI Dashboard Plan

## Purpose

이 문서는 Month-End Close Exception Monitor 프로젝트의 SQL/Python output을  
Power BI dashboard로 확장할 때 어떤 구조로 시각화할 수 있는지 설명합니다.

이 프로젝트의 Power BI dashboard는 단순한 시각화 연습이 아니라,  
월마감 프로세스에서 발생하는 task delay, approval delay, unresolved exception, entity-level risk를  
관리자 관점에서 빠르게 확인할 수 있는 reporting layer를 설계하는 데 목적이 있습니다.

---

## Dashboard Objective

이 dashboard는 다음 3가지 질문에 답하는 것을 목표로 합니다.

1. 전체 월마감 상태는 어떤가?
2. 어떤 entity가 close risk를 많이 만들고 있는가?
3. 어떤 task를 manager가 우선적으로 검토해야 하는가?

즉 Power BI는 SQL 결과를 보기 좋게 꾸미는 도구가 아니라,  
SQL/Python으로 계산된 close monitoring output을 manager-facing report로 바꾸는 역할을 합니다.

---

## Data Sources

Power BI dashboard는 `main.py` 실행 후 생성되는 다음 CSV 파일들을 사용합니다.

- `output/task_exception_summary.csv`
- `output/entity_close_risk_summary.csv`
- `output/manager_close_dashboard_summary.csv`

각 파일의 역할은 다음과 같습니다.

### task_exception_summary.csv

task-level 상세 리포트입니다.

각 close task에 대해 지연 여부, 승인 지연, 미해결 예외, 우선 점검 여부를 포함합니다.

주요 활용:

- priority review task list
- task delay detail
- approval delay monitoring
- unresolved exception detail

### entity_close_risk_summary.csv

entity-level 리스크 요약 리포트입니다.

각 entity별 overdue task, unresolved exception, delayed approval, entity risk flag를 포함합니다.

주요 활용:

- entity risk ranking
- high-risk entity table
- region / business unit filter
- entity-level close status view

### manager_close_dashboard_summary.csv

manager-level KPI 요약 리포트입니다.

전체 close process의 핵심 KPI를 1행으로 요약합니다.

주요 활용:

- executive summary card
- overall close status
- high-risk entity count
- priority review task count

---

## Dashboard Page Structure

Power BI dashboard는 3개 page로 구성하는 것을 목표로 합니다.

---

## Page 1: Executive Summary

### Purpose

전체 월마감 상태를 한눈에 보여주는 executive view입니다.

이 페이지는 manager가 close meeting 전에 전체 리스크 수준을 빠르게 파악하는 데 사용됩니다.

### Dataset

- `manager_close_dashboard_summary.csv`

### Key Metrics

- total_task_count
- completed_task_count
- open_task_count
- overdue_task_count
- overdue_task_ratio
- unresolved_exception_count
- delayed_approval_count
- high_risk_entity_count
- priority_review_task_count

### Suggested Visuals

- KPI card: total_task_count
- KPI card: overdue_task_count
- KPI card: overdue_task_ratio
- KPI card: unresolved_exception_count
- KPI card: delayed_approval_count
- KPI card: high_risk_entity_count
- KPI card: priority_review_task_count
- small summary table

### Management Question

이 페이지는 다음 질문에 답합니다.

> 현재 close process가 정상적으로 진행되고 있는가, 아니면 manager review가 필요한 상태인가?

---

## Page 2: Entity Risk View

### Purpose

어떤 entity가 가장 높은 close risk를 보이는지 확인하는 페이지입니다.

이 페이지는 entity별 병목과 리스크 집중도를 파악하는 데 사용됩니다.

### Dataset

- `entity_close_risk_summary.csv`

### Key Metrics

- total_task_count
- completed_task_count
- overdue_task_count
- unresolved_exception_count
- delayed_approval_count
- avg_task_delay_days
- high_priority_task_count
- entity_risk_flag

### Suggested Visuals

- bar chart: overdue_task_count by entity_name
- bar chart: unresolved_exception_count by entity_name
- table: entity_name, region, business_unit, entity_risk_flag
- slicer: region
- slicer: business_unit
- slicer: entity_risk_flag

### Management Question

이 페이지는 다음 질문에 답합니다.

> 어느 entity가 close process에서 가장 큰 리스크를 만들고 있는가?

---

## Page 3: Task Exception Detail

### Purpose

우선 점검이 필요한 task를 상세히 확인하는 페이지입니다.

이 페이지는 실무자 또는 manager가 실제 후속 조치를 취할 task를 찾는 데 사용됩니다.

### Dataset

- `task_exception_summary.csv`

### Key Fields

- task_id
- entity_name
- region
- business_unit
- task_name
- task_category
- owner_name
- team_name
- scheduled_close_date
- actual_close_date
- task_status
- task_delay_days
- overdue_task_flag
- approval_delay_flag
- unresolved_exception_count
- highest_exception_severity
- priority_review_flag

### Suggested Visuals

- detail table: priority review tasks
- filter: priority_review_flag
- filter: highest_exception_severity
- filter: approval_delay_flag
- filter: team_name
- bar chart: task_delay_days by task_name or entity_name

### Management Question

이 페이지는 다음 질문에 답합니다.

> 어떤 task를 지금 가장 먼저 확인해야 하는가?

---

## Dashboard Flow

Power BI dashboard는 다음 흐름으로 보는 것을 가정합니다.

1. Executive Summary에서 전체 close status 확인
2. Entity Risk View에서 high-risk entity 확인
3. Task Exception Detail에서 priority review task 확인
4. 필요 시 owner/team 단위로 후속 조치 진행

즉 dashboard는 단순히 지표를 나열하는 것이 아니라,  
전체 상태 확인 → entity 리스크 식별 → task-level action으로 내려가는 구조입니다.

---

## Power BI Design Principle

이 dashboard는 generic visualization이 아니라  
finance close monitoring을 위한 reporting layer로 설계합니다.

따라서 시각화의 목적은 예쁜 그래프가 아니라,  
manager가 다음 의사결정을 할 수 있도록 돕는 것입니다.

중요한 설계 원칙은 다음과 같습니다.

- KPI는 executive summary에서 간단히 보여준다.
- entity-level risk는 비교 가능한 형태로 보여준다.
- priority review task는 상세 table로 제공한다.
- region, business unit, risk flag 기준으로 필터링할 수 있게 한다.
- SQL/Python output과 Power BI visual 사이의 연결이 명확해야 한다.

---

## Future Extension

향후 이 dashboard는 다음 방향으로 확장할 수 있습니다.

- Power BI screenshot을 README에 추가
- entity risk page에 conditional formatting 적용
- task detail page에 priority review filter 추가
- management_summary.md와 dashboard KPI 비교
- AI-generated commentary와 dashboard output 연결

---

## Summary

이 Power BI dashboard plan은 SQL/Python으로 생성된 close monitoring output을  
manager-facing dashboard로 확장하기 위한 설계 문서입니다.

프로젝트의 핵심은 단순 시각화가 아니라,  
월마감 프로세스의 지연, 승인 병목, 미해결 예외, entity-level risk를  
관리자가 이해하고 후속 조치할 수 있는 reporting structure로 만드는 것입니다.