# Next Prompt

아래 내용을 다음 새 세션의 첫 프롬프트로 사용한다.

```text
/home/jongwon/personal_project/law_main_road 에서 작업해주세요.

기준일:
- 2026-04-20

현재 상태 요약:
- origin/main과 main은 최신 상태여야 합니다.
- 최근 중요 커밋:
  - 1461a44 docs: record MVP eval tuning follow-up
  - 9856c45 test: add answer eval evidence report
  - ab32c26 docs: record final demo preflight pass
  - 5f23e76 chore: add demo preflight script
- SCN-004 demo freeze 유지 완료.
- SCN-004 document draft backend 완료.
- SCN-004 After frontend 4-route flow 완료:
  - /after
  - /after/result
  - /after/intake
  - /after/draft
- rendered_text copy, browser print, print disclaimer 완료.
- draft navigation race 수정 완료.
- free input SCN-004 document eligibility guard 완료.
- presentation-local fixed answer preset 구조 완료.
- demo preflight script 추가 완료.
- eval answer evidence report와 full 60 QA summary 추가 완료.

현재 frontend presentation preset:
- Source of truth: frontend/src/lib/scenarioPresets.ts
- Fixed answer fixture: frontend/src/lib/scenarioPresetAnswers.json
- SCN-001-BRIDGE-DEMO
  - scenarioId: SCN-001
  - supportsDraft: false
  - Before/Bridge handoff 설명용 answer-only preset
  - fixed/live 여부와 관계없이 문서 초안 선택 UI를 열지 않음
- SCN-004-DEMO-FREEZE
  - scenarioId: SCN-004
  - supportsDraft: true
  - main demo / document draft freeze용 preset
  - fixed/live 여부와 관계없이 SCN-004 draft eligibility 적용
- SCN-005
  - 현재 frontend UI preset에서 제외
  - 후속 확장 후보로만 유지

중요한 구분:
- eval/scenario_demo_question_sets_v1.json은 scenario smoke/eval 질문 세트입니다.
- eval id(SCN-001-Q3, SCN-004-Q1 등)와 presentation-local preset id(SCN-001-BRIDGE-DEMO, SCN-004-DEMO-FREEZE)를 혼용하지 마세요.
- presentation fixed fixture는 데모 안정성을 위한 고정 응답입니다.
- eval answer evidence report는 live retrieval/answer 품질 검증 산출물입니다.

SCN-004 freeze 기준:
- SCN-004-DEMO-FREEZE exact preset path는 /api/v1/answer를 호출하지 않고 fixed AnswerResponse fixture를 사용합니다.
- fixed answer:
  - cited_articles=6
  - grounded_context_ids=[1, 2, 3, 5, 10, 4]
  - retrieval_total=10
  - model_name=gemini-2.5-flash
- wage complaint draft:
  - document_type=labor_office_wage_complaint
  - cited_articles=2
  - source_context_ids=[5, 10]
  - missing_legal_basis=[]
- unfair dismissal brief draft:
  - document_type=labor_commission_unfair_dismissal_brief
  - cited_articles=4
  - source_context_ids=[1, 2, 3, 4]
  - missing_legal_basis=[]
- frontend flow:
  - /after -> /after/result -> /after/intake -> /after/draft 통과
  - copy 통과
  - print는 headless에서 window.print() 호출 검증, 실제 OS dialog는 발표 브라우저에서 육안 확인 권장
  - direct URL guard 통과:
    - /after/result state 없음 -> /after
    - /after/intake state 없음 -> /after
    - /after/draft state 없음 -> /after
- Web Storage:
  - raw user_statement, answer_response, case_intake, draft_response 저장 금지
  - active flow와 guard pages에서 localStorage/sessionStorage 0 확인 이력 있음

Free input 정책:
- preset 없음 + 직접 입력:
  - live /api/v1/answer
  - top_k=5
  - ef_search=100
- preset 버튼 클릭 후 문장 수정:
  - live /api/v1/answer
  - preset recommendedTopK 사용, 현재 top_k=10
  - ef_search=100
- SCN-004 관련 free input:
  - answer의 cited_articles / grounded chunks 기반 eligibility guard로 문서 타입 표시
  - wage-only -> 임금체불 진정서만
  - dismissal-only -> 부당해고 이유서만
  - combined -> 두 문서 타입
- SCN-001/SCN-005/범위 밖 free input:
  - answer-only
  - SCN-004 문서 선택 UI 미표시

Eval / QA 상태:
- eval source scope:
  - backend/data/law_chunks/all_chunks.json
  - selected_as_of=2026-04-11
  - current live chunk count=1722
- full 60 answer evidence report:
  - summary: eval/reports/answer_evidence_2026-04-20.summary.md
  - JSONL: eval/reports/answer_evidence_2026-04-20.jsonl
  - command:
    python eval/run_answer_evidence_report.py --top-k 5 --ef-search 100 --limit 60 --output eval/reports/answer_evidence_2026-04-20.jsonl
  - PASS: 44
  - PARTIAL: 16
  - FAIL: 0
  - expected point coverage: 135/153
  - citation grounding violation: 0
  - invalid raw/grounded context id: 0
  - timeout/provider/schema error: 0
- MVP 기준으로 acceptable입니다.
- PARTIAL 16건은 citation/retrieval/grounding failure가 아니라 expected point 일부 누락입니다.
- 후속 answer quality tuning 후보:
  - 법정 예외
  - 숫자/기간/상한
  - 보조 절차 의무
  - 복수 쟁점 답변 누락
- eval 전체를 document draft로 자동 연결하지 않습니다.
- draft 확장은 먼저 draft_candidate 분류 후 별도 document type/template 작업으로 진행합니다.

발표 전 기본 preflight:
```bash
bash scripts/demo_preflight.sh
```

preflight script는 다음을 확인합니다:
- main == origin/main
- PostgreSQL readiness
- conda env activation
- backend import
- backend/verify/check_document_draft.py
- frontend npm run build
- WSL Playwright Chromium smoke

preflight script는 하지 않는 일:
- DB start/stop
- backend/frontend dev server start
- process/port kill
- git add/commit/restore
- full 60 eval 실행

수동 서버 실행:
```bash
conda activate law_main_road
uvicorn backend.main:app --reload
```

```bash
cd frontend
npm run dev
```

브라우저 기준 URL:
- http://localhost:3000
- http://127.0.0.1:3000은 Next dev HMR cross-origin warning 이력이 있어 QA 기준 URL로 쓰지 않음

먼저 해야 할 일:
1. git status -sb로 origin/main과 clean/dirty 상태를 확인해주세요.
2. AGENTS.md, CLAUDE.md, backend/CLAUDE.md, frontend/CLAUDE.md를 읽고 금지 범위를 확인해주세요.
3. README.md, docs/ops/runbook.md, docs/demo/demo_scenario.md, docs/demo/presentation_notes.md를 읽고 demo/preflight/fallback 절차를 확인해주세요.
4. eval/README.md와 eval/reports/answer_evidence_2026-04-20.summary.md를 읽고 full 60 evidence 결과와 MVP acceptable 판단을 확인해주세요.
5. docs/product/before_flow.md, docs/product/bridge_flow.md, docs/product/after_flow.md, docs/planning/14_frontend_implementation_handoff.md를 읽고 SCN-001 확장 전 contract 조건을 확인해주세요.

절대 하지 말 것:
- SCN-004 freeze 기준을 흔드는 변경 금지
- SCN-005를 바로 구현하지 마세요. 사용자가 명시적으로 요청하면 별도 패치로만 진행하세요.
- SCN-001 document type / Before -> Bridge -> After 구현은 팀원 Before/Bridge contract 확인 전까지 금지
- /before, /bridge, Recovery 본 구현 금지
- backend API contract 임의 변경 금지
- retrieval/answer behavior 변경은 regression/evidence 계획 없이 금지
- scripts/demo_preflight.sh에 full 60 eval 추가 금지
- data/legalize-kr/ 수정 금지
- backend/data/law_chunks/ 직접 수정 금지
- raw user_statement, answer_response, case_intake, draft_response를 Web Storage에 저장 금지
- 문제가 발견되면 코드 수정 전에 실패 지점, 재현 절차, 원인을 먼저 보고
- 파일 수정이 필요하면 먼저 수정 범위를 보고

다음 작업 우선순위:
1. 사용자가 “제출/발표 전 확인”을 요청하면:
   - bash scripts/demo_preflight.sh
   - 필요 시 backend/frontend 수동 실행 후 http://localhost:3000/after에서 SCN-004-DEMO-FREEZE dry-run
   - SCN-001-BRIDGE-DEMO answer-only 확인
2. 사용자가 “팀원 Before-begin 코드가 준비됐다”고 하면:
   - 새 기능 구현 전에 contract만 먼저 확인
   - Before output schema 확인:
     - scenario_id
     - source_scenario 또는 preset_id
     - summary
     - risk_tags
     - extracted_terms
     - cited_articles
     - created_at
     - 개인정보/원문/OCR 이미지 포함 여부
   - raw 계약서 원문, OCR 이미지, 연락처 등 민감정보 저장 여부 확인
   - Bridge 최소 contract 초안과 After 연결 field를 문서화
   - contract 확정 전 SCN-001 frontend 연결 구현 금지
3. 사용자가 “eval 품질 개선”을 요청하면:
   - PARTIAL 16건을 먼저 유형 분류
   - answer prompt/planning 개선 후보를 제안
   - retrieval/citation/grounding clean 상태를 유지하는 방향으로 별도 패치
   - 변경 후 full 60 evidence report로 FAIL=0 유지 및 PARTIAL 감소 확인
4. 사용자가 “SCN-005 확장”을 요청하면:
   - SCN-004 freeze와 분리한 별도 패치로만 진행
   - 질문 1~2개, draft template 1개 이하, verifier/fixture 포함 여부부터 계획
5. 사용자가 “인프라 전환”을 요청하면:
   - 로컬 실행 재현성
   - .env / secret / credential 분리
   - backend 배포 방식
   - frontend 배포 방식
   - PostgreSQL + pgvector 운영 위치
   - Vertex AI 인증
   - demo용 최소 배포 또는 로컬 fallback
   - 비용/보안/장애 대응 문서화 순서로 진행

마지막 보고 형식:
- git 상태
- 읽은 문서
- 실행한 검증과 결과
- SCN-004 freeze 영향 여부
- 수정한 파일
- 커밋/푸시 여부
- 남은 리스크 또는 다음 권장 작업
```

## 참고

이 프롬프트는 현재 main 기준 새 세션을 빠르게 시작하기 위한 작업 메모다.
MVP 제출 기준으로는 SCN-004 freeze, SCN-001 answer-only bridge preset, full 60 eval evidence, demo preflight가 정리된 상태다.
다음 큰 기능 작업은 팀원 Before-begin 코드/contract가 준비된 뒤 SCN-001 Before/Bridge/After 연결 가능성을 검토하는 것이다.
