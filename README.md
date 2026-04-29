# Month-End Close Exception Monitor

SQL and Python project for month-end close exception monitoring, entity-level close risk analysis, and manager-level KPI reporting.

Built with SQLite, SQL, Python, and pandas.  
Outputs task-level exception reports, entity-level risk summaries, manager dashboard summaries, and a management summary report.

---

## Project Overview

월마감(month-end close) 프로세스에서 발생하는 지연 태스크, 승인 지연, 미해결 예외를 SQL과 Python으로 분석하여  
관리자 관점의 close risk monitoring 리포트를 생성하는 프로젝트입니다.

이 프로젝트는 단순히 task 완료 여부를 집계하는 것을 넘어서,  
close task delay, approval delay, unresolved exception, entity-level risk를 함께 반영하여  
controllership 관점의 업무개선형 리포트 구조를 만드는 데 초점을 두었습니다.

---

## Business Problem

월마감 과정에서는 여러 entity, 담당자, 승인 절차, 예외 이슈가 동시에 발생합니다.

실무에서는 단순히 “마감 task가 완료되었는가”만 보는 것이 아니라,

- 어떤 task가 예정일보다 늦었는지
- 어떤 approval이 지연되고 있는지
- 어떤 exception이 아직 unresolved 상태인지
- 어느 entity가 반복적으로 close risk를 만들고 있는지
- manager가 어떤 영역을 우선 점검해야 하는지

를 함께 봐야 합니다.

이 프로젝트는 이러한 close monitoring 흐름을 반영하여  
task-level detail, entity-level risk summary, manager-level KPI summary를 생성합니다.

---

## Why It Matters

월마감은 재무보고의 정확성과 적시성에 직접 연결되는 핵심 프로세스입니다.

close process에서 지연 task, unresolved exception, approval delay가 누적되면  
재무제표 작성, 내부통제, reporting timeline에 영향을 줄 수 있습니다.

이 프로젝트는 close process를 데이터 구조로 나누고,  
SQL 기반 리스크 기준을 적용하여 다음 3단계로 분석합니다.

1. Task-level exception monitoring
2. Entity-level close risk classification
3. Manager-level KPI reporting

이를 통해 단순 작업 목록이 아니라  
관리자가 바로 읽고 판단할 수 있는 controllership monitoring output을 만드는 것을 목표로 합니다.

---

## Tech Stack

- Python
- SQLite
- SQL
- pandas

---

## Project Structure

```text
month-end-close-exception-monitor/
├── setup_data.py
├── main.py
├── docs/
│   ├── process_overview.md
│   └── control_matrix.md
├── output/
│   ├── task_exception_summary.csv
│   ├── entity_close_risk_summary.csv
│   ├── manager_close_dashboard_summary.csv
│   └── management_summary.md
├── sql/
│   ├── 01_task_exception_summary.sql
│   ├── 02_entity_close_risk_summary.sql
│   └── 03_manager_close_dashboard_summary.sql
└── README.md
```

## Data Model

이 프로젝트는 월마감 프로세스를 4개의 테이블로 나누어 설계했습니다.

### close_tasks

월마감 task의 본체가 되는 테이블입니다.

주요 컬럼:

- task_id
- entity_id
- task_name
- task_category
- owner_id
- scheduled_close_date
- actual_close_date
- task_status
- requires_approval
- approval_due_date
- approval_completed_date
- approval_status
- priority_level

이 테이블을 기준으로 task delay, overdue task, approval delay를 계산합니다.

### close_exceptions

각 close task에 연결된 예외 및 통제 이슈를 담는 테이블입니다.

주요 컬럼:

- exception_id
- task_id
- exception_type
- exception_severity
- identified_date
- resolved_date
- exception_status
- root_cause

이 테이블을 사용하여 unresolved exception count와 highest exception severity를 계산합니다.

### entities

마감 대상 법인 또는 사업단위 정보를 담는 마스터 테이블입니다.

주요 컬럼:

- entity_id
- entity_name
- region
- business_unit
- entity_priority

이 테이블을 사용하여 entity-level close risk summary를 생성합니다.

### task_owners

close task 담당자 및 팀 정보를 담는 마스터 테이블입니다.

주요 컬럼:

- owner_id
- owner_name
- team_name
- manager_name

이 테이블을 사용하여 task owner 및 team-level context를 리포트에 연결합니다.

## Documentation

이 프로젝트는 코드와 SQL output뿐 아니라, 월마감 프로세스와 리스크/통제 관점을 설명하는 문서를 함께 포함합니다.

- `docs/process_overview.md`  
  월마감 프로세스 흐름, 주요 리스크, 데이터 모델, SQL 리포트 구조를 설명합니다.

- `docs/control_matrix.md`  
  월마감 과정에서 발생할 수 있는 task delay, approval delay, unresolved exception, entity-level risk를  
  데이터 신호와 SQL output, 관리 액션으로 연결한 control matrix입니다.

- `docs/ai_usage_note.md`  
  SQL/Python output을 기반으로 AI-generated management commentary를 생성할 수 있는 구조와, human-in-the-loop 검토 원칙을 설명합니다.

이 문서들은 프로젝트가 단순 SQL 연습이 아니라,  
회계·재무 업무 프로세스를 데이터 구조와 reporting output으로 번역하는 과정을 보여주기 위해 작성했습니다.

## Key Features

- 월마감 task별 지연일수 계산
- overdue task flag 생성
- approval delay flag 생성
- task별 unresolved exception count 집계
- task별 highest exception severity 산정
- priority review task 식별
- entity별 close risk flag 분류
- manager-level KPI summary 생성
- SQL 결과를 CSV로 자동 export
- management summary markdown report 자동 생성
- Power BI dashboard 연결을 고려한 output 구조 설계

