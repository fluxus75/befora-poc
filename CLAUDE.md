# CLAUDE.md

## 프로젝트 개요

### 목적
의료 사전 문진(Pre-appointment History Taking)을 위한 음성 기반 AI Agent PoC

### 핵심 성공 기준
1. 고령자 포함 사용자가 끊김 없이 음성 문진 완료
2. 문진 결과가 구조화된 데이터(JSON/Report)로 저장
3. 의사가 대시보드에서 검토·수정·확정 가능
4. WebRTC 음성 문진 평균 지연 ≤ 300ms

### SRD 버전
- POC_SRD: v0.2
- Implementation Plan: v0.2

---

## 아키텍처

### 핵심 원칙 (MUST)
```
Browser ── WebRTC (직접) ──> OpenAI Realtime API
   ▲
   │ ephemeral token 발급
   ▼
Server (FastAPI)
- 세션/권한 관리
- 로그/리포트 저장
- DSL 시나리오 실행
```

### 서버 역할
- ✅ Ephemeral token 발급
- ✅ 세션/권한/로그/리포트 관리
- ✅ DSL 시나리오 엔진 실행
- ❌ 오디오 중계 (금지)

---

## 개발 환경

### Package Manager
| 영역 | 도구 | 버전 |
|------|------|------|
| Frontend | pnpm | 8.x+ |
| Backend | uv | latest |
| 금지 | npm, yarn, pip 직접 사용 | - |

### 런타임
| 기술 | 버전 | 비고 |
|------|------|------|
| Node.js | 20.x LTS | Frontend |
| Python | 3.11+ | Backend |
| Chrome | 120+ | WebRTC 호환성 |

### 기술 스택

#### Frontend
- React 18 + TypeScript 5.x + Vite 5.x
- Zustand (상태 관리)
- Web Audio API + WebRTC

#### Backend
- FastAPI 0.110+
- Pydantic 2.x
- SQLite (PoC) → PostgreSQL (Phase 2)
- LangGraph (옵션, Scale-up 시)

#### 외부 서비스
- OpenAI Realtime API (음성 STT/TTS)
- HeyGen Streaming Avatar (옵션)
- Twilio SMS (Phase 2 이후)

---

## 프로젝트 명령어

### Frontend (apps/)
```bash
pnpm install                   # 의존성 설치
pnpm dev                       # 모든 앱 동시 실행
pnpm dev:web                   # web-client만
pnpm dev:dashboard             # doctor-dashboard만
pnpm build                     # 프로덕션 빌드
pnpm test                      # 테스트 실행
pnpm lint                      # ESLint 실행
```

### Backend (server/)
```bash
cd server
uv venv                        # 가상환경 생성
source .venv/bin/activate      # 활성화 (Windows: .venv\Scripts\activate)
cd ..                          # requirements.txt 없음; repo root에서 설치
uv pip install -e ".[dev]"     # pyproject.toml 기준 의존성 설치
uv run uvicorn main:app --reload --port 8000
uv run pytest                  # 테스트
```

### 검증 명령어
```bash
# Frontend 실행 확인
curl http://localhost:5173

# Backend Health Check
curl http://localhost:8000/health

# WebRTC 연결 테스트 (브라우저 콘솔)
# → Chrome 120+ 필수
```

---

## 코드 스타일

### TypeScript/React
- TypeScript strict mode 필수
- ESLint + Prettier 자동 실행
- 2 space 들여쓰기
- 컴포넌트: PascalCase
- 함수/변수: camelCase
- 상수: SCREAMING_SNAKE_CASE

### Python
- Black + isort + ruff
- Type hints 필수
- 4 space 들여쓰기
- Pydantic v2 for schemas
- 클래스: PascalCase
- 함수/변수: snake_case

---

## Git Workflow

### 브랜치 전략
- `main`: 프로덕션 (보호 브랜치)
- `develop`: 개발 통합
- `feature/*`: 기능 개발
- `hotfix/*`: 긴급 패치

