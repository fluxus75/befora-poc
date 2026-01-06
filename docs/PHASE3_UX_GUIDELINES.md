# Phase 3 음성 연동 UX/UI 가이드라인

## 목적
고령자를 포함한 모든 사용자가 직관적으로 음성 문진을 완료할 수 있도록 하는 UX/UI 설계 기준

---

## 1. 재연결 정책 기준

### 권장 설정 (의료 환경 최적화)

```typescript
const RECONNECT_CONFIG = {
  maxRetries: 3,              // ✅ 권장: 3회
  baseDelay: 2000,            // ✅ 권장: 2초
  maxDelay: 8000,             // ✅ 권장: 8초
  backoffMultiplier: 2,       // ✅ 권장: 2 (지수 증가)
  sessionRestoreTimeout: 60,  // ✅ 권장: 60초
};
```

### 설정 근거

| 항목 | 권장값 | 이유 |
|------|--------|------|
| `maxRetries` | **3회** | 고령자가 기다릴 수 있는 합리적인 시도 횟수<br>총 소요 시간: 2s + 4s + 8s = 14초 |
| `baseDelay` | **2초** | 네트워크 복구에 충분한 초기 대기 시간<br>너무 짧으면 서버 부하, 너무 길면 UX 저하 |
| `maxDelay` | **8초** | 사용자 인내심 한계 (10초 이하 유지)<br>의료 환경에서 응급 상황 대응 고려 |
| `backoffMultiplier` | **2** | 표준 지수 백오프 (1s → 2s → 4s → 8s)<br>일반적으로 검증된 패턴 |
| `sessionRestoreTimeout` | **60초** | 의료 문진 특성상 중간 중단 가능성 고려<br>(예: 보호자 통화, 증상 확인 등) |

### 재시도 시퀀스 예시

```
1차 시도: 즉시 (0초)       → 실패
2차 시도: 2초 대기 후      → 실패
3차 시도: 4초 대기 후      → 실패
4차 시도: 8초 대기 후      → 실패
최종 포기: 사용자에게 수동 새로고침 안내
```

**총 소요 시간**: 14초 (사용자가 견딜 수 있는 최대 시간)

### 대안 설정 (적극적 vs 보수적)

| 시나리오 | maxRetries | baseDelay | maxDelay | 비고 |
|---------|-----------|-----------|----------|------|
| **적극적** | 5 | 1000ms | 16000ms | 네트워크가 불안정한 환경 |
| **권장** | 3 | 2000ms | 8000ms | ⭐ 일반적인 의료 환경 |
| **보수적** | 2 | 3000ms | 6000ms | 빠른 포기, 수동 복구 유도 |

---

## 2. 오디오 UI 스타일

### 컬러/테마 가이드

**권장 컬러 팔레트 (의료 환경)**:

```typescript
const AUDIO_UI_COLORS = {
  // Primary: 신뢰감 있는 블루 계열
  primary: '#2563EB',        // Blue-600 (메인 액션)
  primaryHover: '#1D4ED8',   // Blue-700 (호버)

  // Success: 녹색 (연결 성공, 정상 상태)
  success: '#10B981',        // Green-500
  successLight: '#D1FAE5',   // Green-100 (배경)

  // Warning: 주황색 (재연결 중)
  warning: '#F59E0B',        // Amber-500
  warningLight: '#FEF3C7',   // Amber-100 (배경)

  // Error: 빨간색 (연결 실패, 응급)
  error: '#EF4444',          // Red-500
  errorLight: '#FEE2E2',     // Red-100 (배경)

  // Neutral: 회색 (비활성, 텍스트)
  neutral: '#6B7280',        // Gray-500
  neutralLight: '#F3F4F6',   // Gray-100 (배경)

  // Audio Levels: 그라디언트 (레벨 미터)
  audioLow: '#10B981',       // 낮은 레벨 (녹색)
  audioMid: '#F59E0B',       // 중간 레벨 (주황)
  audioHigh: '#EF4444',      // 높은 레벨 (빨강)
};
```

### 레벨 미터 형태 (3가지 옵션)

#### 옵션 A: 수평 바 (Horizontal Bar) ⭐ **권장**

```
┌──────────────────────────────────┐
│ ████████████░░░░░░░░░░░░░░░░░░░ │  75%
└──────────────────────────────────┘
```

**장점**:
- 직관적 (왼쪽→오른쪽 읽기 자연스러움)
- 고령자도 쉽게 이해
- 구현 간단 (CSS width 조정)

**사용 시나리오**: 기본 권장

---