## SQL Reports

### 01_task_exception_summary.sql

task-level 상세 리포트입니다.

각 close task에 대해 지연 여부, 승인 지연, 미해결 예외, 우선 점검 여부를 계산합니다.

주요 컬럼:

- task_id
- entity_name
- region
- business_unit
- task_name
- task_category
- owner_name
- team_name
- task_delay_days
- overdue_task_flag
- approval_delay_flag
- unresolved_exception_count
- highest_exception_severity
- priority_review_flag

이 리포트는 실무자가 어떤 task를 먼저 확인해야 하는지 파악하기 위한 상세 목록입니다.

### 02_entity_close_risk_summary.sql

entity-level 리스크 요약 리포트입니다.

각 entity별로 close task 현황, overdue task 수, unresolved exception 수, delayed approval 수를 집계하고
entity_risk_flag를 분류합니다.

주요 컬럼:

- entity_name
- region
- business_unit
- total_task_count
- completed_task_count
- overdue_task_count
- unresolved_exception_count
- delayed_approval_count
- avg_task_delay_days
- high_priority_task_count
- entity_risk_flag

이 리포트는 어떤 entity가 close process에서 리스크가 높은지 파악하기 위한 요약입니다.

### 03_manager_close_dashboard_summary.sql

manager-level KPI summary 리포트입니다.

전체 월마감 현황을 한눈에 볼 수 있도록 핵심 KPI를 1행으로 요약합니다.

주요 컬럼:

- total_task_count
- completed_task_count
- open_task_count
- overdue_task_count
- overdue_task_ratio
- unresolved_exception_count
- delayed_approval_count
- high_risk_entity_count
- avg_task_delay_days
- priority_review_task_count

이 리포트는 Power BI dashboard의 executive summary page로 확장하기 좋은 구조입니다.

## Management Summary Output

`main.py`는 SQL 결과를 CSV로 export한 뒤,
주요 KPI와 high-risk entity, priority review task를 요약한 `management_summary.md` 파일을 생성합니다.

생성되는 management summary는 다음 내용을 포함합니다.

- Overall close status
- High-risk entities
- Priority review tasks
- Recommended management actions

이 파일은 SQL output을 사람이 읽을 수 있는 management commentary 형태로 바꾸는 중간 산출물입니다.

## Power BI-Ready Design

이 프로젝트의 output CSV 파일들은 Power BI dashboard 연결을 염두에 두고 설계했습니다.

예상 Power BI page 구성:

1. Executive Summary
2. Entity Close Risk View
3. Task Exception Detail
4. Approval Delay Monitoring
5. Priority Review Task List

Power BI에서 사용할 수 있는 주요 데이터셋:

- task_exception_summary.csv
- entity_close_risk_summary.csv
- manager_close_dashboard_summary.csv

이를 통해 SQL/Python 결과를 단순 CSV 산출물에서
dashboard-ready finance operations dataset으로 확장할 수 있습니다.

## AI-Ready Extension

현재 단계에서는 Python rule-based 방식으로 `management_summary.md`를 생성합니다.

향후 AI layer를 추가하면, SQL/Python으로 계산된 검증 가능한 output을 기반으로
LLM이 manager commentary draft를 생성하는 구조로 확장할 수 있습니다.

예상 AI 활용 방향:

- close risk commentary 초안 생성
- high-risk entity 원인 요약
- unresolved exception 패턴 설명
- manager action item 초안 작성
- human review를 통한 AI output 검증

이 프로젝트에서 AI는 데이터를 대신 판단하는 역할이 아니라,
SQL 기반 산출물을 사람이 읽기 쉬운 management commentary로 변환하는 보조 layer로 활용하는 것을 목표로 합니다.

## How to Run

샘플 데이터와 SQLite DB를 생성합니다.
``` bash
python3 setup_data.py
```
SQL 리포트를 실행하고 CSV 및 management summary를 생성합니다.
``` bash
python3 main.py
```
생성된 output 파일을 확인합니다.
``` bash
ls output
```

## Generated Output

```
output/task_exception_summary.csv
output/entity_close_risk_summary.csv
output/manager_close_dashboard_summary.csv
output/management_summary.md
```

## Key Insights

월마감 리스크는 단순히 task 완료 여부만으로는 충분히 설명할 수 없습니다.

approval delay, unresolved exception, task delay, entity-level concentration을 함께 봐야
실제 close process의 병목과 관리 우선순위를 파악할 수 있습니다.

이 프로젝트는 task-level detail과 entity-level summary, manager-level KPI를 분리함으로써
실무자와 관리자 모두가 활용할 수 있는 close monitoring 구조를 구현했습니다.

## What I Learned

- 월마감 프로세스를 데이터 모델로 나누는 방식
- task, exception, entity, owner 데이터를 분리하고 다시 결합하는 방식
- CTE를 활용한 task-level, entity-level, manager-level SQL 구조 설계
- overdue task, approval delay, unresolved exception 같은 rule-based flag 계산
- SQL 결과를 Python으로 자동 export하는 방법
- CSV output을 management summary report로 변환하는 방법
- Power BI와 AI layer로 확장 가능한 finance operations output 구조 설계

## Portfolio Relevance

이 프로젝트는 회계·재무 프로세스에서 발생하는 task delay, approval delay, unresolved exception을
데이터 기반으로 식별하고 요약하는 과정을 구현한 프로젝트입니다.

SQL을 통해 close risk를 계산하고, Python으로 결과를 자동 export하며,
관리자가 확인할 수 있는 summary output으로 연결하는 흐름을 설계했습니다.

이를 통해 단순 분석 결과가 아니라, 실제 업무 판단에 활용될 수 있는 reporting output을 만드는 데 초점을 두었습니다.