### 커밋 컨벤션
```
타입(스코프): 설명

# 타입
feat, fix, docs, refactor, test, chore, security

# 스코프
web, dashboard, api, agent, auth, rtc, dsl

# 예시
feat(dsl): 증상 트랙 분기 로직 구현
fix(rtc): WebRTC 재연결 시 오디오 스트림 누수 수정
security(auth): ephemeral token 만료 시간 60초로 단축
```

### PR 체크리스트
- [ ] 단위 테스트 통과
- [ ] WebRTC 연결 테스트 (Chrome 120+)
- [ ] 마이크 권한 거부 시나리오 테스트
- [ ] 환경 변수 노출 없음
- [ ] PII 로깅 없음

---

## 보안 요구사항 (PoC 필수)

### 저장 시 보안
- At-rest encryption 적용
- 환자 식별 정보 ↔ 문진 내용 분리 저장

### 접근 통제 (RBAC)
| 역할 | 권한 |
|------|------|
| Admin | 전체 세션 조회, 사용자 관리 |
| Doctor | 배정된 세션 조회/편집/확정 |
| Reviewer | 읽기 전용 |

### 환경 변수 (커밋 금지)
```
OPENAI_API_KEY
HEYGEN_API_KEY
TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN
DATABASE_URL
JWT_SECRET
DB_ENCRYPTION_KEY
```

### 데이터 보존
- 기본 보존 기간: 30일 (또는 90일)
- PoC 종료 시 파기 절차 정의 필수

---

## Agent 오케스트레이션

### 전략: DSL 엔진 우선 + 추상화
```
Phase 2 (PoC)     → DSL 엔진으로 빠른 검증
ScenarioRunner    → 전환 비용 최소화 인터페이스
Phase 2+ (옵션)   → LangGraph 래핑 (필요 시)
```

### ScenarioRunner 인터페이스
```python
class ScenarioRunner(Protocol):
    def process(self, user_input: str) -> ScenarioResponse: ...
    def get_state(self) -> dict: ...
    def reset(self) -> None: ...
```

### DSL 시나리오 파일 (유지 필수)
| 파일 | 역할 |
|------|------|
| scenario.json | 정상 문진 흐름 DSL |
| emergency_keywords.json | 응급 감지 조건 |
| EMERGENCY_FLOW.json | 응급 대응 흐름 |

### 증상 트랙
- COGNITIVE, DIZZINESS, HEADACHE, TREMOR
- symptom_track 슬롯 기반 분기

---

## 구현 Phase 요약

| Phase | 목표 | 주요 태스크 |
|-------|------|------------|
| 1 | 환경 설정 | Monorepo, Frontend/Backend 초기화, 스키마 정의 |
| 2 | DSL 엔진 | 시나리오 로더, 슬롯 관리, 응급 감지, ScenarioRunner |
| 3 | 음성 연동 | WebRTC, Ephemeral Token, 오디오 UI, 복구 처리 |
| 4 | 의사 대시보드 | 인증, 세션 목록/상세, 편집/확정, 리포트 |
| 5 | 통합 테스트 | E2E 테스트, 보안 검증, 문서화 |

---

## 리스크 대응

| 리스크 | 대응 |
|--------|------|
| WebRTC 연결 불안정 | ICE candidate 최적화, TURN 서버 검토 |
| Realtime API 지연 | 모니터링 대시보드, 대체 TTS 검토 |
| 응급 키워드 미감지 | 키워드 지속 확장, Fallback 모델 |
| 고령자 마이크 어려움 | 텍스트 입력 대체 옵션 |
| DSL→LangGraph 전환 | ScenarioRunner 추상화로 비용 최소화 |

---

## 참고 문서
- docs/POC_SRD_v0.2.md
- docs/implementation_plan_v0.2.md
- server/scenarios/*.json
```
