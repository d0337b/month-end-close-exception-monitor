# Process Overview

## Purpose

이 문서는 Month-End Close Exception Monitor 프로젝트가 어떤 월마감 프로세스를 가정하고 있으며,  
각 데이터 테이블과 SQL 리포트가 실제 업무 흐름에서 어떤 역할을 하는지 설명합니다.

이 프로젝트의 목적은 단순히 close task 목록을 집계하는 것이 아니라,  
월마감 과정에서 발생할 수 있는 지연, 승인 병목, 미해결 예외를 식별하고  
관리자가 우선적으로 검토해야 할 영역을 보여주는 것입니다.

---

## Month-End Close Process

월마감(month-end close)은 한 회계기간이 끝난 후  
거래 정리, 분개 검토, 계정 대사, 발생주의 항목 검토, 재무보고 준비 등을 수행하는 프로세스입니다.

일반적인 월마감 흐름은 다음과 같습니다.

1. Close task 생성
2. 담당자별 task 수행
3. 필요한 경우 approval 진행
4. exception 발생 시 원인 확인 및 해결
5. entity별 close status 점검
6. manager-level KPI 확인
7. 최종 reporting cycle 마감

이 프로젝트는 위 흐름 중에서  
task delay, approval delay, unresolved exception, entity-level risk를 모니터링하는 데 초점을 둡니다.

---

## Key Process Risks

월마감 프로세스에서 중요한 리스크는 다음과 같습니다.

### Task Delay

예정된 close date보다 task가 늦게 완료되거나 아직 완료되지 않은 상태입니다.

이 리스크는 reporting timeline 지연으로 이어질 수 있습니다.

### Approval Delay

승인이 필요한 task가 approval due date를 넘겼거나, 승인 완료가 지연된 상태입니다.

이 리스크는 review bottleneck 또는 control weakness 신호가 될 수 있습니다.

### Unresolved Exception

close task와 관련된 예외가 아직 Open 상태로 남아 있는 경우입니다.

예외가 해결되지 않으면 마감 품질과 재무보고 정확성에 영향을 줄 수 있습니다.

### Entity-Level Concentration

특정 entity에서 overdue task, unresolved exception, delayed approval이 반복적으로 발생하는 경우입니다.

이는 개별 task 문제가 아니라 entity 단위의 close risk로 볼 수 있습니다.

---

## Data Model Logic

이 프로젝트는 월마감 프로세스를 4개의 테이블로 나누어 설계했습니다.

### close_tasks

월마감 task의 중심 테이블입니다.

각 task의 예정일, 실제 완료일, 상태, 승인 필요 여부, 승인 상태, 우선순위를 담고 있습니다.

이 테이블을 기준으로 다음 지표를 계산합니다.

- task_delay_days
- overdue_task_flag
- approval_delay_flag

### close_exceptions

close task에 연결된 예외 이슈를 담는 테이블입니다.

각 task에 여러 개의 exception이 붙을 수 있기 때문에,  
SQL에서는 먼저 task_id 기준으로 요약한 뒤 close_tasks와 연결합니다.

이 테이블을 기준으로 다음 지표를 계산합니다.

- unresolved_exception_count
- highest_exception_severity

### entities

entity, region, business unit 정보를 담는 마스터 테이블입니다.

이 테이블을 통해 task-level 데이터를 entity-level risk summary로 확장합니다.

### task_owners

task 담당자와 팀 정보를 담는 마스터 테이블입니다.

task-level report에서 owner와 team context를 제공하기 위해 사용합니다.

---

## Report Flow

이 프로젝트의 SQL 리포트는 3단계로 구성됩니다.

### 1. Task-Level Exception Summary

`01_task_exception_summary.sql`

각 task를 기준으로 지연 여부, 승인 지연, 미해결 예외, 우선 점검 여부를 계산합니다.

이 리포트는 실무자가 어떤 task를 먼저 확인해야 하는지 판단하기 위한 상세 리포트입니다.

### 2. Entity-Level Close Risk Summary

`02_entity_close_risk_summary.sql`

task-level 결과를 entity 기준으로 집계하여  
각 entity의 close risk를 High Risk, Medium Risk, Low Risk로 분류합니다.

이 리포트는 manager가 어떤 entity를 우선적으로 점검해야 하는지 판단하기 위한 요약 리포트입니다.

### 3. Manager-Level Dashboard Summary

`03_manager_close_dashboard_summary.sql`

전체 close process의 핵심 KPI를 1행으로 요약합니다.

이 리포트는 Power BI dashboard 또는 management summary의 executive view로 확장하기 위한 기반 데이터입니다.

---

## Risk Classification Logic

Entity-level risk는 다음 기준으로 분류합니다.

### High Risk

다음 중 하나라도 해당하는 entity입니다.

- overdue_task_count >= 3
- unresolved_exception_count >= 2
- delayed_approval_count >= 2

### Medium Risk

다음 중 하나라도 해당하는 entity입니다.

- overdue_task_count >= 1
- unresolved_exception_count >= 1

### Low Risk

위 조건에 해당하지 않는 entity입니다.

이 기준은 실제 회계 판단을 대체하기 위한 것이 아니라,  
우선 검토 대상을 식별하기 위한 rule-based monitoring logic입니다.

---

## Management Use Case

이 프로젝트의 결과물은 다음과 같은 업무 상황에서 활용될 수 있습니다.

- close meeting 전 high-risk entity 확인
- overdue task와 approval delay 우선 점검
- unresolved exception이 많은 task 식별
- manager-level KPI dashboard 구성
- close process 병목 구간 파악

즉 이 프로젝트는 단순 데이터 분석 결과가 아니라,  
월마감 프로세스에서 관리자가 우선적으로 확인해야 할 리스크를 구조화한 reporting output입니다.