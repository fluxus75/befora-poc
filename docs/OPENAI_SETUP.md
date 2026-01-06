# OpenAI Realtime API 설정 가이드

## 1. OpenAI 홈페이지에서 할 일

### Step 1: API 키 발급

1. **OpenAI Platform 접속**: https://platform.openai.com/
2. **로그인** 후 좌측 메뉴에서 **"API keys"** 클릭
3. **"Create new secret key"** 버튼 클릭
   - Name: `befora-poc-realtime` (구분용)
   - Permissions: **All** 또는 **Restricted** (Realtime API 포함 확인)
4. **키 복사** (sk-proj-... 또는 sk-... 형식)
   - ⚠️ 이 키는 다시 확인할 수 없으므로 즉시 안전한 곳에 보관하세요

### Step 2: Organization ID 확인

1. 좌측 메뉴 **"Settings"** → **"Organization"** 클릭
2. **Organization ID** 복사 (org-... 형식)
   - 멀티 조직 환경에서 권장 (선택사항)

### Step 3: Project ID 확인 (선택사항)

1. 좌측 메뉴 **"Settings"** → **"Projects"** (있는 경우)
2. 프로젝트 선택 후 **Project ID** 복사 (proj-... 형식)
   - Realtime API는 프로젝트 레벨 격리 지원

### Step 4: 결제 정보 및 사용량 한도 확인

1. **"Settings"** → **"Billing"**
   - 결제 수단 등록 (미등록 시 API 호출 불가)
   - 사용량 한도 설정 권장 (예: 월 $50)

2. **"Settings"** → **"Limits"** 또는 **"Usage"**
   - Realtime API 사용 가능 여부 확인
   - 모델: `gpt-4o-realtime-preview-2024-12-17` (최신)

### Step 5: Realtime API 요금 확인

**gpt-realtime 모델 (GA, 2025년 기준)**:

| 항목 | 요금 | 할인율 |
|------|------|--------|
| 텍스트 입력 | $2.50 / 1M 토큰 | - |
| 텍스트 출력 | $10.00 / 1M 토큰 | - |
| 오디오 입력 | $32.00 / 1M 토큰 | **68% 절감** (기존 $100) |
| 오디오 출력 | $64.00 / 1M 토큰 | **68% 절감** (기존 $200) |
| 캐시 입력 (신규) | $0.40 / 1M 토큰 | **99.6% 절감** |

**예상 비용 (1회 문진 = 5분)**:
- 오디오 입력: ~75,000 토큰 = $2.40 (기존 $7.50)
- 오디오 출력: ~50,000 토큰 = $3.20 (기존 $10.00)
- **총 약 $5.60 / 세션** (기존 대비 **68% 절감**)

---

## 2. 코드베이스에서 할 일

### Step 1: 환경 변수 설정

1. `.env` 파일 수정 (루트 디렉토리):

```bash
# OpenAI API Configuration
OPENAI_API_KEY=sk-proj-your-actual-key-here
OPENAI_ORG_ID=org-your-org-id-here
OPENAI_PROJECT_ID=proj-your-project-id-here

# Realtime API Settings
# Models: gpt-realtime (GA), gpt-4o-mini-realtime-preview (low-cost)
REALTIME_MODEL=gpt-realtime
# Voices: alloy, ash, ballad, coral, echo, sage, shimmer, verse, marin, cedar
REALTIME_VOICE=alloy
REALTIME_TEMPERATURE=0.8
REALTIME_MAX_TOKENS=4096

# Ephemeral Token Settings
EPHEMERAL_TOKEN_EXPIRE_SECONDS=60

# Database
DATABASE_URL=sqlite:///./befora.db

# General
DEBUG=true
```

2. **실제 값 입력**:
   - `OPENAI_API_KEY`: OpenAI에서 발급받은 API 키
   - `OPENAI_ORG_ID`: Organization ID (선택사항)
   - `OPENAI_PROJECT_ID`: Project ID (선택사항)

### Step 2: 의존성 설치

```bash
# Backend 의존성 설치
cd /home/yoon/works/befora-poc
uv pip install -e ".[dev]"
```

새로 추가된 패키지:
- `pydantic-settings>=2.0` - 환경 변수 관리
- `openai>=1.54.0` - OpenAI Python SDK

### Step 3: 설정 파일 확인

생성된 설정 파일들:

1. **server/config.py**
   - 환경 변수를 타입 안전하게 로드
   - Pydantic Settings 사용
   - 기본값 및 유효성 검사 포함

2. **server/constants/realtime.py**
   - Realtime API 상수 정의
   - 모델, 음성, 오디오 설정
   - WebRTC 설정

### Step 4: 설정 테스트

