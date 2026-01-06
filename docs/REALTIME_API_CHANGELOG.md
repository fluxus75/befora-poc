# OpenAI Realtime API 변경사항 (2025-01 업데이트)

## 변경 요약

2025년 1월 기준, OpenAI Realtime API가 Preview에서 **General Availability (GA)**로 전환되면서 다음과 같은 주요 변경사항이 있습니다.

---

## 1. 모델명 변경

### 변경 전 (Preview)
```
gpt-4o-realtime-preview-2024-12-17
gpt-4o-realtime-preview-2024-10-01
```

### 변경 후 (GA)
```
gpt-realtime  ← 권장 (GA 모델)
gpt-4o-mini-realtime-preview  ← 저비용 대안
gpt-4o-realtime-preview-2024-12-17  ← 레거시 (호환성용)
```

**영향**:
- ✅ 기존 preview 모델은 계속 작동 (레거시 지원)
- ✅ 새 프로젝트는 `gpt-realtime` 사용 권장
- ✅ 20% 가격 절감 효과

---

## 2. 음성 옵션 확장

### 변경 전 (3가지 음성)
```
alloy, echo, shimmer
```

### 변경 후 (10가지 음성)
```
alloy, ash, ballad, coral, echo, sage, shimmer, verse, marin, cedar
```

**신규 추가된 음성**:
- `ash`: 명확하고 정확한 톤
- `ballad`: 멜로디컬하고 부드러운 톤
- `coral`: 따뜻하고 친근한 톤
- `sage`: 차분하고 사려깊은 톤 (의료 문진 추천)
- `verse`: 다재다능하고 표현력 풍부한 톤
- `marin`: 전문적이고 명료한 톤 (의료 문진 추천)
- `cedar`: 권위있고 자신감 있는 톤

**의료 문진 추천 순위**:
1. `alloy` (기본, 중성적)
2. `sage` (차분함)
3. `marin` (전문성)

---

## 3. API 엔드포인트 변경

### WebRTC 엔드포인트
```
POST https://api.openai.com/v1/realtime/calls
```
- Ephemeral token 생성 시 사용
- SDP (Session Description Protocol) 교환

### WebSocket 엔드포인트
```
wss://api.openai.com/v1/realtime?model=gpt-realtime
```
- 직접 WebSocket 연결 시 사용
- 모델명을 쿼리 파라미터로 전달

---

## 4. 세션 설정 필수 필드 추가

### 변경 전
```javascript
{
  "modalities": ["text", "audio"],
  "instructions": "...",
  "voice": "alloy"
}
```

### 변경 후 (GA 모델)
```javascript
{
  "type": "realtime",  // ← 필수 추가
  "model": "gpt-realtime",  // ← 명시 권장
  "modalities": ["text", "audio"],
  "instructions": "...",
  "voice": "alloy"
}
```

**변경 이유**:
- GA 모델은 `type: "realtime"` 필드 필수
- 명시적 모델 지정으로 버전 관리 개선

---

## 5. 가격 인하 (20% 절감)

### 변경 전 (Preview)
| 항목 | 요금 |
|------|------|
| 오디오 입력 | $100.00 / 1M 토큰 |
| 오디오 출력 | $200.00 / 1M 토큰 |

### 변경 후 (GA)
| 항목 | 요금 | 절감율 |
|------|------|--------|
| 오디오 입력 | $32.00 / 1M 토큰 | **68% 절감** |
| 오디오 출력 | $64.00 / 1M 토큰 | **68% 절감** |
| 캐시 입력 (신규) | $0.40 / 1M 토큰 | **99.6% 절감** |

**예상 비용 절감 (1회 5분 문진)**:
- 변경 전: ~$17.50 / 세션
- 변경 후: ~$5.60 / 세션
- **절감액: $11.90 (68%)**

---

## 6. API 버전 업데이트

### 최신 API 버전
```
2025-08-28
```

**사용 방법**:
```http
POST https://api.openai.com/v1/realtime/calls
OpenAI-Beta: realtime=v1
```

---

## 7. 코드베이스 마이그레이션 가이드

### Step 1: 환경 변수 업데이트

**`.env` 파일 수정**:
```bash
# 변경 전
REALTIME_MODEL=gpt-4o-realtime-preview-2024-12-17
REALTIME_VOICE=alloy

# 변경 후
REALTIME_MODEL=gpt-realtime
REALTIME_VOICE=alloy  # 또는 sage, marin
```

### Step 2: 세션 설정 업데이트

**Python 코드 예시**:
```python
# 변경 전
session_config = {
    "modalities": ["text", "audio"],
    "voice": "alloy",
}

# 변경 후
session_config = {
    "type": "realtime",  # 필수 추가
    "model": "gpt-realtime",  # 명시 권장
    "modalities": ["text", "audio"],
    "voice": "alloy",
}
```

### Step 3: 의존성 업데이트

```bash
# OpenAI SDK 최신 버전 설치
uv pip install --upgrade openai>=1.54.0
```

### Step 4: 테스트

```bash
# 설정 확인
python -c "from server.config import settings; print(settings.realtime_model)"
# 출력: gpt-realtime

# API 연결 테스트 (Phase 3 이후)
curl -X POST http://localhost:8000/api/realtime/token \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-123"}'
```

---

## 8. 하위 호환성

### 레거시 모델 지원

OpenAI는 기존 preview 모델을 계속 지원합니다:
- `gpt-4o-realtime-preview-2024-12-17` ✅ 작동 (레거시 요금)
- `gpt-4o-realtime-preview-2024-10-01` ✅ 작동 (레거시 요금)

**권장 사항**:
- 신규 개발: `gpt-realtime` 사용
- 기존 시스템: 단계적 마이그레이션

---

## 9. 주의사항

### 필수 변경 사항
1. ✅ `type: "realtime"` 필드 추가 (GA 모델 사용 시)
2. ✅ 환경 변수 `REALTIME_MODEL=gpt-realtime` 설정
3. ✅ OpenAI SDK 1.54.0+ 업그레이드

### 선택적 변경 사항
1. 새로운 음성 옵션 테스트 (sage, marin 추천)
2. 캐시 기능 활용 (입력 토큰 비용 99.6% 절감)
3. `gpt-4o-mini-realtime-preview` 저비용 옵션 검토

---

## 10. 참고 링크

- [OpenAI Realtime API 공식 문서](https://platform.openai.com/docs/guides/realtime)
- [gpt-realtime 모델 상세](https://platform.openai.com/docs/models/gpt-realtime)
- [Realtime API 출시 발표](https://openai.com/index/introducing-gpt-realtime/)
- [음성 옵션 가이드](https://platform.openai.com/docs/guides/voice-agents)

---

**업데이트 날짜**: 2025-01-06
**적용 버전**: befora-poc v0.1.0 (Phase 3 준비)
