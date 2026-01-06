# Phase 3 구현 빠른 참조 가이드

## 목적
Phase 3 음성 연동 구현 시 빠르게 참조할 수 있는 핵심 설정 및 결정사항

---

## 1. 재연결 정책 ⚙️

### 권장 설정 (복사해서 사용)

```typescript
const RECONNECT_CONFIG = {
  maxRetries: 3,              // 최대 3회 재시도
  baseDelay: 2000,            // 초기 2초 대기
  maxDelay: 8000,             // 최대 8초 대기
  backoffMultiplier: 2,       // 지수 증가 (2s → 4s → 8s)
  sessionRestoreTimeout: 60,  // 60초 이내 세션 복구
};
```

**총 재연결 시간**: 14초 (2s + 4s + 8s)

---

## 2. 오디오 UI 컬러 🎨

### 빠른 복사용 컬러 팔레트

```typescript
const COLORS = {
  primary: '#2563EB',     // 파랑 (메인 액션)
  success: '#10B981',     // 녹색 (성공, 연결됨)
  warning: '#F59E0B',     // 주황 (재연결 중)
  error: '#EF4444',       // 빨강 (실패, 응급)
  neutral: '#6B7280',     // 회색 (비활성)
};
```

### 오디오 레벨 컬러

```typescript
function getAudioLevelColor(level: number): string {
  if (level < 30) return '#10B981';  // 녹색 (낮음)
  if (level < 70) return '#F59E0B';  // 주황 (중간)
  return '#EF4444';                  // 빨강 (높음)
}
```

---

## 3. 레벨 미터 형태 📊

### ✅ 권장: 수평 바 (Horizontal Bar)

```tsx
<div className="w-full h-6 bg-gray-100 rounded-full overflow-hidden">
  <div
    className="h-full rounded-full transition-all duration-100"
    style={{
      width: `${audioLevel}%`,
      background: getAudioLevelColor(audioLevel),
    }}
  />
</div>
```

**선택 이유**: 직관적, 고령자 친화적, 구현 간단

---

## 4. STT 표시 방식 💬

### ✅ 권장: 하이브리드 (확정 텍스트 + 실시간 스트리밍)

```tsx
<div className="transcript-container">
  {/* 확정된 텍스트 (검정색) */}
  {confirmedTexts.map((text, idx) => (
    <div key={idx} className="text-black font-normal">
      환자: {text}
    </div>
  ))}

  {/* 실시간 스트리밍 (회색 이탤릭) */}
  {currentText && (
    <div className="text-gray-500 italic">
      환자: {currentText}...
    </div>
  )}
</div>
```

**시각적 구분**:
- 확정: 검정색, 일반 폰트
- 스트리밍: 회색, 이탤릭, "..." 표시

---

## 5. 네트워크 상태 문구 📡

### 빠른 복사용 메시지

| 상태 | 문구 | 컬러 |
|------|------|------|
| 연결 중 | "음성 연결 중이에요..." | 🟠 주황 |
| 연결됨 | "연결 완료" | 🟢 녹색 |
| 듣는 중 | "듣고 있어요..." | 🔵 파랑 |
| 재연결 | "재연결 중이에요... (1/3)" | 🟠 주황 |
| 실패 | "연결에 실패했어요<br>페이지를 새로고침해주세요" | 🔴 빨강 |
| 응급 | "⚠️ 응급 증상이 감지되었어요<br>즉시 119에 연락하세요" | 🔴 빨강 |

```typescript
const STATUS_MESSAGES = {
  CONNECTING: '음성 연결 중이에요...',
  CONNECTED: '연결 완료',
  LISTENING: '말씀해 주세요',
  PROCESSING: '듣고 있어요...',
  RECONNECTING: (n, max) => `재연결 중이에요... (${n}/${max})`,
  FAILED: '연결에 실패했어요\n페이지를 새로고침해주세요',
  EMERGENCY: '⚠️ 응급 증상이 감지되었어요\n즉시 119에 연락하세요',
};
```

---

## 6. 음성 버튼 UX 🎤

### ✅ 권장: 토글 방식