#### 옵션 B: 원형 게이지 (Circular Gauge)

```
      ╱───╲
    ╱   75% ╲
   │    ●    │
    ╲       ╱
      ╲───╱
```

**장점**:
- 시각적으로 세련됨
- 공간 효율적

**단점**:
- 구현 복잡 (SVG/Canvas 필요)
- 고령자 인지 부담

**사용 시나리오**: 데모/프리젠테이션용

---

#### 옵션 C: 수직 바 (Vertical Bars) - VU 미터 스타일

```
│ │ │ │ │ │ ░ ░ ░ ░
│ │ │ │ │ │ ░ ░ ░ ░
│ │ │ │ │ │ ░ ░ ░ ░
```

**장점**:
- 전문적 (오디오 장비 느낌)
- 여러 채널 표시 가능

**단점**:
- 의료 환경과 맞지 않음
- 공간 많이 차지

**사용 시나리오**: 기술적 데모용

---

### 권장: 옵션 A (수평 바)

**구현 예시**:

```tsx
<div className="audio-level-meter">
  <div
    className="audio-level-bar"
    style={{
      width: `${audioLevel}%`,
      background: getAudioLevelColor(audioLevel)
    }}
  />
</div>

// CSS
.audio-level-meter {
  width: 100%;
  height: 24px;
  background: #F3F4F6;
  border-radius: 12px;
  overflow: hidden;
}

.audio-level-bar {
  height: 100%;
  transition: width 0.1s ease-out;
  border-radius: 12px;
}

// Color logic
function getAudioLevelColor(level: number): string {
  if (level < 30) return '#10B981';  // Green
  if (level < 70) return '#F59E0B';  // Amber
  return '#EF4444';                  // Red
}
```

---

## 3. STT 표시 방식

### 옵션 비교

| 방식 | 장점 | 단점 | 권장도 |
|------|------|------|--------|
| **실시간 스트리밍** | 즉각 피드백, 인터랙티브 | 깜빡임, 혼란 가능 | ⭐⭐ |
| **최종 텍스트만** | 깔끔, 명확 | 피드백 지연, 답답함 | ⭐⭐⭐ **권장** |
| **하이브리드** | 양쪽 장점 결합 | 구현 복잡 | ⭐⭐⭐ **최선** |

---

### 권장: 하이브리드 방식

**구현 방식**:

```tsx
<div className="transcript-container">
  {/* 확정된 이전 발화들 */}
  <div className="transcript-history">
    {confirmedTranscripts.map((text, idx) => (
      <div key={idx} className="transcript-item confirmed">
        <span className="speaker">환자:</span>
        <span className="text">{text}</span>
      </div>
    ))}
  </div>

  {/* 현재 실시간 스트리밍 (임시) */}
  {currentTranscript && (
    <div className="transcript-item streaming">
      <span className="speaker">환자:</span>
      <span className="text text-gray-500 italic">
        {currentTranscript}...
      </span>
    </div>
  )}
</div>
```

**시각적 구분**:
- 확정 텍스트: 검정색, 일반 폰트
- 스트리밍 텍스트: 회색, 이탤릭, "..." 표시

**예시**:

```
환자: 두통이 있어요                    [확정됨 - 검정색]
환자: 어제부터 계속 아팠고...          [스트리밍 중 - 회색 이탤릭]
```

---

### 대안: 최종 텍스트만 (단순 버전)

**고령자 우선 시나리오**:
- 실시간 스트리밍 없음
- 발화 완료 후 한 번에 표시
- 깜빡임 없음, 명확함

```tsx
<div className="transcript-container">
  {transcripts.map((text, idx) => (
    <div key={idx} className="transcript-item">
      <span className="speaker">환자:</span>
      <span className="text">{text}</span>
    </div>
  ))}
</div>
```

---

## 4. 네트워크 상태 문구

### 상태별 권장 문구

| 상태 | 문구 | 컬러 | 아이콘 |
|------|------|------|--------|
| **연결 중** | "음성 연결 중입니다..." | 주황 | 🔄 회전 |
| **연결됨** | "음성 연결 완료" | 녹색 | ✓ |
| **대기 중** | "말씀해 주세요" | 녹색 | 🎤 |
| **듣는 중** | "듣고 있습니다..." | 파랑 | 🎧 파동 |
| **재연결 중** | "재연결 중입니다... (1/3)" | 주황 | 🔄 |
| **연결 실패** | "연결에 실패했습니다<br>페이지를 새로고침해주세요" | 빨강 | ⚠️ |
| **응급 감지** | "⚠️ 응급 증상이 감지되었습니다<br>즉시 119에 연락하세요" | 빨강 | 🚨 |