```bash
# Python 인터프리터에서 테스트
cd /home/yoon/works/befora-poc
source server/.venv/bin/activate  # 가상환경 활성화 (생성되어 있는 경우)

python
>>> from server.config import settings
>>> print(settings.openai_api_key)  # API 키가 출력되어야 함 (앞 4자만 확인)
>>> print(settings.realtime_model)
gpt-4o-realtime-preview-2024-12-17
>>> print(settings.realtime_voice)
alloy
>>> exit()
```

### Step 5: 보안 체크리스트

- [ ] `.env` 파일이 `.gitignore`에 포함되어 있는지 확인
- [ ] API 키가 코드에 하드코딩되지 않았는지 확인
- [ ] `.env.example`에는 실제 키가 없는지 확인
- [ ] Organization/Project ID가 필요한 경우 설정했는지 확인

---

## 3. 모델 및 음성 옵션 가이드

### Realtime 모델 선택

| 모델 | 상태 | 가격 | 권장 용도 |
|------|------|------|----------|
| `gpt-realtime` | **GA** | $32/$64 (입/출력) | ⭐⭐⭐ **프로덕션 (권장)** |
| `gpt-4o-mini-realtime-preview` | Preview | 저비용 | 비용 절감 필요 시 |
| `gpt-4o-realtime-preview-2024-12-17` | Legacy | $40/$80 (입/출력) | 레거시 호환성 |

**PoC 권장**: `gpt-realtime` (GA 모델, 20% 저렴)

### 음성 옵션 선택 (10가지 음성)

**의료 문진 추천 순위**:

| 순위 | 음성 | 특징 | 적합도 |
|------|------|------|--------|
| 1 | `alloy` | 중성적, 균형잡힌 톤 | ⭐⭐⭐ **최우선 권장** |
| 2 | `sage` | 차분하고 사려깊은 톤 | ⭐⭐⭐ 매우 적합 |
| 3 | `marin` | 전문적이고 명료한 톤 | ⭐⭐⭐ 매우 적합 |
| 4 | `ash` | 명확하고 정확한 톤 | ⭐⭐ 적합 |
| 5 | `coral` | 따뜻하고 친근한 톤 | ⭐⭐ 적합 |

**기타 음성 옵션**:
- `ballad`: 멜로디컬하고 부드러운 톤
- `echo`: 울림이 있는 깊은 톤
- `shimmer`: 밝고 에너제틱한 톤
- `verse`: 다재다능하고 표현력 풍부한 톤
- `cedar`: 권위있고 자신감 있는 톤

**PoC 권장**: `alloy` 또는 `sage` (명료성 + 전문성)

### Temperature 설정

- **0.6-0.8**: 일관적이고 예측 가능한 응답 (의료 문진 권장)
- **0.8-1.0**: 자연스럽고 다양한 응답
- **1.0+**: 창의적이지만 불안정할 수 있음

**PoC 권장**: `0.8`

---

## 4. 검증 방법

### 환경 변수 로드 테스트

```bash
cd /home/yoon/works/befora-poc
python -c "from server.config import settings; print(f'Model: {settings.realtime_model}, Voice: {settings.realtime_voice}')"
```

예상 출력:
```
Model: gpt-realtime, Voice: alloy
```

### API 연결 테스트 (Phase 3 이후)

```bash
# Ephemeral token 발급 테스트 (구현 후)
curl -X POST http://localhost:8000/api/realtime/token \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-session-123"}'
```

---

## 5. 문제 해결

### 401 Unauthorized

- API 키가 올바른지 확인
- Organization ID가 올바른지 확인
- 결제 정보가 등록되어 있는지 확인
- Realtime API 접근 권한이 있는지 확인

### 429 Rate Limit

- 사용량 한도를 초과한 경우
- "Settings" → "Limits"에서 한도 확인
- 필요 시 한도 증액 요청

### ImportError: pydantic-settings

```bash
uv pip install pydantic-settings
```

### ModuleNotFoundError: openai

```bash
uv pip install openai
```

---

## 6. 다음 단계

환경 변수 설정이 완료되면:

1. **Ephemeral Token API 구현** (server/api/realtime.py)
2. **WebRTC 클라이언트 구현** (apps/web-client/src/lib/realtime.ts)
3. **음성 UI 컴포넌트 구현** (apps/web-client/src/components/)

---

## 참고 링크

- [OpenAI Realtime API 공식 문서](https://platform.openai.com/docs/guides/realtime)
- [OpenAI API 키 관리](https://platform.openai.com/api-keys)
- [OpenAI Pricing](https://openai.com/pricing)
- [WebRTC 가이드](https://platform.openai.com/docs/guides/realtime/webrtc)
