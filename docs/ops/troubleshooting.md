# Troubleshooting Log

기록 기준:
- 같은 문제 2회 이상 반복
- 재사용 가치 있음
- 원인과 해결책이 명확함

자동 기록 금지.
필요하다고 판단될 때만 추가.

## 2026-04-20 Demo / QA Troubleshooting

### 1. Non-interactive shell에서 `conda activate` 실패

증상:

```text
CondaError: Run 'conda init' before 'conda activate'
```

발생 맥락:

- AI agent가 비대화형 shell에서 backend import smoke 또는 verify script를 실행할 때 발생할 수 있다.
- 사용자의 일반 WSL 터미널에서는 `conda activate law_main_road`가 동작해도, automation shell에서는 conda hook이 로드되지 않을 수 있다.

해결:

```bash
source /home/jongwon/anaconda3/etc/profile.d/conda.sh
conda activate law_main_road
python -c "from backend.main import app; print('import_ok')"
```

예방:

- `scripts/demo_preflight.sh`는 conda profile script를 먼저 source한 뒤 `conda activate law_main_road`를 실행한다.
- 새 automation script를 만들 때도 plain `conda activate`만 쓰지 말고 hook source를 포함한다.

### 2. `npm run build` 또는 Next dev 후 `frontend/next-env.d.ts`가 dirty로 남음

증상:

```diff
-import "./.next/types/routes.d.ts";
+import "./.next/dev/types/routes.d.ts";
```

발생 맥락:

- Next.js dev/build 과정에서 generated type import path가 바뀌며 git dirty가 생길 수 있다.
- 실제 코드 변경이 아니라 local generated state인 경우가 많다.

해결:

```bash
git diff -- frontend/next-env.d.ts
git checkout -- frontend/next-env.d.ts
git status -sb
```

예방:

- `npm run build` 후에는 항상 `git status -sb`를 확인한다.
- 의도한 변경이 아니라면 커밋에 포함하지 않는다.

### 3. `localhost:3000`에 stale Next dev server가 이미 떠 있음

증상:

- 새로 `npm run dev`를 실행하지 않았는데 `http://localhost:3000/after`가 응답한다.
- browser QA가 예상과 다르게 보이거나 이전 코드 상태를 보는 것처럼 느껴진다.

확인:

```bash
curl -I http://localhost:3000/after
```

대응:

- 이미 떠 있는 dev server가 같은 repo / 같은 frontend cwd에서 실행 중인지 확인한다.
- 발표 전에는 stale server가 남아 있지 않은 상태에서 backend/frontend를 깨끗하게 재시작하는 편이 안전하다.
- `scripts/demo_preflight.sh`는 dev server를 start/stop하지 않는다. preflight 통과 후 별도 터미널에서 수동 실행한다.

### 4. `127.0.0.1:3000`에서 Next dev HMR cross-origin warning 또는 route guard 재현 차이

증상:

- `http://127.0.0.1:3000` 접근 시 Next dev HMR cross-origin warning이 보인다.
- direct URL guard 또는 browser runtime QA가 `localhost` 기준과 다르게 재현될 수 있다.

해결:

- demo / browser QA 기준 URL은 `http://localhost:3000`으로 고정한다.
- `http://127.0.0.1:3000`은 QA 기준 URL로 쓰지 않는다.

### 5. WSL Playwright Chromium 실행 실패 또는 Windows Chrome CDP 우회로 시간 소모

증상:

- WSL에서 Playwright Chromium 실행 시 `libnss3`, `libasound2` 같은 system dependency 오류가 난다.
- AI agent가 Windows Chrome CDP / PowerShell 우회로 시간을 많이 쓰게 된다.

초기 설치:

```bash
cd frontend
npm install
npm install -D @playwright/test
npx playwright install-deps
npx playwright install chromium
```

주의:

- `npx playwright install-deps`는 `sudo` 권한이 필요할 수 있으므로 사용자가 직접 실행한다.
- `npx playwright install chromium` 전에 project dependencies가 설치되어 있지 않으면 Playwright가 warning을 띄울 수 있다. 먼저 `npm install`을 실행한다.

확인:

