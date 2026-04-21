# architecture_option4_spec.md
## K-Labor Shield — Target Deployment Architecture / Option 4 (v2)

> ⚠️ **주의:** 이 문서는 **현재 로컬 MVP(SCN-004-DEMO-FREEZE, SCN-001-BRIDGE-DEMO)의 구조가 아닌, Option 4 후속 클라우드 배포 목표 아키텍처**입니다.
> 현재 구현 범위와 이 목표 아키텍처를 반드시 구분하십시오. → [6절 참고](#6-현재-mvp와-목표-아키텍처-구분)

---

## 1. v2 수정 요약

| 항목 | v1 | v2 (현재) |
|------|----|-----------|
| Client 그룹 박스 | 없음 (User 단독 배치) | Client 그룹 박스 추가 |
| Backend API 레이블 | 한 줄 나열 (과밀) | 4줄 구조화 (badge + 제목 + 기능 2줄) |
| Supporting Services 정렬 | 불균등 크기/간격 | 5박스 동일 크기(280×148), 균등 간격(80px) |
| Legend | 없음 | 하단 중앙 범례 박스 추가 |
| GCP 서비스 시각화 | 순수 텍스트 레이블 | HTML 컬러 badge (서비스명 칩) 추가 |
| Local LLM Server | 오렌지 강조 박스 | Compute Engine GPU VM badge 추가 후 오렌지 강조 박스 유지 |
| 전체 여백 | 1654×1169 | 1900×1360 (캔버스 확대, 그룹 간 여백 증가) |

### GCP 서비스 아이콘 접근 방식 결정

`mxgraph.gcp2.*` 아이콘 셀을 사용하면 GCP 라이브러리 미로드 시 XML import 불안정 우려가 있다. 따라서 **HTML `<span>` badge 방식**을 채택했다.

- 각 서비스 박스 레이블 최상단에 GCP 서비스명 colored chip 표시
- 라이브러리 의존성 없이 항상 렌더링
- 서비스 식별이 텍스트 레벨에서 명확

| 서비스 | Badge 색상 | 이유 |
|--------|-----------|------|
| Cloud Run (Frontend / Backend) | `#4285F4` Google Blue | 공식 Cloud Run 색상 |
| Cloud SQL | `#4285F4` Google Blue | Compute 계열 |
| Vertex AI | `#7B5EA7` Purple | AI/ML 계열 |
| Cloud Storage | `#F57C00` Orange | Storage 계열 |
| Secret Manager | `#34A853` Green | Security/IAM 계열 |
| Cloud Run Jobs | `#4285F4` Google Blue | Cloud Run 계열 |
| Workflows | `#0097A7` Teal | Orchestration 계열 |
| Cloud Logging | `#558B2F` Dark Green | Observability 계열 |
| Compute Engine (Local LLM) | `#DB4437` Red | Compute/GPU 계열 |

---

## 2. 최종 레이아웃 구조

```
캔버스: 1900 × 1360

┌─────────────────────── GCP (x=10, y=10, w=1880, h=1330) ───────────────────────┐
│                                                                                  │
│  ┌──────────────────── Client (x=30, y=45, w=1840, h=135) ──────────────────┐  │
│  │                       User / Browser (centered)                          │  │
│  └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
│  ┌──────────────── Application (x=30, y=215, w=1840, h=445) ───────────────┐   │
│  │                 Frontend (x=730, y=248, w=380, h=150)                   │   │
│  │  ┌───────────────────── Backend API (x=155, y=432, w=1530, h=200) ────┐ │   │
│  │  │  [Cloud Run/FastAPI badge]  Backend API                            │ │   │
│  │  │  Retrieval · Grounded Answer Orchestration · Document Draft        │ │   │
│  │  │  Citation Validation · Model Routing                               │ │   │
│  │  └───────────────────────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│  ┌──────────────── Data & AI (x=30, y=698, w=1840, h=272) ────────────────┐    │
│  │  Cloud SQL (x=80)   Vertex AI (x=790)   Local LLM Server (x=1490)     │    │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│  ┌────────── Supporting Services (x=30, y=1012, w=1840, h=210) ──────────┐     │
│  │  SecretMgr(90) CloudStorage(450) CloudRunJobs(810) Workflows(1170)    │     │
│  │  CloudLogging(1530)   ← 균등 크기 280×148, 간격 80px                  │     │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│              [ Legend: ━━━ Primary flow  ╌╌╌ Supporting flow ]                 │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. 박스 내부 문구 정리 (v2)

| ID | 박스 | Badge | 제목 | 설명 |
|----|------|-------|------|------|
| 3 | User / Browser | — | User / Browser | — |
| 11 | Frontend | Cloud Run (Blue) | Frontend | 사용자 입력 · 결과 화면 · 데모 시나리오 UI |
| 12 | Backend API | Cloud Run / FastAPI (Blue) | Backend API | Retrieval · Grounded Answer Orchestration · Document Draft / Citation Validation · Model Routing |
| 21 | Cloud SQL | Cloud SQL (Blue) | PostgreSQL | pgvector · law_chunks |
| 22 | Vertex AI | Vertex AI (Purple) | Managed Model Path | Gemini API |
| 23 | Local LLM Server | Compute Engine GPU VM (Red) | Local LLM Server | Ollama + Qwen · Warm State · Self-hosted Inference |
| 31 | Secret Manager | Secret Manager (Green) | API Keys | DB Secrets |
| 32 | Cloud Storage | Cloud Storage (Orange) | Files · Outputs | Intermediate Results |
| 33 | Cloud Run Jobs | Cloud Run Jobs (Blue) | Batch Jobs | Scheduled Tasks |
| 34 | Workflows | Workflows (Teal) | Orchestration | Pipeline Flow |
| 35 | Cloud Logging | Cloud Logging (Dark Green) | Logs · Metrics | Health Check |

---

## 4. Mermaid 코드

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'fontSize': '13px'}}}%%
flowchart TB

    subgraph GCP["☁️  Google Cloud Platform — Region: asia-northeast3 (Seoul)"]

        subgraph CLIENT["Client"]
            User(["👤 User / Browser"])
        end

        subgraph APP["Application"]
            direction TB
            Frontend["🔵 Cloud Run\n**Frontend**\n사용자 입력 · 결과 화면 · 데모 시나리오 UI"]
            BackendAPI["🔵 Cloud Run / FastAPI\n**Backend API**\nRetrieval · Grounded Answer Orchestration · Document Draft\nCitation Validation · Model Routing"]
        end

        subgraph DATA["Data & AI"]
            direction LR
            CloudSQL["🔵 Cloud SQL\n**PostgreSQL**\npgvector · law_chunks"]
            VertexAI["🟣 Vertex AI\n**Managed Model Path**\nGemini API"]
            LocalLLM["🔴 Compute Engine GPU VM\n**Local LLM Server**\nOllama + Qwen\nWarm State · Self-hosted Inference"]
        end

        subgraph SUP["Supporting Services"]
            direction LR
            SecretMgr["🟢 Secret Manager\n**API Keys**\nDB Secrets"]
            CloudStorage["🟠 Cloud Storage\n**Files · Outputs**\nIntermediate Results"]
            CloudRunJobs["🔵 Cloud Run Jobs\n**Batch Jobs**\nScheduled Tasks"]
            Workflows["🔵 Workflows\n**Orchestration**\nPipeline Flow"]
            Logging["🟩 Cloud Logging\n**Logs · Metrics**\nHealth Check"]
        end

    end

    User       -->|HTTPS|                       Frontend
    Frontend   -->|API Call / HTTPS|            BackendAPI
    BackendAPI -->|SQL / Vector Search|         CloudSQL
    BackendAPI -->|Managed Model Path|          VertexAI
    BackendAPI -->|Self-hosted Inference Route| LocalLLM

    BackendAPI -.->|Secrets / Credentials|   SecretMgr
    BackendAPI -.->|Files / Artifacts|       CloudStorage
    BackendAPI -.->|Batch Trigger|           CloudRunJobs
    Workflows  -.->|Orchestration|           BackendAPI
    Workflows  -.->|Job Orchestration|       CloudRunJobs
    BackendAPI -.->|App Logs / Metrics|      Logging
    LocalLLM   -.->|Inference Logs / Health| Logging

    style BackendAPI fill:#D6EAF8,stroke:#2874A6,stroke-width:3px,color:#000000
    style LocalLLM   fill:#FFF3E0,stroke:#E65100,stroke-width:3px,color:#000000
    style CLIENT fill:#F5F5F5,stroke:#9E9E9E,stroke-width:2px,color:#555555
    style APP    fill:#F0EDFF,stroke:#7B5EA7,stroke-width:2px,color:#7B5EA7
    style DATA   fill:#E8F5E9,stroke:#2E7D32,stroke-width:2px,color:#2E7D32
    style SUP    fill:#FFF9E6,stroke:#B7860B,stroke-width:2px,color:#B7860B
    style GCP    fill:#EBF3FB,stroke:#4285F4,stroke-width:2px,color:#4285F4
```

---

## 5. ASCII 텍스트 다이어그램

```
┌──────────────────────────────────────────────────────────────────────────┐
│  Google Cloud Platform  /  Region: asia-northeast3 (Seoul)               │
│                                                                          │
│  ┌──────────────────── [Client] ──────────────────────────────────────┐  │
│  │                   ◯  User / Browser                                │  │
│  └────────────────────────────┬───────────────────────────────────────┘  │
│                               │ HTTPS                                    │
│  ┌────────────────── [Application] ──────────────────────────────────┐   │
│  │            ┌──────── [Cloud Run] Frontend ────────┐               │   │
│  │            │  사용자 입력 · 결과 화면 · 데모 UI    │               │   │
│  │            └─────────────────┬──────────────────┘                │   │
│  │                              │ API Call / HTTPS                   │   │
│  │  ╔═══════════════ [Cloud Run / FastAPI] Backend API ════════════╗  │   │
│  │  ║  Retrieval · Grounded Answer Orchestration · Document Draft  ║  │   │
│  │  ║  Citation Validation · Model Routing                         ║  │   │
│  │  ╚══════════╤═════════════════╤═══════════════════════╤═════════╝  │   │
│  └─────────────┼─────────────────┼───────────────────────┼────────────┘  │
│                │                 │                        │               │
│  SQL/Vector    │  Managed Model  │    Self-hosted         │               │
│  Search        │  Path           │    Inference Route     │               │
│  ┌─────────────────────────────────────── [Data & AI] ──────────────┐    │
│  │  ┌──────────────┐   ┌──────────────┐   ┌════════════════════════┐│    │
│  │  │  Cloud SQL   │   │  Vertex AI   │   ║  Local LLM Server      ║│    │
│  │  │  PostgreSQL  │   │  Managed     │   ║  Compute Engine GPU VM ║│    │
│  │  │  pgvector    │   │  Gemini API  │   ║  Ollama + Qwen         ║│    │
│  │  └──────────────┘   └──────────────┘   ╚════════════════════════╝│    │
│  └───────────────────────────────────────────────────────────────────┘    │
│                                                                           │
│  ┌──────────────────── [Supporting Services] ────────────────────────┐   │
│  │  ┌────────┐ ┌────────┐ ┌──────────┐ ┌─────────┐ ┌─────────────┐  │   │
│  │  │Secret  │ │Cloud   │ │Cloud Run │ │Workflows│ │Cloud Logging│  │   │
│  │  │Manager │ │Storage │ │Jobs      │ │         │ │/ Monitoring │  │   │
│  │  └────────┘ └────────┘ └──────────┘ └─────────┘ └─────────────┘  │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│         [ Legend:  ━━━ Primary flow  │  ╌╌╌ Supporting flow ]            │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 6. 현재 MVP와 목표 아키텍처 구분

| 구분 | 현재 로컬 MVP | Option 4 목표 아키텍처 (이 문서) |
|------|--------------|----------------------------------|
| 상태 | **완료** (SCN-004-DEMO-FREEZE / SCN-001-BRIDGE-DEMO) | **후속 클라우드 배포 계획** |
| Frontend | 로컬 실행 (localhost) | Cloud Run 또는 Managed Hosting |
| Backend API | 로컬 FastAPI | Cloud Run |
| LLM 추론 | 로컬 Qwen3-8B + vLLM | Vertex AI (Gemini) + Local LLM Server 병행 라우팅 |
| 데이터 | 로컬 PostgreSQL + pgvector | Cloud SQL for PostgreSQL + pgvector |
| 관찰성 | 없음 | Cloud Logging / Monitoring |
| 배치 작업 | 없음 | Cloud Run Jobs + Workflows |
| 시크릿 관리 | .env 파일 | Secret Manager |

> 강사님께 설명 시 반드시 **"현재 로컬 MVP가 아닌 Option 4 배포 목표 구조"** 임을 먼저 명시하십시오.

---

## 7. 연결 관계 전체 목록

### 핵심 흐름 (실선 ━━━)
| From | To | Label |
|------|----|-------|
| User / Browser | Frontend | HTTPS |
| Frontend | Backend API | API Call / HTTPS |
| Backend API | Cloud SQL (PostgreSQL) | SQL / Vector Search |
| Backend API | Vertex AI | Managed Model Path |
| Backend API | Local LLM Server | Self-hosted Inference Route |

### 보조 연결 (점선 ╌╌╌)
| From | To | Label |
|------|----|-------|
| Backend API | Secret Manager | Secrets / Credentials |
| Backend API | Cloud Storage | Files / Artifacts |
| Backend API | Cloud Run Jobs | Batch Trigger |
| Workflows | Backend API | Orchestration |
| Workflows | Cloud Run Jobs | Job Orchestration |
| Backend API | Cloud Logging / Monitoring | App Logs / Metrics |
| Local LLM Server | Cloud Logging / Monitoring | Inference Logs / Health |

---

## 8. draw.io import 가이드

1. app.diagrams.net 또는 draw.io 데스크탑 앱 실행
2. `File → Import from → Device` 선택
3. `architecture_option4.drawio` 업로드
4. 모든 셀은 `parent="1"` 평면 구조 → 개별 선택/이동/수정 가능
5. GCP 서비스명은 HTML badge 방식으로 표현되므로 별도 라이브러리 로드 불필요

---

## 9. 색상 범례

| 요소 | 색상 코드 | 의미 |
|------|----------|------|
| GCP 외곽 | `#EBF3FB` bg / `#4285F4` border | Google Cloud 공식 색상 |
| Client 그룹 | `#F5F5F5` bg / `#9E9E9E` border | 외부 사용자 계층 |
| Application 그룹 | `#F0EDFF` bg / `#7B5EA7` border | 애플리케이션 계층 |
| Data & AI 그룹 | `#E8F5E9` bg / `#2E7D32` border | 데이터/AI 계층 |
| Supporting 그룹 | `#FFF9E6` bg / `#B7860B` border | 보조 서비스 계층 |
| Backend API 강조 | `#D6EAF8` bg / `#2874A6` border (3px) | 중앙 오케스트레이터 강조 |
| Local LLM 강조 | `#FFF3E0` bg / `#E65100` border (3px) | GPU 분리 계층 강조 |