```tsx
// 상태별 버튼 설정
const buttonConfig = {
  START: {
    text: '시작하기',
    bg: '#2563EB',      // 파랑
    icon: 'microphone',
  },
  CONNECTING: {
    text: '연결 중...',
    bg: '#F59E0B',      // 주황
    icon: 'spinner',
  },
  STOP: {
    text: '대화 중지',
    bg: '#EF4444',      // 빨강
    icon: 'stop',
  },
};
```

### 버튼 크기 (고령자 고려)

```css
.voice-button {
  width: 200px;
  height: 80px;
  font-size: 20px;
  border-radius: 40px;
  /* 아이콘 크기: 32px */
}

/* 모바일 */
@media (max-width: 640px) {
  .voice-button {
    width: 100%;
    max-width: 300px;
    height: 64px;
    font-size: 18px;
  }
}
```

---

## 7. 에러 메시지 ⚠️

### 사용자 친화적 에러 문구

```typescript
const ERROR_MESSAGES = {
  MICROPHONE_DENIED: {
    title: '마이크 권한이 필요해요',
    message: '음성 문진을 위해 마이크 권한이 필요합니다.\n브라우저 설정에서 마이크 권한을 허용해주세요.',
    action: '설정으로 이동',
  },
  NETWORK_ERROR: {
    title: '연결에 실패했어요',
    message: '인터넷 연결을 확인하고 다시 시도해주세요.',
    action: '다시 시도',
  },
  SESSION_EXPIRED: {
    title: '세션이 만료되었어요',
    message: '페이지를 새로고침하여 다시 시작해주세요.',
    action: '새로고침',
  },
};
```

---

## 8. 접근성 체크리스트 ♿

### 필수 구현 사항

```tsx
<button
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

### 컬러 대비율
- 텍스트: **4.5:1** 이상
- UI 요소: **3:1** 이상

---

## 9. 전체 화면 레이아웃 📐

```
┌─────────────────────────────────┐
│       Befora 음성 문진          │ ← Header
├─────────────────────────────────┤
│ [✓ 연결 완료]                   │ ← Status Bar
├─────────────────────────────────┤
│ 음성 레벨                        │
│ ████████████░░░░░░░░░░░░░░░░░░ │ ← Audio Meter
│                                  │
│ ┌─────────────────────────────┐ │
│ │ AI: 어떤 증상으로 방문하시  │ │
│ │ 환자: 두통이 있어요         │ │ ← Transcript
│ │ 환자: 어제부터...           │ │   (스크롤)
│ └─────────────────────────────┘ │
│                                  │
│        ┌───────────┐             │
│        │ 🛑 중지   │             │ ← Main Button
│        └───────────┘             │
└─────────────────────────────────┘
```

---

## 10. 구현 파일 구조 📁

```
apps/web-client/src/
├── constants/
│   └── ui.ts                  ✅ 생성됨 (모든 상수)
├── components/
│   ├── VoiceInterview.tsx     🔜 메인 화면
│   ├── AudioControls.tsx      🔜 시작/중지 버튼
│   ├── AudioLevelMeter.tsx    🔜 레벨 미터
│   ├── NetworkStatus.tsx      🔜 상태 표시
│   └── TranscriptView.tsx     🔜 STT 표시
├── lib/
│   └── realtime.ts            🔜 WebRTC 클라이언트
└── stores/
    └── voiceStore.ts          🔜 Zustand 상태