```bash
cd frontend
node -e "const { chromium } = require('@playwright/test'); (async () => { const browser = await chromium.launch({ headless: true }); const page = await browser.newPage(); await page.goto('data:text/html,<h1>ok</h1>'); console.log(await page.textContent('h1')); await browser.close(); })().catch((error) => { console.error(error); process.exit(1); });"
```

expected:

```text
ok
```

예방:

- WSL Playwright가 실패하면 Windows CDP / PowerShell 우회 전에 실패 원인과 필요한 사용자 조치를 먼저 보고한다.

### 6. `check_document_draft.py` 숫자와 browser fixed preset draft 숫자가 다름

증상:

- `python backend/verify/check_document_draft.py` 출력:
  - answer-derived wage fixture가 `cited_articles=3`
  - answer-derived unfair fixture가 `cited_articles=5`
- browser `SCN-004-DEMO-FREEZE` fixed path:
  - wage draft `cited_articles=2`, `source_context_ids=[5, 10]`
  - unfair draft `cited_articles=4`, `source_context_ids=[1, 2, 3, 4]`

원인:

- `check_document_draft.py`는 backend verify fixture 기준 smoke다.
- 발표용 `SCN-004-DEMO-FREEZE` browser path는 frontend fixed answer fixture 기준이다.

판정:

- 이 차이는 정상이다.
- backend draft contract smoke는 `check_document_draft.py`로 확인한다.
- 발표 demo freeze 기준은 browser dry-run fixed preset path 값으로 확인한다.

### 7. `scripts/demo_preflight.sh`가 `main != origin/main`에서 실패

증상:

- 로컬 commit이 `origin/main`보다 앞서 있을 때 preflight가 실패한다.

원인:

- preflight는 제출/발표 직전 재현성을 확인하기 위해 `main == origin/main`을 요구한다.

해결:

```bash
git status -sb
git log --oneline origin/main..HEAD
git push origin main
bash scripts/demo_preflight.sh
```

주의:

- push 전 상태에서 preflight가 실패하는 것은 정상이다.

### 8. Headless browser print 검증과 실제 OS print dialog 차이

증상:

- Playwright headless QA에서는 print dialog가 실제로 보이지 않는다.

원인:

- headless browser에서는 실제 OS print dialog가 아니라 `window.print()` 호출 여부만 검증한다.

대응:

- 자동 QA에서는 `window.print()` 호출을 확인한다.
- 발표 직전 실제 브라우저에서 print 버튼을 한 번 눌러 OS print dialog가 뜨는지 육안 확인한다.

### 9. Full 60 answer evidence에서 `PARTIAL`이 남음

증상:

- `eval/run_answer_evidence_report.py` full 60 결과:
  - `PASS=44`
  - `PARTIAL=16`
  - `FAIL=0`
  - expected point coverage `135/153`

판정:

- MVP 기준 acceptable이다.
- `PARTIAL` 16건은 citation miss, retrieval failure, grounding violation, context id invalid가 아니다.
- 주된 원인은 expected point 일부 누락이며, 법정 예외, 숫자/기간/상한, 보조 절차 의무, 복수 쟁점 답변 누락 유형이다.

후속:

- answer prompt / answer planning tuning 후보로 분리한다.
- SCN-004 demo freeze나 presentation fixed fixture의 blocker로 보지 않는다.
- 개선 시에는 full 60 evidence report를 다시 실행해 `FAIL=0` 유지와 `PARTIAL` 감소 여부를 비교한다.

### 10. Root `.gitignore`를 frontend 하위에서 stage하려고 할 때 경로 혼동

증상:

- `frontend/` 디렉터리에서 `git add .gitignore`를 실행했는데 root `.gitignore`가 stage되지 않는다.

원인:

- 현재 작업 디렉터리가 `frontend/`라서 `.gitignore` 경로가 root가 아니라 `frontend/.gitignore`로 해석된다.

해결:

```bash
cd /home/jongwon/personal_project/law_main_road
git add .gitignore
```

또는:

```bash
cd frontend
git add ../.gitignore
```

예방:

- repo-root 파일을 stage / commit할 때는 repo root에서 실행한다.
