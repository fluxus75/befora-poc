# CI/CD 설정 가이드

## 개요

이 프로젝트는 GitHub Actions를 사용하여 CI 파이프라인을 구성합니다.

## CI 파이프라인 구성

### 트리거 조건

```yaml
on:
  push:
    branches: [main]
  pull_request:
```

- **main 브랜치 push**: 모든 CI job 실행
- **Pull Request**: 모든 CI job 실행

### 워크플로우 구조

```
.github/workflows/ci.yml
├── frontend (Frontend - lint/test/build)
│   ├── Lint (ESLint)
│   ├── Type Check (tsc)
│   ├── Unit Tests (Vitest)
│   └── Build (Vite)
├── backend (Backend - lint/test)
│   ├── Lint (ruff, black, isort) - server/, shared/ 대상
│   └── Unit Tests (pytest)
├── e2e (E2E - Playwright) [depends: frontend, backend]
│   ├── Backend 서버 시작
│   ├── Playwright 테스트 실행
│   └── 리포트 아티팩트 업로드
├── security (Security - trivy/trufflehog/pii)
│   ├── Trivy 파일시스템 스캔 (CRITICAL, HIGH)
│   ├── TruffleHog 시크릿 검사 (verified only)
│   └── PII 패턴 검사 (주민번호, SSN, 전화번호, 이메일)
└── dependencies (Dependencies - audit)
    ├── pnpm audit (high 이상)
    └── pip-audit
```

## 필수 GitHub Secrets 설정

### 1. Repository Secrets 추가

GitHub Repository → Settings → Secrets and variables → Actions에서 다음 시크릿을 추가하세요:

```
OPENAI_API_KEY           # OpenAI Realtime API 키 (사용 시)
```

### 2. (선택사항) Codecov 설정

현재 CI는 Codecov 업로드를 수행하지 않습니다. 필요 시 별도 job을 추가하세요.

## 로컬에서 CI 검증

### Frontend 검증

```bash
# Lint
pnpm -C apps/web-client lint

# Type 체크
pnpm -C apps/web-client type-check

# 단위 테스트
pnpm -C apps/web-client test

# 빌드
pnpm -C apps/web-client build
```

### Backend 검증

```bash
# Lint (server/, shared/ 대상)
uv run ruff check server shared

# Format 체크
uv run black --check server shared
uv run isort --check-only server shared

# 테스트
uv run pytest

# 보안 스캔 (로컬)
uv pip install pip-audit  # 최초 1회
uv run pip-audit
```

### E2E 테스트 실행

```bash
# Playwright 설치 (최초 1회)
pnpm -C apps/web-client exec playwright install --with-deps chromium

# 환경 변수 설정 (Mock 모드로 실행 시)
export VITE_REALTIME_PROVIDER=mock
export OPENAI_API_KEY=test-key-not-used

# 백엔드 서버 시작
uv run uvicorn server.main:app --port 8000 &

# E2E 테스트 실행
pnpm -C apps/web-client test:e2e
```

> **참고**: CI에서는 `VITE_REALTIME_PROVIDER=mock`으로 실행되어 실제 OpenAI API 호출 없이 테스트됩니다.

## CI 실패 시 대응

### 1. Lint 실패

```bash
# Frontend 자동 수정
pnpm -C apps/web-client lint --fix

# Backend 자동 수정
uv run ruff check --fix server shared
uv run black server shared
uv run isort server shared
```

### 2. 테스트 실패

```bash
# Frontend 테스트 재실행 (상세 로그)
pnpm -C apps/web-client test -- --reporter=verbose

# Backend 테스트 재실행 (상세 로그)
uv run pytest -v
```

### 3. 보안 스캔 실패

**시크릿 노출 감지:**

- 커밋 히스토리에서 제거: `git filter-branch` 또는 `BFG Repo-Cleaner`
- `.env` 파일이 커밋되지 않도록 `.gitignore` 확인

**취약한 의존성:**

```bash
# Frontend
pnpm audit --fix

# Backend
uv pip install --upgrade <package-name>
```

### 4. E2E 테스트 실패

```bash
# 스크린샷/비디오 확인
ls apps/web-client/test-results/

# 브라우저 호환성 확인 (Chrome 120+)
google-chrome --version

# WebRTC 권한 확인
# 테스트가 마이크 권한을 올바르게 부여하는지 확인
```

## PR 체크리스트

PR을 생성하기 전에 다음을 확인하세요:

- [ ] 로컬에서 `pnpm -C apps/web-client lint` 통과
- [ ] 로컬에서 `pnpm -C apps/web-client test` 통과
- [ ] 로컬에서 `uv run ruff check server shared` 통과
- [ ] 로컬에서 `uv run pytest` 통과
- [ ] 환경 변수가 코드에 하드코딩되지 않음
- [ ] PII 로깅 없음
- [ ] 커밋 메시지가 컨벤션을 따름 (예: `feat(rtc): WebRTC 재연결 로직 추가`)

## 브랜치 보호 규칙 (권장)

GitHub Repository → Settings → Branches에서 `main` 브랜치에 다음 규칙 설정:

- [x] Require a pull request before merging
- [x] Require status checks to pass before merging
  - [x] Frontend (lint/test/build)
  - [x] Backend (lint/test)
  - [x] E2E (Playwright)
  - [x] Security (trivy/trufflehog/pii)
  - [x] Dependencies (audit)
- [x] Require conversation resolution before merging
- [x] Do not allow bypassing the above settings

## 성능 최적화

### 캐싱 전략

CI는 다음 캐시를 사용하여 빌드 시간을 단축합니다:

- **pnpm**: `actions/setup-node`의 `cache: pnpm` 옵션으로 자동 캐싱

> **참고**: uv와 Playwright 브라우저는 현재 별도 캐싱 설정이 없습니다. 필요 시 `actions/cache`를 추가할 수 있습니다.

### E2E 아티팩트

CI는 Playwright 결과를 아티팩트로 업로드합니다 (테스트 성공/실패 관계없이):

- `apps/web-client/playwright-report` - HTML 리포트
- `apps/web-client/test-results` - 스크린샷, 비디오, 트레이스

아티팩트 이름: `playwright-report`

### 병렬 실행

독립적인 작업은 병렬로 실행됩니다:

- `frontend`, `backend`, `security`, `dependencies`는 병렬 실행
- `e2e`는 `frontend`와 `backend` 완료 후 실행 (`needs: [frontend, backend]`)

## 모니터링

### CI 실행 시간 목표

- Frontend CI: < 3분
- Backend CI: < 2분
- E2E Tests: < 5분
- Security Scan: < 3분

실행 시간이 목표를 초과하면 최적화를 고려하세요.

## 문제 해결

### "pnpm not found" 에러

GitHub Actions에서 pnpm을 찾지 못하는 경우:

- `package.json`의 `packageManager` 필드 확인
- `pnpm/action-setup@v4` 버전 확인

### "uv command not found" 에러

- `astral-sh/setup-uv@v4` 액션이 올바르게 설정되었는지 확인
- Python 버전이 3.11+ 인지 확인

### Playwright 관련 오류

```bash
# 로컬에서 재설치
pnpm -C apps/web-client exec playwright install --with-deps chromium
```

## 추가 리소스

- [GitHub Actions 문서](https://docs.github.com/en/actions)
- [Playwright 문서](https://playwright.dev)
- [Codecov 문서](https://docs.codecov.io)
- [Trivy 문서](https://aquasecurity.github.io/trivy)