```

---

## 11. 우선순위별 구현 단계 🎯

### Phase 3.1 (MVP - 필수)
- [x] 상수 파일 생성 (`constants/ui.ts`)
- [ ] 토글 버튼 (`AudioControls.tsx`)
- [ ] 수평 바 레벨 미터 (`AudioLevelMeter.tsx`)
- [ ] 최종 텍스트 표시 (`TranscriptView.tsx`)
- [ ] 기본 네트워크 상태 (`NetworkStatus.tsx`)
- [ ] 재연결 정책 (`lib/realtime.ts`)

### Phase 3.2 (개선 - 권장)
- [ ] 하이브리드 STT (실시간 + 확정)
- [ ] 응급 상태 UI
- [ ] 접근성 강화 (ARIA)

### Phase 3.3 (고급 - 선택)
- [ ] 원형 게이지 옵션
- [ ] 푸시투톡 대체 모드
- [ ] 다크모드

---

## 12. 코드 템플릿 (빠른 시작) 🚀

### AudioLevelMeter.tsx

```tsx
export function AudioLevelMeter({ level }: { level: number }) {
  return (
    <div className="w-full h-6 bg-gray-100 rounded-full overflow-hidden">
      <div
        className="h-full rounded-full transition-all duration-100"
        style={{
          width: `${level}%`,
          background: getAudioLevelColor(level),
        }}
        role="progressbar"
        aria-valuenow={level}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={`음성 레벨 ${level}%`}
      />
    </div>
  );
}
```

### AudioControls.tsx

```tsx
export function AudioControls({ onStart, onStop, state }: Props) {
  const config = VOICE_BUTTON_CONFIGS[state];

  return (
    <button
      className="voice-button"
      style={{ background: config.backgroundColor }}
      onClick={state === 'START' ? onStart : onStop}
      aria-label={config.ariaLabel}
      disabled={config.disabled}
    >
      <Icon name={config.icon} size={32} />
      <span className="text-xl font-bold">{config.text}</span>
    </button>
  );
}
```

### NetworkStatus.tsx

```tsx
export function NetworkStatus({ status, retryCount }: Props) {
  const message =
    status === 'RECONNECTING'
      ? getReconnectingMessage(retryCount, RECONNECT_CONFIG.maxRetries)
      : NETWORK_STATUS_MESSAGES[status];

  return (
    <div
      className={`status-bar ${message.color}`}
      role="status"
      aria-live="polite"
      aria-label={message.ariaLabel}
    >
      <Icon name={message.icon} />
      <span>{message.text}</span>
    </div>
  );
}
```

---

## 13. 테스트 시나리오 ✅

### 기본 플로우
1. [ ] "시작하기" 버튼 클릭
2. [ ] 마이크 권한 요청 표시
3. [ ] 권한 허용 → 연결 중 스피너
4. [ ] 연결 완료 → "대화 중지" 버튼으로 변경
5. [ ] 말하기 → 레벨 미터 반응
6. [ ] STT 텍스트 표시 확인
7. [ ] "대화 중지" 버튼 클릭 → 종료

### 에러 시나리오
1. [ ] 마이크 권한 거부 → 안내 메시지
2. [ ] 네트워크 끊김 → 재연결 시도 (1/3, 2/3, 3/3)
3. [ ] 재연결 실패 → 최종 에러 메시지

### 접근성 테스트
1. [ ] Tab 키로 버튼 포커스
2. [ ] Enter/Space로 버튼 클릭
3. [ ] 스크린 리더로 상태 읽기

---

## 14. 참고 문서 📚

| 문서 | 용도 |
|------|------|
| [PHASE3_UX_GUIDELINES.md](./PHASE3_UX_GUIDELINES.md) | 상세한 UX/UI 설계 가이드 |
| [OPENAI_SETUP.md](./OPENAI_SETUP.md) | OpenAI API 설정 방법 |
| [REALTIME_API_CHANGELOG.md](./REALTIME_API_CHANGELOG.md) | API 변경사항 |
| [constants/ui.ts](../apps/web-client/src/constants/ui.ts) | 모든 상수 정의 |

---

## 15. 결정사항 요약 📋

| 항목 | 선택 | 근거 |
|------|------|------|
| **재연결** | 3회, 2초, 8초 | 사용자 인내심 한계 (14초) |
| **레벨 미터** | 수평 바 | 직관적, 고령자 친화적 |
| **STT** | 하이브리드 | 피드백 + 명확성 |
| **버튼** | 토글 | 단순, 명확 |
| **컬러** | Blue/Green/Red | 의료 환경 표준 |
| **폰트** | 20px | 고령자 가독성 |
| **버튼 크기** | 200x80px | 터치 타겟 |

---

**빠른 시작**: `apps/web-client/src/constants/ui.ts` 파일에 모든 상수가 정의되어 있습니다. 복사해서 사용하세요!

**문의**: Phase 3 구현 중 불명확한 사항은 `docs/PHASE3_UX_GUIDELINES.md` 참조