### 문구 작성 원칙

1. **평어 사용**: "~합니다" (X) → "~해요" (O)
2. **짧고 명확**: 10자 이내 권장
3. **진행 표시**: 재시도 횟수 명시 (1/3)
4. **행동 유도**: "새로고침해주세요" (구체적 안내)
5. **이모지 사용**: 시각적 인지 향상 (선택적)

### 구현 예시

```typescript
const NETWORK_STATUS_MESSAGES = {
  CONNECTING: {
    text: '음성 연결 중이에요...',
    color: 'warning',
    icon: 'spinner',
  },
  CONNECTED: {
    text: '연결 완료',
    color: 'success',
    icon: 'check',
  },
  LISTENING: {
    text: '말씀해 주세요',
    color: 'success',
    icon: 'microphone',
  },
  PROCESSING: {
    text: '듣고 있어요...',
    color: 'primary',
    icon: 'waveform',
  },
  RECONNECTING: (attempt: number, max: number) => ({
    text: `재연결 중이에요... (${attempt}/${max})`,
    color: 'warning',
    icon: 'spinner',
  }),
  FAILED: {
    text: '연결에 실패했어요\n페이지를 새로고침해주세요',
    color: 'error',
    icon: 'alert',
  },
  EMERGENCY: {
    text: '⚠️ 응급 증상이 감지되었어요\n즉시 119에 연락하세요',
    color: 'error',
    icon: 'emergency',
  },
};
```

---

## 5. 음성 시작/중지 UX

### 옵션 비교

| 방식 | 설명 | 장점 | 단점 | 권장도 |
|------|------|------|------|--------|
| **토글** | 클릭 → ON/OFF | 단순, 직관적 | 실수 종료 가능 | ⭐⭐⭐ **권장** |
| **푸시투톡** | 누르는 동안만 녹음 | 명확한 제어 | 손 떼면 중단 (고령자 어려움) | ⭐ |
| **자동 VAD** | 음성 감지 자동 시작 | 편리함 | 오감지, 제어 불가 | ⭐⭐ |

---

### 권장: 토글 방식 + 자동 VAD 조합

**흐름**:

1. **초기 상태**: "시작하기" 버튼 표시
2. **클릭 → 연결 시작**: 마이크 권한 요청 → WebRTC 연결
3. **연결 완료**: 버튼이 "대화 중지" 로 변경, 자동으로 음성 감지 시작
4. **대화 진행**: VAD가 자동으로 발화 감지/전송
5. **중지 버튼 클릭**: 연결 종료

**UI 상태 변화**:

```
[ 시작하기 ]  →  [ 연결 중... ]  →  [ 대화 중지 ]
   (파랑)          (회전 주황)         (빨강)
```

### 버튼 디자인 가이드

```tsx
// 시작 버튼 (큰 사이즈, 명확한 액션)
<button className="voice-button start">
  <MicrophoneIcon className="w-8 h-8" />
  <span className="text-xl font-bold">시작하기</span>
</button>

// 중지 버튼 (위치 동일, 색상만 변경)
<button className="voice-button stop">
  <StopIcon className="w-8 h-8" />
  <span className="text-xl font-bold">대화 중지</span>
</button>

// CSS
.voice-button {
  width: 200px;
  height: 80px;
  border-radius: 40px;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  transition: all 0.2s;
}

.voice-button.start {
  background: #2563EB;  // 파랑
  color: white;
}

.voice-button.start:hover {
  background: #1D4ED8;
  transform: scale(1.05);
}

.voice-button.stop {
  background: #EF4444;  // 빨강
  color: white;
}

.voice-button.stop:hover {
  background: #DC2626;
  transform: scale(1.05);
}
```

### 버튼 크기 가이드 (고령자 고려)

| 요소 | 최소 크기 | 권장 크기 | 이유 |
|------|----------|----------|------|
| 버튼 너비 | 150px | **200px** | 손가락 터치 영역 |
| 버튼 높이 | 60px | **80px** | 시각적 인지 |
| 폰트 크기 | 16px | **20px** | 가독성 |
| 아이콘 크기 | 24px | **32px** | 명확한 의미 전달 |

---

## 6. 전체 화면 레이아웃 예시

