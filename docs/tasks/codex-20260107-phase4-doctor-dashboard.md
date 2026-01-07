# Task: Phase 4 - 의사 대시보드 구현

## 1. Goal (목표)
의사가 완료된 문진 세션을 조회하고, 수집된 슬롯 데이터를 검토·수정·확정할 수 있는 웹 대시보드 구축

## 2. Phase & Context (단계 및 맥락)
- **Phase**: Phase 4 (의사 대시보드)
- **Related Docs**:
  - [implementation_plan_v0.2.md](../../SRD/implementation_plan_v0.2.md) - Section 6
  - [POC_SRD_v0.2.md](../../SRD/POC_SRD_v0.2.md)
- **Affected Areas**:
  - [x] Frontend - doctor-dashboard (새로 생성)
  - [x] Backend - FastAPI server (API 추가)
  - [x] Shared - schemas (확장)
  - [ ] DSL - scenarios/*.json

## 3. Scope (범위)

### 수정 가능한 파일/폴더
**Frontend (새로 생성):**
- `apps/doctor-dashboard/` - 전체 (React 18 + TypeScript + Vite)
  - `src/pages/` - 페이지 컴포넌트
  - `src/components/` - 공통 컴포넌트
  - `src/stores/` - Zustand 상태 관리
  - `src/lib/` - API 클라이언트
  - `src/types/` - TypeScript 타입 정의

**Backend (확장):**
- `server/api/` - 새로운 라우터 추가
  - `auth.py` - 인증/권한 API
  - `sessions.py` - 세션 조회/수정 API
  - `reports.py` - 리포트 생성 API
- `server/db/` - 데이터베이스 스키마 확장
  - `database.py` - 테이블 생성 로직
  - `models.py` - (새로 생성) ORM 모델

**Shared (확장):**
- `shared/schemas/` - DTO 추가
  - `auth.py` - (새로 생성) 인증 스키마
  - `session.py` - 확장 (상세 정보 포함)
  - `report.py` - (새로 생성) 리포트 스키마

### 금지 영역
- `.env` 파일 직접 수정 금지 (`.env.example`만 수정)
- `apps/web-client/` - 환자용 클라이언트는 수정 금지
- `server/scenarios/*.json` - DSL 시나리오 수정 금지
- `server/agents/` - 기존 DSL 엔진 수정 금지

## 4. Constraints (제약 조건)

### 아키텍처
- [x] doctor-dashboard는 별도 Vite 앱으로 구성 (web-client와 독립)
- [x] Backend는 RESTful API 제공 (GraphQL 사용 안 함)
- [x] 데이터베이스는 SQLite 사용 (PoC 단계)
- [x] 인증은 간단한 세션 기반 (JWT 또는 쿠키)

### 스타일
- [x] TypeScript strict mode, 2 space 들여쓰기
- [x] Python: 4 space, type hints 필수, snake_case
- [x] 컴포넌트: PascalCase, 함수/변수: camelCase (TS)
- [x] ESLint + Prettier (Frontend), Black + ruff (Backend)

### 성능/보안
- [x] **RBAC 구현 필수**: Admin, Doctor, Reviewer 역할 구분
- [x] **At-rest encryption**: 민감 데이터 암호화 저장
- [x] **PII 로깅 금지**: 환자 식별 정보 로그 남기지 않음
- [x] **CSRF 보호**: 수정/삭제 작업에 토큰 검증
- [x] SQL Injection 방지 (ORM 사용 또는 parameterized query)
- [x] XSS 방지 (입력 sanitization)

## 5. Acceptance Criteria (완료 조건)

### 기능
- [ ] **로그인**: Admin/Doctor/Reviewer 역할로 로그인 가능
- [ ] **세션 목록**: 문진 완료된 세션 리스트 조회 (페이지네이션)
- [ ] **세션 상세**: 개별 세션의 슬롯 데이터, 대화 로그 확인
- [ ] **슬롯 편집**: Doctor가 슬롯 값 수정 및 메모 추가
- [ ] **확정**: Doctor가 검토 완료 상태로 변경 (상태: reviewed → confirmed)
- [ ] **리포트 출력**: PDF 또는 프린터블 HTML 생성

### 권한
- [ ] **Admin**: 모든 세션 조회, 사용자 관리 가능
- [ ] **Doctor**: 배정된 세션만 조회/편집/확정
- [ ] **Reviewer**: 모든 세션 읽기 전용

### 보안
- [ ] 로그인하지 않은 사용자는 대시보드 접근 불가 (리다이렉트)
- [ ] Reviewer는 편집 버튼 비활성화
- [ ] 환자 식별 정보(patient_id)와 문진 내용(slots) 분리 저장
- [ ] At-rest encryption 적용 확인

### 테스트
- [ ] 단위 테스트: API 엔드포인트 테스트 (pytest)
- [ ] 통합 테스트: 로그인 → 세션 조회 → 편집 → 확정 플로우
- [ ] E2E 테스트: Playwright/Cypress로 UI 플로우 검증

## 6. Steps (구현 순서)

### Step 1: 데이터베이스 스키마 설계 및 생성
- 테이블 설계:
  - `users` - 사용자 정보 (id, username, password_hash, role)
  - `sessions` - 문진 세션 (id, patient_id_encrypted, status, created_at, completed_at, assigned_doctor_id, reviewed_at, confirmed_at)
  - `session_slots` - 슬롯 데이터 (session_id, slot_key, slot_value_encrypted)
  - `session_logs` - 대화 로그 (session_id, turn_index, user_input, agent_response, timestamp)
  - `session_notes` - 의사 메모 (session_id, doctor_id, note, created_at)
- 파일:
  - `server/db/models.py` (새로 생성)
  - `server/db/database.py` (테이블 생성 로직 추가)
  - `shared/schemas/session.py` (SessionDetail, SessionListItem 추가)
  - `shared/schemas/auth.py` (새로 생성 - LoginRequest, User, Role)
  - `shared/schemas/report.py` (새로 생성 - ReportData)

### Step 2: Backend API - 인증 시스템
- 간단한 세션 기반 인증 구현 (또는 JWT)
- 엔드포인트:
  - `POST /api/auth/login` - 로그인
  - `POST /api/auth/logout` - 로그아웃
  - `GET /api/auth/me` - 현재 사용자 정보
- RBAC 미들웨어 구현 (role 검증)
- 파일:
  - `server/api/auth.py` (새로 생성)
  - `server/auth/` - 인증/권한 유틸리티
  - `server/main.py` (라우터 등록)

### Step 3: Backend API - 세션 조회 및 관리
- 엔드포인트:
  - `GET /api/sessions` - 세션 목록 (페이지네이션, 필터링)
  - `GET /api/sessions/{session_id}` - 세션 상세 (슬롯 + 로그)
  - `PATCH /api/sessions/{session_id}/slots` - 슬롯 수정 (Doctor만)
  - `POST /api/sessions/{session_id}/notes` - 메모 추가 (Doctor만)
  - `PATCH /api/sessions/{session_id}/status` - 상태 변경 (Doctor: confirm, Admin: assign)
- 파일:
  - `server/api/sessions.py` (새로 생성)
  - `server/services/session_store.py` (확장 - DB 연동)

### Step 4: Backend API - 리포트 생성
- 엔드포인트:
  - `GET /api/sessions/{session_id}/report` - 리포트 데이터 조회
  - `GET /api/sessions/{session_id}/report/pdf` - PDF 생성 (옵션)
  - `GET /api/sessions/{session_id}/report/html` - 프린터블 HTML
- 파일:
  - `server/api/reports.py` (새로 생성)
  - `server/services/report_generator.py` (새로 생성)

### Step 5: Frontend - doctor-dashboard 초기화
- Vite + React 18 + TypeScript 설정
- 패키지 설치:
  - react, react-dom, react-router-dom
  - zustand (상태 관리)
  - axios (API 클라이언트)
  - (옵션) UI 라이브러리 (shadcn/ui, MUI, Ant Design 등)
- 폴더 구조:
  ```
  apps/doctor-dashboard/
  ├─ src/
  │  ├─ pages/
  │  │  ├─ LoginPage.tsx
  │  │  ├─ SessionListPage.tsx
  │  │  ├─ SessionDetailPage.tsx
  │  │  └─ NotFoundPage.tsx
  │  ├─ components/
  │  │  ├─ Header.tsx
  │  │  ├─ SessionCard.tsx
  │  │  ├─ SlotEditor.tsx
  │  │  ├─ SessionLogs.tsx
  │  │  └─ ReportViewer.tsx
  │  ├─ stores/
  │  │  ├─ authStore.ts
  │  │  └─ sessionStore.ts
  │  ├─ lib/
  │  │  └─ api.ts
  │  ├─ types/
  │  │  └─ index.ts
  │  ├─ App.tsx
  │  └─ main.tsx
  ├─ package.json
  ├─ vite.config.ts
  └─ tsconfig.json
  ```
- 파일:
  - `apps/doctor-dashboard/package.json`
  - `apps/doctor-dashboard/vite.config.ts`
  - `apps/doctor-dashboard/tsconfig.json`

### Step 6: Frontend - 인증 및 라우팅
- React Router 설정
- Protected Route (로그인 필요)
- 인증 Store (Zustand)
- 로그인 페이지 UI
- 파일:
  - `apps/doctor-dashboard/src/App.tsx`
  - `apps/doctor-dashboard/src/pages/LoginPage.tsx`
  - `apps/doctor-dashboard/src/stores/authStore.ts`
  - `apps/doctor-dashboard/src/lib/api.ts`

### Step 7: Frontend - 세션 목록 및 상세 페이지
- 세션 목록 페이지:
  - 테이블 또는 카드 형식
  - 상태별 필터 (active, completed, emergency_terminated, reviewed, confirmed)
  - 페이지네이션
  - Doctor는 본인 배정 세션만, Admin/Reviewer는 전체
- 세션 상세 페이지:
  - 슬롯 데이터 표시
  - 대화 로그 타임라인
  - 메모 영역
  - 상태 변경 버튼 (확정)
- 파일:
  - `apps/doctor-dashboard/src/pages/SessionListPage.tsx`
  - `apps/doctor-dashboard/src/pages/SessionDetailPage.tsx`
  - `apps/doctor-dashboard/src/components/SessionCard.tsx`
  - `apps/doctor-dashboard/src/components/SlotEditor.tsx`
  - `apps/doctor-dashboard/src/components/SessionLogs.tsx`
  - `apps/doctor-dashboard/src/stores/sessionStore.ts`

### Step 8: Frontend - 슬롯 편집 및 리포트
- 슬롯 편집 UI:
  - 인라인 편집 또는 모달
  - 저장/취소 버튼
  - Reviewer는 읽기 전용
- 리포트 뷰어:
  - 프린터블 HTML 또는 PDF 다운로드
- 파일:
  - `apps/doctor-dashboard/src/components/SlotEditor.tsx` (확장)
  - `apps/doctor-dashboard/src/components/ReportViewer.tsx`

### Step 9: 통합 테스트
- Backend:
  - pytest로 API 엔드포인트 테스트
  - RBAC 권한 테스트 (Doctor가 타인 세션 편집 시도 → 403)
- Frontend:
  - Playwright/Cypress로 E2E 테스트
  - 시나리오: 로그인 → 세션 목록 → 상세 조회 → 편집 → 확정
- 파일:
  - `server/tests/test_auth.py` (새로 생성)
  - `server/tests/test_sessions_api.py` (새로 생성)
  - `apps/doctor-dashboard/e2e/` (새로 생성)

### Step 10: 문서화 및 배포 준비
- README 업데이트 (doctor-dashboard 실행 방법)
- 환경 변수 추가 (`.env.example`)
  - `DASHBOARD_PORT=5174`
  - `DB_ENCRYPTION_KEY=...` (at-rest encryption용)
  - `JWT_SECRET=...` (인증용)
- 파일:
  - `README.md` (업데이트)
  - `.env.example` (업데이트)

## 7. Commands (실행 명령)

### 개발 서버
```bash
# Frontend - doctor-dashboard
cd apps/doctor-dashboard
pnpm install
pnpm dev                    # http://localhost:5174

# Frontend - web-client (환자용, 참고용)
cd apps/web-client
pnpm dev                    # http://localhost:5173

# Backend
cd server
source .venv/bin/activate   # Windows: .venv\Scripts\activate
uv run uvicorn main:app --reload --port 8000
```

### 데이터베이스 초기화
```bash
# SQLite 초기화 (테이블 생성)
cd server
uv run python -m db.database   # 또는 별도 init 스크립트

# 테스트 데이터 생성 (선택)
uv run python -m fixtures.seed_data
```

### 테스트
```bash
# Backend 테스트
cd server
uv run pytest                           # 전체
uv run pytest tests/test_auth.py        # 인증
uv run pytest tests/test_sessions_api.py # 세션 API

# Frontend 테스트 (E2E)
cd apps/doctor-dashboard
pnpm test:e2e              # Playwright 실행
```

### 린트 & 포맷
```bash
# Frontend
cd apps/doctor-dashboard
pnpm lint                  # ESLint
pnpm lint:fix              # 자동 수정
pnpm format                # Prettier

# Backend
cd server
uv run black .
uv run ruff check --fix .
uv run isort .
```

### 빌드
```bash
# doctor-dashboard 프로덕션 빌드
cd apps/doctor-dashboard
pnpm build                 # dist/ 생성
pnpm preview               # 빌드 결과 미리보기
```

## 8. Security Checklist (보안 체크리스트)

### 인증/권한
- [ ] 로그인 없이 대시보드 접근 시 리다이렉트
- [ ] RBAC 미들웨어 적용 (Admin/Doctor/Reviewer)
- [ ] Doctor는 배정된 세션만 접근 가능
- [ ] Reviewer는 편집 불가 (읽기 전용)
- [ ] 세션 토큰 또는 JWT 유효 시간 설정 (예: 8시간)

### 데이터 보호
- [ ] **At-rest encryption**: `patient_id`, `slot_value` 암호화 저장
- [ ] **PII 로깅 금지**: 환자 이름, 주민번호 등 로그 미포함
- [ ] **데이터 분리**: 식별 정보 ↔ 문진 내용 별도 테이블
- [ ] 암호화 키는 환경 변수 (`DB_ENCRYPTION_KEY`)에서 로드

### 입력 검증
- [ ] SQL Injection 방지 (ORM 사용 또는 parameterized query)
- [ ] XSS 방지 (입력 sanitization, React 자동 escaping 활용)
- [ ] CSRF 토큰 검증 (POST/PATCH/DELETE 요청)

### 환경 변수
- [ ] `.env` 파일 커밋 금지 (`.gitignore` 확인)
- [ ] 환경 변수 하드코딩 없음
- [ ] `.env.example` 업데이트 (키 이름만, 값은 플레이스홀더)

### 기타
- [ ] HTTPS 사용 (프로덕션 배포 시)
- [ ] CORS 설정 (doctor-dashboard 도메인만 허용)
- [ ] Rate limiting 고려 (API 남용 방지)

## 9. Output Format (PR 생성 시)

### PR 제목
```
feat(dashboard): Phase 4 의사 대시보드 구현
```

### PR 본문 템플릿
```markdown
## Summary
- 의사 대시보드 앱 추가 (`apps/doctor-dashboard/`)
- 인증 시스템 (Admin/Doctor/Reviewer 역할 기반)
- 세션 조회/편집/확정 기능
- 리포트 생성 및 출력
- RBAC 및 At-rest encryption 적용

## Changes
**Frontend:**
- Added: `apps/doctor-dashboard/` - React 18 + TypeScript + Vite
- Added: `apps/doctor-dashboard/src/pages/` - 로그인, 세션 목록/상세 페이지
- Added: `apps/doctor-dashboard/src/components/` - SlotEditor, ReportViewer 등

**Backend:**
- Added: `server/api/auth.py` - 인증 API
- Added: `server/api/sessions.py` - 세션 조회/수정 API
- Added: `server/api/reports.py` - 리포트 생성 API
- Added: `server/db/models.py` - 데이터베이스 모델
- Modified: `server/db/database.py` - 테이블 생성 로직
- Modified: `server/main.py` - 라우터 등록

**Shared:**
- Added: `shared/schemas/auth.py` - 인증 스키마
- Modified: `shared/schemas/session.py` - SessionDetail, SessionListItem 추가
- Added: `shared/schemas/report.py` - ReportData 스키마

## Test Plan
- [ ] Backend 단위 테스트: `pytest tests/test_auth.py`, `tests/test_sessions_api.py`
- [ ] RBAC 권한 테스트: Doctor가 타인 세션 접근 시 403
- [ ] E2E 테스트: 로그인 → 세션 목록 → 상세 → 편집 → 확정 플로우
- [ ] 암호화 확인: SQLite DB에서 `patient_id`, `slot_value` 암호화 상태 확인

## Security Review
- [ ] At-rest encryption 적용 (`DB_ENCRYPTION_KEY`)
- [ ] RBAC 미들웨어 적용 (Admin/Doctor/Reviewer)
- [ ] PII 로깅 없음
- [ ] 환경 변수 노출 없음
- [ ] CSRF 토큰 검증 (수정/삭제 작업)
- [ ] SQL Injection, XSS 방지

## Acceptance Criteria
- [ ] 로그인 후 세션 목록 조회 가능
- [ ] 세션 상세에서 슬롯 데이터 확인 가능
- [ ] Doctor가 슬롯 수정 및 메모 추가 가능
- [ ] Reviewer는 읽기 전용
- [ ] 확정 버튼 클릭 시 상태 변경 (reviewed → confirmed)
- [ ] 리포트 HTML 출력 가능

## Related Issues
Closes #[Phase 4 issue number]
Refs: POC_SRD_v0.2.md - Section 6
```

---

## 추가 참고 사항

### 데이터베이스 스키마 예시 (SQLite)

```sql
-- users 테이블
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'doctor', 'reviewer')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- sessions 테이블
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    patient_id_encrypted TEXT,  -- at-rest encryption
    status TEXT NOT NULL CHECK(status IN ('active', 'completed', 'emergency_terminated', 'reviewed', 'confirmed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    assigned_doctor_id TEXT REFERENCES users(id),
    reviewed_at TIMESTAMP,
    confirmed_at TIMESTAMP
);

-- session_slots 테이블
CREATE TABLE session_slots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT REFERENCES sessions(id),
    slot_key TEXT NOT NULL,
    slot_value_encrypted TEXT,  -- at-rest encryption
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, slot_key)
);

-- session_logs 테이블
CREATE TABLE session_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT REFERENCES sessions(id),
    turn_index INTEGER NOT NULL,
    user_input TEXT,
    agent_response TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- session_notes 테이블
CREATE TABLE session_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT REFERENCES sessions(id),
    doctor_id TEXT REFERENCES users(id),
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### UI 라이브러리 권장 사항

**옵션 1: shadcn/ui (추천)**
- Tailwind CSS 기반
- 복사-붙여넣기 방식 (의존성 최소화)
- 빠른 프로토타이핑

**옵션 2: Material-UI (MUI)**
- 풍부한 컴포넌트
- 접근성 우수
- 테마 커스터마이징 쉬움

**옵션 3: Ant Design**
- 엔터프라이즈급 UI
- 테이블, 폼 컴포넌트 강력
- 한국어 지원

### 암호화 구현 예시

```python
# server/services/encryption.py
import os
from cryptography.fernet import Fernet

class EncryptionService:
    def __init__(self):
        key = os.getenv("DB_ENCRYPTION_KEY")
        if not key:
            raise ValueError("DB_ENCRYPTION_KEY not set")
        self.cipher = Fernet(key.encode())

    def encrypt(self, plaintext: str) -> str:
        return self.cipher.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        return self.cipher.decrypt(ciphertext.encode()).decode()
```

### RBAC 미들웨어 예시

```python
# server/auth/rbac.py
from fastapi import Depends, HTTPException, status
from typing import List

async def require_role(allowed_roles: List[str]):
    def dependency(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {current_user.role} not allowed"
            )
        return current_user
    return dependency

# 사용 예시
@router.patch("/sessions/{session_id}/slots")
async def update_slots(
    session_id: str,
    data: SlotUpdateRequest,
    current_user: User = Depends(require_role(["admin", "doctor"]))
):
    # ...
```

---

## Notes

- **PoC 단계**이므로 SQLite 사용, 추후 PostgreSQL 전환 고려
- **at-rest encryption**은 필수이므로 `cryptography` 패키지 사용
- **리포트 PDF 생성**은 선택사항 (HTML 우선, 시간 남으면 PDF)
- **UI 라이브러리**는 팀 선호도에 따라 선택 (shadcn/ui 추천)
- **테스트**는 핵심 플로우 중심 (E2E > 단위)
- **문서화**는 README에 실행 방법 추가로 충분

---

**다음 단계**: 본 Task 파일을 검토하고 구현 시작
