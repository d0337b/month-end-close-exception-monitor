# Control Matrix

## Purpose

이 문서는 Month-End Close Exception Monitor 프로젝트에서 가정한 월마감 리스크와  
그 리스크를 탐지하기 위한 데이터 신호, SQL 리포트, 관리 액션을 정리한 control matrix입니다.

이 프로젝트는 실제 내부통제 제도를 대체하기 위한 것이 아니라,  
월마감 과정에서 우선 검토가 필요한 리스크를 식별하기 위한 rule-based monitoring 구조를 보여주는 데 목적이 있습니다.

---

## Control Matrix Overview

| Risk Area | Risk Description | Data Signal | Report Output | Suggested Management Action |
|---|---|---|---|---|
| Task Delay | 예정된 close task가 기한 내 완료되지 않음 | `overdue_task_flag = 'Yes'` | `task_exception_summary.csv` | 지연 task 담당자 확인 및 close timeline 재조정 |
| Approval Delay | 승인 필요한 task의 approval이 지연됨 | `approval_delay_flag = 'Yes'` | `task_exception_summary.csv` | reviewer 또는 manager에게 승인 병목 확인 |
| Unresolved Exception | close exception이 해결되지 않고 Open 상태로 남아 있음 | `unresolved_exception_count >= 1` | `task_exception_summary.csv` | open exception 원인 확인 및 해결 우선순위 지정 |
| High Severity Exception | High severity exception이 unresolved 상태로 남아 있음 | `highest_exception_severity = 'High'` | `task_exception_summary.csv` | high severity issue 우선 검토 |
| Entity-Level Risk Concentration | 특정 entity에 지연 task 또는 unresolved exception이 집중됨 | `entity_risk_flag = 'High Risk'` | `entity_close_risk_summary.csv` | high-risk entity 중심으로 close review 진행 |
| Close Process Visibility Gap | 전체 close status를 한눈에 보기 어려움 | manager-level KPI summary | `manager_close_dashboard_summary.csv` | close meeting 전 KPI summary 확인 |
| Priority Review Need | 여러 리스크 신호가 있는 task를 우선 식별해야 함 | `priority_review_flag = 'Yes'` | `task_exception_summary.csv` | priority review task list 기반 후속 조치 |

---

## Risk Area Details

### 1. Task Delay

#### Risk Description

월마감 task가 예정된 close date까지 완료되지 않거나, 실제 완료일이 예정일보다 늦은 경우입니다.

#### Data Signal

이 프로젝트에서는 다음 조건 중 하나라도 해당하면 task delay로 봅니다.

- `actual_close_date IS NULL`이고 `scheduled_close_date`가 기준일보다 과거인 경우
- `actual_close_date > scheduled_close_date`인 경우

SQL에서는 이를 `overdue_task_flag`로 표시합니다.

#### Report Output

- `task_exception_summary.csv`
- `entity_close_risk_summary.csv`
- `manager_close_dashboard_summary.csv`

#### Suggested Management Action

지연된 task의 owner와 team을 확인하고,  
close timeline에 미치는 영향을 검토합니다.

---

### 2. Approval Delay

#### Risk Description

승인이 필요한 close task가 approval due date 내에 승인되지 않은 경우입니다.

승인 지연은 단순 일정 지연뿐 아니라 review bottleneck 또는 control weakness 신호일 수 있습니다.

#### Data Signal

다음 조건을 기준으로 approval delay를 탐지합니다.

- `requires_approval = 'Yes'`
- `approval_status = 'Pending'`이고 `approval_due_date`가 기준일보다 과거인 경우
- 또는 `approval_completed_date > approval_due_date`인 경우

SQL에서는 이를 `approval_delay_flag`로 표시합니다.

#### Report Output

- `task_exception_summary.csv`
- `manager_close_dashboard_summary.csv`

#### Suggested Management Action

approval이 지연된 task를 확인하고,  
reviewer 또는 manager에게 승인 병목 원인을 확인합니다.

---

### 3. Unresolved Exception

#### Risk Description

close task와 관련된 exception이 아직 해결되지 않고 Open 상태로 남아 있는 경우입니다.

미해결 예외는 마감 품질과 재무보고 정확성에 영향을 줄 수 있습니다.

#### Data Signal

`close_exceptions` 테이블에서 다음 조건을 기준으로 탐지합니다.

- `exception_status = 'Open'`