```
┌────────────────────────────────────────┐
│          Befora 음성 문진              │  Header
├────────────────────────────────────────┤
│                                        │
│  [✓ 연결 완료]                         │  Status Bar
│                                        │
├────────────────────────────────────────┤
│                                        │
│  ┌──────────────────────────────────┐ │
│  │ 음성 레벨                         │ │
│  │ ████████████░░░░░░░░░░░░░░░░░░░ │ │  Audio Meter
│  └──────────────────────────────────┘ │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │ AI: 어떤 증상으로 방문하시나요?   │ │
│  │ 환자: 두통이 있어요               │ │  Transcript
│  │ 환자: 어제부터 계속...            │ │  (스크롤 가능)
│  └──────────────────────────────────┘ │
│                                        │
│           ┌──────────┐                │
│           │ 🛑 중지  │                │  Main Button
│           └──────────┘                │
│                                        │
└────────────────────────────────────────┘
```

---

## 7. 접근성 (Accessibility) 요구사항

### WCAG 2.1 Level AA 준수

1. **컬러 대비율**: 4.5:1 이상 (텍스트), 3:1 이상 (UI 요소)
2. **키보드 탐색**: Tab, Enter, Space로 모든 기능 사용 가능
3. **스크린 리더**: ARIA 레이블 필수
4. **포커스 표시**: 명확한 포커스 아웃라인

### 구현 예시

```tsx
<button
  className="voice-button start"
  aria-label="음성 문진 시작하기"
  aria-pressed={isRecording}
  tabIndex={0}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      handleStartVoice();
    }
  }}
>
  <MicrophoneIcon aria-hidden="true" />
  <span>시작하기</span>
</button>

<div
  className="audio-level-meter"
  role="progressbar"
  aria-valuenow={audioLevel}
  aria-valuemin={0}
  aria-valuemax={100}
  aria-label={`음성 레벨 ${audioLevel}%`}
/>
```

---

## 8. 반응형 디자인 (모바일 대응)

### 브레이크포인트

```typescript
const BREAKPOINTS = {
  mobile: '640px',   // 스마트폰
  tablet: '768px',   // 태블릿
  desktop: '1024px', // 데스크톱
};
```

### 모바일 최적화

1. **버튼 크기**: 최소 44x44px (iOS 권장)
2. **폰트 크기**: 최소 16px (자동 확대 방지)
3. **여백**: 터치 타겟 간 8px 이상

```css
@media (max-width: 640px) {
  .voice-button {
    width: 100%;
    max-width: 300px;
    height: 64px;
    font-size: 18px;
  }

  .transcript-container {
    max-height: 40vh;
    font-size: 16px;
  }
}
```

---

## 9. 구현 우선순위

### Phase 3.1 (MVP - 필수)
1. ✅ 토글 버튼 (시작/중지)
2. ✅ 수평 바 레벨 미터
3. ✅ 최종 텍스트 표시
4. ✅ 기본 네트워크 상태 (4가지)
5. ✅ 재연결 정책 (3회, 2초, 8초)

### Phase 3.2 (개선 - 권장)
6. 🔄 하이브리드 STT (실시간 + 확정)
7. 🔄 응급 상태 UI
8. 🔄 접근성 강화 (ARIA)

### Phase 3.3 (고급 - 선택)
9. ⏳ 원형 게이지 옵션
10. ⏳ 푸시투톡 대체 모드
11. ⏳ 다크모드

---

## 10. 테스트 체크리스트

### 기능 테스트
- [ ] 버튼 클릭 시 마이크 권한 요청
- [ ] 권한 거부 시 안내 메시지 표시
- [ ] 연결 중 스피너 표시
- [ ] 연결 실패 시 재시도 (3회)
- [ ] 레벨 미터 실시간 업데이트
- [ ] STT 텍스트 표시
- [ ] 중지 버튼 동작
- [ ] 네트워크 끊김 시 자동 재연결

### 사용성 테스트
- [ ] 고령자 (60+) 5명 테스트
- [ ] 버튼 크기 충분한지 확인
- [ ] 문구 이해도 확인
- [ ] 에러 상황 대처 가능 여부

### 접근성 테스트
- [ ] 키보드만으로 전체 플로우 완료
- [ ] 스크린 리더 호환성
- [ ] 컬러 대비율 확인 (WebAIM Contrast Checker)

---

## 참고 자료

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Material Design - Voice & Audio](https://m3.material.io/)
- [Apple Human Interface Guidelines - Audio](https://developer.apple.com/design/human-interface-guidelines/playing-audio)
- [Nielsen Norman Group - Voice UI Design](https://www.nngroup.com/articles/voice-first/)

---

**작성일**: 2025-01-06
**버전**: 1.0
**대상**: Befora PoC Phase 3 구현팀
