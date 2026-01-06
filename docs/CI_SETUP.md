# CI/CD 설정 가이드

## 개요

이 프로젝트는 GitHub Actions를 사용하여 CI 파이프라인을 구성합니다.

## CI 파이프라인 구성

### 워크플로우 구조

```
.github/workflows/ci.yml
├── frontend (Frontend CI)
│   ├── Lint
│   ├── Type Check
│   ├── Unit Tests
│   └── Build
├── backend (Backend CI)
│   ├── Lint (ruff, black, isort)
│   └── Unit Tests (including local realtime websocket framing test)
├── e2e (E2E Tests)
│   └── Playwright 브라우저 테스트
├── security (Security Scan)
│   ├── Trivy 취약점 스캔
│   ├── TruffleHog 시크릿 검사
│   └── PII 패턴 검사
└── dependencies (Dependency Check)
    ├── pnpm audit
    └── Python pip-audit
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
pnpm lint

# Format 체크
pnpm format:check

# Type 체크
pnpm --filter web-client type-check

# 단위 테스트
pnpm -C apps/web-client test

# 빌드
pnpm build
```

### Backend 검증

```bash
cd server

# Lint
uv run ruff check .

# Format 체크
uv run black --check .
uv run isort --check-only .

# 테스트
uv run pytest

# 보안 스캔 (로컬)
uv run pip-audit
```

### E2E 테스트 실행

```bash
# Playwright 설치 (최초 1회)
pnpm -C apps/web-client exec playwright install --with-deps chromium

# 백엔드 서버 시작
uv run uvicorn server.main:app --port 8000

# 프론트엔드 개발 서버 시작 (다른 터미널)
pnpm dev

# E2E 테스트 실행 (다른 터미널)
pnpm -C apps/web-client test:e2e
```

## CI 실패 시 대응

### 1. Lint 실패

```bash
# 자동 수정
pnpm lint:fix
pnpm format

# Backend
uv run ruff check --fix .
uv run black .
uv run isort .
```

### 2. 테스트 실패

```bash
# 테스트 재실행 (상세 로그)
pnpm test -- --reporter=verbose

# Backend
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

- [ ] 로컬에서 `pnpm lint` 통과
- [ ] 로컬에서 `pnpm test` 통과
- [ ] 로컬에서 `uv run pytest` 통과
- [ ] 환경 변수가 코드에 하드코딩되지 않음
- [ ] PII 로깅 없음
- [ ] 커밋 메시지가 컨벤션을 따름 (예: `feat(rtc): WebRTC 재연결 로직 추가`)

## 브랜치 보호 규칙 (권장)

GitHub Repository → Settings → Branches에서 `main` 브랜치에 다음 규칙 설정:

- [x] Require a pull request before merging
- [x] Require status checks to pass before merging
  - [x] frontend
  - [x] backend
  - [x] e2e
  - [x] security
  - [x] dependencies
  - [x] frontend
  - [x] backend
- [x] Require conversation resolution before merging
- [x] Do not allow bypassing the above settings

## 성능 최적화

### 캐싱 전략

CI는 다음 캐시를 사용하여 빌드 시간을 단축합니다:

- **pnpm**: `~/.pnpm-store`
- **uv**: `.uv/cache`
- **Playwright**: `~/.cache/ms-playwright`

### E2E 아티팩트

CI는 Playwright 결과를 아티팩트로 업로드합니다:

- `apps/web-client/playwright-report`
- `apps/web-client/test-results`

### 병렬 실행

독립적인 작업은 병렬로 실행됩니다:
- Frontend, Backend, Security, Dependencies는 병렬 실행
- E2E 테스트는 Frontend와 Backend 완료 후 실행

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