task별로 Open exception 개수를 집계하여  
`unresolved_exception_count`로 표시합니다.

#### Report Output

- `task_exception_summary.csv`
- `entity_close_risk_summary.csv`
- `manager_close_dashboard_summary.csv`

#### Suggested Management Action

Open exception의 root cause를 확인하고,  
High severity 또는 반복 발생 exception부터 우선 해결합니다.

---

### 4. High Severity Exception

#### Risk Description

미해결 예외 중 severity가 높은 exception이 존재하는 경우입니다.

예외 개수가 적더라도 High severity exception은 우선 검토 대상이 될 수 있습니다.

#### Data Signal

Open exception을 기준으로 severity 우선순위를 적용합니다.

- High
- Medium
- Low
- None

SQL에서는 task별 최고 severity를 `highest_exception_severity`로 표시합니다.

#### Report Output

- `task_exception_summary.csv`

#### Suggested Management Action

High severity exception이 있는 task를 우선 검토하고,  
해당 issue가 reporting timeline 또는 재무정보 정확성에 미치는 영향을 확인합니다.

---

### 5. Entity-Level Risk Concentration

#### Risk Description

특정 entity에서 overdue task, unresolved exception, delayed approval이 집중되는 경우입니다.

이는 개별 task 문제가 아니라 entity 단위의 close process risk로 볼 수 있습니다.

#### Data Signal

entity별 집계값을 기준으로 risk를 분류합니다.

High Risk 기준:

- `overdue_task_count >= 3`
- 또는 `unresolved_exception_count >= 2`
- 또는 `delayed_approval_count >= 2`

Medium Risk 기준:

- `overdue_task_count >= 1`
- 또는 `unresolved_exception_count >= 1`

그 외는 Low Risk로 분류합니다.

#### Report Output

- `entity_close_risk_summary.csv`
- `manager_close_dashboard_summary.csv`

#### Suggested Management Action

High Risk entity를 close meeting에서 우선 검토하고,  
반복적으로 발생하는 delay 또는 exception 원인을 확인합니다.

---

### 6. Priority Review Task

#### Risk Description

여러 리스크 신호가 있는 task를 우선적으로 식별하지 못하면,  
관리자가 중요한 이슈를 놓칠 수 있습니다.

#### Data Signal

다음 조건 중 하나라도 해당하면 priority review 대상으로 분류합니다.

- `overdue_task_flag = 'Yes'`
- `approval_delay_flag = 'Yes'`
- `unresolved_exception_count >= 1`
- `highest_exception_severity = 'High'`

SQL에서는 이를 `priority_review_flag`로 표시합니다.

#### Report Output

- `task_exception_summary.csv`
- `management_summary.md`

#### Suggested Management Action

Priority Review task를 우선 검토하고,  
owner, team, exception root cause를 기준으로 후속 조치를 진행합니다.

---

## Report-to-Control Mapping

| Report | Main Purpose | Control Perspective |
|---|---|---|
| `01_task_exception_summary.sql` | task-level issue detail | 지연, 승인 지연, 미해결 예외를 task 단위로 식별 |
| `02_entity_close_risk_summary.sql` | entity-level risk classification | entity 단위의 반복적 close risk를 요약 |
| `03_manager_close_dashboard_summary.sql` | manager-level KPI summary | 전체 close process의 상태와 우선순위를 요약 |
| `management_summary.md` | readable management commentary | SQL output을 사람이 읽을 수 있는 action-oriented summary로 변환 |

---

## Limitations

이 프로젝트의 risk classification은 rule-based logic에 기반합니다.

따라서 실제 업무 적용 시에는 다음 요소가 추가로 고려되어야 합니다.

- materiality threshold
- entity-specific close calendar
- task dependency
- reviewer capacity
- exception aging policy
- actual internal control framework

이 프로젝트의 목적은 실제 내부통제 판단을 대체하는 것이 아니라,  
SQL과 Python을 활용해 close process risk를 모니터링하는 구조를 설계하는 것입니다.

---

## Summary

이 control matrix는 월마감 과정에서 발생할 수 있는 주요 리스크를  
데이터 신호와 SQL output으로 연결합니다.

이를 통해 프로젝트는 단순한 데이터 집계가 아니라,  
close process의 지연, 예외, 승인 병목을 식별하고  
관리자가 우선 검토할 수 있는 reporting structure를 구현합니다.