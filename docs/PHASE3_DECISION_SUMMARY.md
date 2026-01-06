# Phase 3 구현 결정사항 최종 요약

## 문서 목적
Phase 3 음성 연동 구현 전 검토한 5가지 핵심 항목에 대한 최종 결정사항을 기록

---

## 1. 재연결 정책 ⚙️

### 최종 결정

```typescript
const RECONNECT_CONFIG = {
  maxRetries: 3,              // ✅ 최대 3회 재시도
  baseDelay: 2000,            // ✅ 초기 2초 대기
  maxDelay: 8000,             // ✅ 최대 8초 대기
  backoffMultiplier: 2,       // ✅ 지수 백오프 (2배씩 증가)
  sessionRestoreTimeout: 60,  // ✅ 60초 이내 세션 복구
};
```

### 근거
- **maxRetries: 3회**: 총 14초 대기 (2s + 4s + 8s) → 사용자 인내심 한계
- **baseDelay: 2초**: 네트워크 복구에 충분한 시간, 너무 짧으면 서버 부하
- **maxDelay: 8초**: 10초 이하 유지 (UX 권장 사항)
- **sessionRestoreTimeout: 60초**: 의료 문진 특성상 중간 중단 가능성 고려 (보호자 통화 등)

### 재시도 시퀀스
```
1차: 즉시 (0초)       → 실패
2차: 2초 대기 후      → 실패
3차: 4초 대기 후      → 실패
4차: 8초 대기 후      → 실패
최종: 사용자에게 수동 새로고침 안내
```

### 구현 위치
- `apps/web-client/src/constants/ui.ts` (정의)
- `apps/web-client/src/lib/realtime.ts` (실제 로직)

---

## 2. 오디오 UI 스타일 🎨

### 최종 결정: 컬러/테마

```typescript
const AUDIO_UI_COLORS = {
  primary: '#2563EB',     // Blue-600 (메인 액션)
  success: '#10B981',     // Green-500 (연결 성공)
  warning: '#F59E0B',     // Amber-500 (재연결 중)
  error: '#EF4444',       // Red-500 (실패/응급)
  neutral: '#6B7280',     // Gray-500 (비활성)
};
```

### 근거
- **Blue**: 의료 환경에서 신뢰감을 주는 표준 컬러
- **Green/Amber/Red**: 신호등 패러다임 (직관적)
- **Tailwind CSS 팔레트**: 일관성, 접근성 (WCAG AA 준수)

### 최종 결정: 레벨 미터 형태

**✅ 선택: 수평 바 (Horizontal Bar)**

```
┌──────────────────────────────────┐
│ ████████████░░░░░░░░░░░░░░░░░░░ │  75%
└──────────────────────────────────┘
```

### 근거
- 직관적 (왼쪽→오른쪽 읽기 자연스러움)
- 고령자도 쉽게 이해
- 구현 간단 (CSS `width` 조정만)
- 모바일 대응 용이

### 대안 (불채택)
- ❌ 원형 게이지: 구현 복잡, 고령자 인지 부담
- ❌ 수직 바: 공간 많이 차지, 의료 환경 부적합

### 구현 위치
- `apps/web-client/src/components/AudioLevelMeter.tsx`

---

## 3. STT 표시 방식 💬

### 최종 결정: 하이브리드 (확정 텍스트 + 실시간 스트리밍)

```tsx
<div className="transcript-container">
  {/* 확정된 텍스트 (검정색, 일반 폰트) */}
  {confirmedTranscripts.map(text => (
    <div className="text-black font-normal">환자: {text}</div>
  ))}

  {/* 실시간 스트리밍 (회색, 이탤릭, "..." 표시) */}
  {currentStreaming && (
    <div className="text-gray-500 italic">환자: {currentStreaming}...</div>
  )}
</div>
```

### 근거
- **실시간 피드백**: 사용자가 자신의 발화가 인식되고 있음을 즉시 확인
- **명확한 구분**: 확정 텍스트 vs 임시 텍스트 시각적 분리
- **혼란 최소화**: 깜빡임 없음, 스크롤 자동 조정

### 시각적 구분
| 상태 | 컬러 | 스타일 | 표시 |
|------|------|--------|------|
| 확정 | 검정 | 일반 | "환자: 두통이 있어요" |
| 스트리밍 | 회색 | 이탤릭 | "환자: 어제부터..." |

