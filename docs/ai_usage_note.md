# AI Usage Note

## Purpose

이 문서는 Month-End Close Exception Monitor 프로젝트에서 AI를 어떤 방식으로 활용할 수 있는지 설명합니다.

이 프로젝트에서 AI는 데이터를 직접 계산하거나 리스크를 임의로 판단하는 역할이 아닙니다.

SQL과 Python으로 생성된 검증 가능한 output을 기반으로,  
manager가 읽을 수 있는 commentary draft와 action item 초안을 생성하는 보조 layer로 활용하는 것을 가정합니다.

---

## AI Role in This Project

이 프로젝트의 기본 흐름은 다음과 같습니다.

1. SQL로 close task, exception, approval delay, entity risk를 계산
2. Python으로 CSV output과 management summary를 생성
3. AI는 이 결과를 바탕으로 management commentary draft를 작성
4. 사람이 최종 검토하고 수정

즉 AI는 다음과 같은 역할을 수행할 수 있습니다.

- close risk commentary 초안 작성
- high-risk entity 원인 요약
- unresolved exception 패턴 설명
- manager action item 초안 작성
- reporting meeting용 summary 문장 생성

---

## What AI Should Not Do

이 프로젝트에서 AI가 해서는 안 되는 역할도 명확히 구분합니다.

AI는 다음을 대체하지 않습니다.

- SQL 기반 KPI 계산
- close risk rule 적용
- 실제 회계 판단
- 내부통제 결론
- management approval
- human review

즉 AI output은 최종 보고서가 아니라  
검토가 필요한 draft입니다.

---

## Input Data for AI Commentary

AI commentary는 다음 output 파일을 기반으로 생성될 수 있습니다.

- `output/task_exception_summary.csv`
- `output/entity_close_risk_summary.csv`
- `output/manager_close_dashboard_summary.csv`
- `output/management_summary.md`

이 파일들은 SQL과 Python으로 생성된 구조화된 결과물입니다.

AI는 이 데이터를 바탕으로 요약할 수 있지만,  
숫자와 리스크 판단의 근거는 SQL output에 있어야 합니다.

---

## Example AI Commentary Prompt

아래는 AI commentary 생성을 위해 사용할 수 있는 예시 prompt입니다.

```text
You are assisting a finance manager reviewing month-end close status.

Using the provided SQL-generated outputs, write a concise management commentary that includes:

1. Overall close status
2. Key high-risk entities
3. Main drivers of close risk
4. Priority review tasks
5. Recommended follow-up actions

Do not invent numbers.
Use only the provided output data.
Clearly separate factual observations from recommended actions.
Mention that final review should be performed by the finance manager.
```

## Example Commentary Structure

```text
AI가 생성할 수 있는 commentary는 다음과 같은 구조를 가질 수 있습니다.

Overall close status:
The close process shows elevated risk due to overdue tasks, unresolved exceptions, and delayed approvals.

Key risk areas:
Korea HQ and US West Entity require priority review because they have multiple overdue tasks and unresolved exceptions.

Recommended actions:
1. Review high-risk entities before finalizing the close cycle.
2. Follow up on overdue high-priority tasks.
3. Resolve open high-severity exceptions.
4. Validate AI-generated commentary against the SQL output before management use.
```

## Human-in-the-Loop Review

AI가 생성한 commentary는 사용 전에 반드시 사람이 검토해야 합니다.

검토자는 다음 사항을 확인해야 합니다.

- 수치가 SQL 출력 결과와 일치하는지
- risk에 대한 설명이 데이터로 뒷받침되는지
- 조치 권고 사항이 타당한지
- 해설이 결론을 과장하고 있는지
- 추가적인 회계적 맥락이 필요한지

AI는 패턴을 잘 요약할 수는 있지만,
전문가의 판단이나 경영진의 검토를 대체해서는 안 되기 때문에 이러한 ‘human-in-the-loop’ 단계가 중요합니다.

## Portfolio Relevance
이 AI 레이어는 구조화 재무 데이터의 산출물을 AI 지원 보고 프로세스와 어떻게 연계할 수 있는지 보여줍니다.

이 프로젝트는 다음과 같은 workflow를 구현합니다:

```
SQL calculation
→ Python export
→ management summary
→ AI commentary draft
→ human review
```

이 프로젝트의 목적은 AI를 단순한 생산성 도구로 활용하는 방법을 보여주는 것이 아니라,
명확한 역할 분담과 검토 절차를 통해 AI를 재무 보고 workflow에 어떻게 통합할 수 있는지 보여주는 데 있습니다.