### 대안 (부분 채택 가능)
- **최종 텍스트만**: Phase 3.1 MVP에서 우선 구현 가능 (단순 버전)
- **하이브리드**: Phase 3.2에서 개선

### 구현 위치
- `apps/web-client/src/components/TranscriptView.tsx`
- `apps/web-client/src/stores/voiceStore.ts` (상태 관리)

---

## 4. 네트워크 상태 문구 📡

### 최종 결정: 사용자 친화적 평어 문구

| 상태 | 문구 | 컬러 | 아이콘 |
|------|------|------|--------|
| **연결 중** | "음성 연결 중이에요..." | 🟠 주황 | 🔄 회전 |
| **연결됨** | "연결 완료" | 🟢 녹색 | ✓ |
| **대기 중** | "말씀해 주세요" | 🟢 녹색 | 🎤 |
| **듣는 중** | "듣고 있어요..." | 🔵 파랑 | 🎧 파동 |
| **재연결 중** | "재연결 중이에요... (1/3)" | 🟠 주황 | 🔄 |
| **연결 실패** | "연결에 실패했어요<br>페이지를 새로고침해주세요" | 🔴 빨강 | ⚠️ |
| **응급 감지** | "⚠️ 응급 증상이 감지되었어요<br>즉시 119에 연락하세요" | 🔴 빨강 | 🚨 |

### 근거
1. **평어 사용**: "~합니다" (X) → "~해요" (O) - 친근함
2. **짧고 명확**: 10자 이내 권장 - 고령자 인지 부담 최소화
3. **진행 표시**: 재시도 횟수 명시 (1/3) - 투명성
4. **행동 유도**: "새로고침해주세요" - 구체적 안내
5. **이모지 사용**: 시각적 인지 향상 (선택적)

### 문구 작성 원칙
- 존댓말 평어 ("~해요")
- 능동형 ("연결 중" > "연결되고 있습니다")
- 긍정적 표현 ("완료" > "성공")
- 구체적 행동 ("새로고침" > "다시 시도")

### 구현 위치
- `apps/web-client/src/constants/ui.ts` (정의)
- `apps/web-client/src/components/NetworkStatus.tsx` (표시)

---

## 5. 음성 시작/중지 UX 🎤

### 최종 결정: 토글 방식 + 자동 VAD

**흐름**:
1. 초기: "시작하기" 버튼 (파랑)
2. 클릭 → 마이크 권한 요청 → "연결 중..." (주황, 회전)
3. 연결 완료 → "대화 중지" 버튼 (빨강)
4. 대화 진행: VAD 자동 음성 감지
5. "대화 중지" 클릭 → 종료

### 버튼 상태 전환

```
[ 시작하기 ]  →  [ 연결 중... ]  →  [ 대화 중지 ]
   (파랑)          (주황, 회전)         (빨강)
```

### 버튼 설정

```typescript
const VOICE_BUTTON_CONFIGS = {
  START: {
    text: '시작하기',
    backgroundColor: '#2563EB',  // 파랑
    icon: 'microphone',
    ariaLabel: '음성 문진 시작하기',
  },
  CONNECTING: {
    text: '연결 중...',
    backgroundColor: '#F59E0B',  // 주황
    icon: 'spinner',
    disabled: true,
  },
  STOP: {
    text: '대화 중지',
    backgroundColor: '#EF4444',  // 빨강
    icon: 'stop',
    ariaLabel: '음성 대화 중지하기',
  },
};
```

### 버튼 크기 (고령자 고려)

| 요소 | 최소 | 권장 | 이유 |
|------|------|------|------|
| 너비 | 150px | **200px** | 터치 영역 |
| 높이 | 60px | **80px** | 시각 인지 |
| 폰트 | 16px | **20px** | 가독성 |
| 아이콘 | 24px | **32px** | 명확성 |

### 모바일 최적화

```css
/* 데스크톱 */
.voice-button {
  width: 200px;
  height: 80px;
  font-size: 20px;
  border-radius: 40px;
}

/* 모바일 (640px 이하) */
@media (max-width: 640px) {
  .voice-button {
    width: 100%;
    max-width: 300px;
    height: 64px;
    font-size: 18px;
  }
}
```

### 근거
- **토글 방식**: 단순, 직관적, 실수 종료 방지
- **자동 VAD**: 편리함 (손 떼면 중단되는 푸시투톡은 고령자에게 어려움)
- **큰 버튼**: 터치 타겟 44px 이상 (iOS/Android 권장)
- **명확한 색상**: 파랑(시작) → 빨강(중지) 직관적

### 대안 (불채택)
- ❌ 푸시투톡 (Press-to-Talk): 고령자 어려움 (손 떼면 중단)
- ❌ 자동 VAD만: 제어 불가, 오감지 위험

### 구현 위치
- `apps/web-client/src/components/AudioControls.tsx`
- `apps/web-client/src/lib/realtime.ts` (VAD 설정)

---

## 6. 접근성 (Accessibility) 요구사항 ♿

### 필수 구현 사항

#### WCAG 2.1 Level AA 준수
1. **컬러 대비율**: 4.5:1 (텍스트), 3:1 (UI)
2. **키보드 탐색**: Tab, Enter, Space로 모든 기능 사용
3. **스크린 리더**: ARIA 레이블 필수
4. **포커스 표시**: 명확한 포커스 아웃라인

#### 구현 예시

```tsx
<button
  className="voice-button"
  aria-label="음성 문진 시작하기"
  aria-pressed={isRecording}
  tabIndex={0}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') handleStart();
  }}
>
  시작하기
</button>

<div
  role="progressbar"
  aria-valuenow={audioLevel}
  aria-valuemin={0}
  aria-valuemax={100}
  aria-label={`음성 레벨 ${audioLevel}%`}
/>
```

---

## 7. 구현 우선순위 🎯

### Phase 3.1 (MVP - 필수, 2025-01-06 시작)

- [x] **상수 정의**: `constants/ui.ts` ✅ 완료
- [x] **타입 정의**: `types/voice.ts` ✅ 완료
- [ ] **Ephemeral Token API**: `server/api/realtime.py`
- [ ] **WebRTC 클라이언트**: `lib/realtime.ts`
- [ ] **토글 버튼**: `components/AudioControls.tsx`
- [ ] **수평 바 레벨 미터**: `components/AudioLevelMeter.tsx`
- [ ] **최종 텍스트 표시**: `components/TranscriptView.tsx`
- [ ] **네트워크 상태**: `components/NetworkStatus.tsx`
- [ ] **재연결 정책**: `lib/realtime.ts`

### Phase 3.2 (개선 - 권장)

- [ ] 하이브리드 STT (실시간 + 확정)
- [ ] 응급 상태 UI
- [ ] 접근성 강화 (ARIA 완전 구현)
- [ ] 마이크 권한 에러 처리

### Phase 3.3 (고급 - 선택)

- [ ] 원형 게이지 레벨 미터 (대체 옵션)
- [ ] 푸시투톡 모드 (대체 옵션)
- [ ] 다크모드
- [ ] 모바일 PWA 최적화

---

## 8. 생성된 파일 목록 📁

### 문서 (docs/)
1. ✅ `docs/PHASE3_UX_GUIDELINES.md` - 상세 UX/UI 가이드 (전체 10,000+ words)
2. ✅ `docs/PHASE3_QUICK_REFERENCE.md` - 빠른 참조 가이드 (요약본)
3. ✅ `docs/PHASE3_DECISION_SUMMARY.md` - 최종 결정사항 (이 문서)
4. ✅ `docs/OPENAI_SETUP.md` - OpenAI API 설정 (기존, 업데이트됨)
5. ✅ `docs/REALTIME_API_CHANGELOG.md` - API 변경사항 (신규)

### 소스 코드 (apps/web-client/src/)
1. ✅ `constants/ui.ts` - 모든 UI 상수 정의 (600+ lines)
2. ✅ `types/voice.ts` - TypeScript 타입 정의 (200+ lines)

### 서버 설정 (server/)
1. ✅ `server/config.py` - 환경 변수 설정 (업데이트됨)
2. ✅ `server/constants/realtime.py` - Realtime API 상수 (업데이트됨)
3. ✅ `server/constants/api_endpoints.py` - API 엔드포인트 (신규)

### 환경 설정
1. ✅ `.env.example` - 환경 변수 템플릿 (업데이트됨)
2. ✅ `pyproject.toml` - Python 의존성 (업데이트됨)

---

## 9. 다음 단계 (구현 순서) 🚀

### Step 1: Backend (서버 우선)
1. Ephemeral Token API 구현 (`server/api/realtime.py`)
2. Session Process API 구현 (`server/api/routes.py`)
3. 테스트 작성 (`server/tests/test_realtime.py`)

### Step 2: Frontend Core (핵심 로직)
1. WebRTC 클라이언트 구현 (`lib/realtime.ts`)
2. Zustand 스토어 구현 (`stores/voiceStore.ts`)
3. 재연결 로직 구현 (`lib/realtime.ts`)

### Step 3: Frontend UI (UI 컴포넌트)
1. AudioControls 구현 (시작/중지 버튼)
2. AudioLevelMeter 구현 (레벨 미터)
3. NetworkStatus 구현 (상태 표시)
4. TranscriptView 구현 (STT 표시)
5. VoiceInterview 구현 (메인 화면)

### Step 4: Integration & Testing
1. 전체 플로우 통합
2. 마이크 권한 에러 처리
3. 네트워크 끊김 시나리오 테스트
4. 고령자 사용성 테스트

---

## 10. 테스트 체크리스트 ✅

### 기능 테스트
- [ ] 버튼 클릭 → 마이크 권한 요청
- [ ] 권한 허용 → 연결 성공
- [ ] 권한 거부 → 에러 메시지
- [ ] 말하기 → 레벨 미터 반응
- [ ] 말하기 → STT 텍스트 표시
- [ ] 네트워크 끊김 → 자동 재연결 (3회)
- [ ] 재연결 실패 → 에러 메시지
- [ ] 중지 버튼 → 연결 종료

### 사용성 테스트 (고령자 대상)
- [ ] 버튼 크기 충분한가?
- [ ] 문구 이해하기 쉬운가?
- [ ] 에러 발생 시 대처 가능한가?
- [ ] 레벨 미터 의미 파악 가능한가?

### 접근성 테스트
- [ ] Tab 키로 버튼 포커스 가능
- [ ] Enter/Space로 버튼 클릭 가능
- [ ] 스크린 리더 호환성
- [ ] 컬러 대비율 확인 (WebAIM)

---

## 11. 참고 자료 📚

### 내부 문서
- [PHASE3_UX_GUIDELINES.md](./PHASE3_UX_GUIDELINES.md) - 상세 가이드
- [PHASE3_QUICK_REFERENCE.md](./PHASE3_QUICK_REFERENCE.md) - 빠른 참조
- [OPENAI_SETUP.md](./OPENAI_SETUP.md) - API 설정
- [REALTIME_API_CHANGELOG.md](./REALTIME_API_CHANGELOG.md) - API 변경사항

### 외부 참고
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Material Design - Voice & Audio](https://m3.material.io/)
- [Apple HIG - Audio](https://developer.apple.com/design/human-interface-guidelines/playing-audio)
- [Nielsen Norman Group - Voice UI](https://www.nngroup.com/articles/voice-first/)

---

## 12. 의사결정 기록 (Decision Log)

| 날짜 | 항목 | 결정 | 결정자 | 근거 |
|------|------|------|--------|------|
| 2025-01-06 | 재연결 정책 | 3회/2초/8초 | Team | 사용자 인내심 한계 (14초) |
| 2025-01-06 | 레벨 미터 | 수평 바 | Team | 고령자 친화성, 구현 단순성 |
| 2025-01-06 | STT 표시 | 하이브리드 | Team | 피드백 + 명확성 균형 |
| 2025-01-06 | 버튼 방식 | 토글 + VAD | Team | 단순성, 편의성 |
| 2025-01-06 | 컬러 팔레트 | Tailwind Blue/Green/Red | Team | 의료 환경 표준, 접근성 |

---

## 13. 리스크 및 대응책 ⚠️

| 리스크 | 확률 | 영향 | 대응책 |
|--------|------|------|--------|
| 마이크 권한 거부율 높음 | 중 | 높음 | 명확한 안내 메시지, 설정 이동 버튼 |
| 네트워크 불안정 | 중 | 높음 | 재연결 정책, 세션 복구 (60초) |
| 고령자 버튼 인지 어려움 | 중 | 중 | 큰 버튼 (200x80px), 명확한 문구 |
| VAD 오감지 | 중 | 중 | Threshold 조정 (0.5), 수동 중지 제공 |
| STT 실시간 깜빡임 혼란 | 저 | 중 | 하이브리드 방식, 시각적 구분 |

---

**최종 업데이트**: 2025-01-06
**다음 마일스톤**: Phase 3.1 구현 시작 (Ephemeral Token API)
**예상 완료**: 2025-01-13 (1주일)
