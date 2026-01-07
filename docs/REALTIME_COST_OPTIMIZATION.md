# Realtime API 비용 최적화 전략

## 문서 개요

**목적**: OpenAI Realtime API 비용을 최소화하면서 개발/테스트 효율성을 극대화
**작성일**: 2026-01-06
**버전**: v1.0

---

## 1. 문제 정의

### 1.1 현재 비용 발생 지점

OpenAI Realtime API는 다음 3가지 작업을 통합 수행하며, 각각 비용이 발생:

| 기능 | 현재 구현 | 비용 특성 |
|------|----------|----------|
| **A) VAD (턴 감지)** | `turn_detection: { type: 'server_vad' }` | 연결 시간 기반 과금 |
| **B) STT (음성→텍스트)** | `input_audio_transcription: { model: 'whisper-1' }` | 오디오 분당 과금 |
| **C) LLM + TTS** | `response.create` (audio + text modalities) | 토큰 + 오디오 출력 과금 |

**핵심 문제**:
- 개발 중 매번 Realtime API를 호출하면 비용이 누적
- 침묵 구간도 WebRTC로 전송하면 과금 가능성
- UI/DSL 로직 테스트에도 실제 API 필요

### 1.2 비용 최적화 목표

```
┌─────────────────────────────────────────────┐
│ 개발/테스트 90%  →  Mock/Local (비용 0~최소) │
│ 통합 리허설 10%  →  Real Realtime API       │
└─────────────────────────────────────────────┘
```

---

## 2. 아키텍처 설계: Provider 추상화

### 2.1 핵심 전략

현재 `RealtimeClient`를 **인터페이스 기반 Provider 패턴**으로 리팩토링:

```typescript
interface IRealtimeProvider {
  // 연결 관리
  connect(sessionId: string): Promise<void>;
  disconnect(): void;
  reconnect(): Promise<void>;

  // 오디오 입출력
  startMic(): Promise<void>;
  stopMic(): void;
  speak(text: string): Promise<void>;

  // 콜백 (기존 RealtimeClient 인터페이스 유지)
  onStatusChange: StatusHandler;
  onTranscript: TranscriptHandler;
  onAgentTranscript: TranscriptHandler;
  onStreaming: StreamingHandler;
  onAgentStreaming: AgentStreamingHandler;
  onVadChange: VadHandler;
  onAudioLevel: AudioLevelHandler;
  onNetworkMetrics: NetworkHandler;
  onStepUpdate: StepUpdateHandler;
  onError: ErrorHandler;
}
```

### 2.2 Provider 구현체

| Provider | 용도 | 비용 | 품질 |
|----------|------|------|------|
| **OpenAIRealtimeProvider** | 통합 테스트, 데모 | 높음 | 최고 |
| **MockRealtimeProvider** | UI/DSL 로직 테스트 | 0 | N/A (시뮬레이션) |
| **LocalRealtimeProvider** | 기능 개발, 저비용 테스트 | 최소 | 중간 |

### 2.3 환경 변수 기반 전환

**server/config.py 수정**:
```python
class Settings(BaseSettings):
    # ... 기존 설정 ...

    # Provider 선택
    realtime_provider: Literal["openai", "mock", "local"] = Field(
        default="openai",
        validation_alias="REALTIME_PROVIDER"
    )

    # Mock 설정
    mock_scenario_path: str = Field(
        default="server/fixtures/mock_transcripts.json",
        validation_alias="MOCK_SCENARIO_PATH"
    )
    mock_latency_ms: int = Field(
        default=500,
        validation_alias="MOCK_LATENCY_MS"
    )

    # Local STT/TTS 설정
    local_stt_model: str = Field(
        default="base",  # whisper model size
        validation_alias="LOCAL_STT_MODEL"
    )
    local_tts_engine: Literal["browser", "coqui", "piper"] = Field(
        default="browser",
        validation_alias="LOCAL_TTS_ENGINE"
    )
    local_llm_endpoint: str | None = Field(
        default=None,  # e.g., "http://localhost:11434" for Ollama
        validation_alias="LOCAL_LLM_ENDPOINT"
    )
```

**.env.example 업데이트**:
```bash
# Realtime Provider 선택
REALTIME_PROVIDER=mock  # openai | mock | local

# Mock 설정 (REALTIME_PROVIDER=mock일 때)
MOCK_SCENARIO_PATH=server/fixtures/mock_transcripts.json
MOCK_LATENCY_MS=500

# Local 설정 (REALTIME_PROVIDER=local일 때)
LOCAL_STT_MODEL=base  # tiny, base, small, medium, large
LOCAL_TTS_ENGINE=browser  # browser, coqui, piper
LOCAL_LLM_ENDPOINT=http://localhost:11434  # Ollama endpoint (optional)
```

---

## 3. Mock Provider 구현 (우선순위 1)

### 3.1 목표

**비용 0으로 다음을 테스트**:
- UI 상태 전환 (IDLE → CONNECTING → LISTENING → PROCESSING)
- Transcript streaming 표시
- DSL 시나리오 처리 (`/api/sessions/{id}/process`)
- 에이전트 응답 표시
- 네트워크 품질 UI
- 오류 처리/재연결 로직

### 3.2 Mock 데이터 구조

**server/fixtures/mock_transcripts.json**:
```json
{
  "scenarios": {
    "normal_flow": [
      {
        "step": "greeting",
        "user_input": "안녕하세요",
        "delay_ms": 500,
        "vad_duration_ms": 1200,
        "streaming_chunks": ["안녕", "하세요"]
      },
      {
        "step": "chief_complaint",
        "user_input": "머리가 아파요",
        "delay_ms": 600,
        "vad_duration_ms": 1500,
        "streaming_chunks": ["머리가", " 아파요"]
      }
    ],
    "emergency_flow": [
      {
        "step": "emergency_keyword",
        "user_input": "갑자기 가슴이 너무 아파요",
        "delay_ms": 400,
        "vad_duration_ms": 2000,
        "streaming_chunks": ["갑자기", " 가슴이", " 너무", " 아파요"]
      }
    ],
    "error_cases": [
      {
        "step": "empty_transcript",
        "user_input": "",
        "delay_ms": 800,
        "vad_duration_ms": 500
      },
      {
        "step": "network_disconnect",
        "trigger_error": "connection_lost",
        "delay_ms": 2000
      }
    ]
  }
}
```

### 3.3 MockRealtimeProvider 구현 개요

**apps/web-client/src/lib/providers/MockRealtimeProvider.ts**:

```typescript
export class MockRealtimeProvider implements IRealtimeProvider {
  private scenario: MockScenario[];
  private currentStepIndex = 0;
  private timers: number[] = [];

  async connect(sessionId: string): Promise<void> {
    // 1. Mock 시나리오 로드
    this.scenario = await this.loadScenario(sessionId);

    // 2. 연결 시뮬레이션
    this.onStatusChange('CONNECTING');
    await this.sleep(300);
    this.onStatusChange('CONNECTED');
    await this.sleep(200);
    this.onStatusChange('LISTENING');
  }

  async startMic(): Promise<void> {
    // 다음 시나리오 스텝 자동 실행
    await this.playNextScenarioStep();
  }

  private async playNextScenarioStep(): Promise<void> {
    const step = this.scenario[this.currentStepIndex];
    if (!step) return;

    // 1. VAD 시작
    await this.sleep(step.delay_ms);
    this.onVadChange(true);
    this.onStatusChange('PROCESSING');

    // 2. Streaming transcript
    for (const chunk of step.streaming_chunks) {
      await this.sleep(100);
      this.onStreaming(chunk);
    }

    // 3. Transcript 완료
    await this.sleep(200);
    this.onTranscript({
      id: crypto.randomUUID(),
      speaker: 'patient',
      text: step.user_input,
      status: 'CONFIRMED',
      timestamp: Date.now()
    });
    this.onStreaming(null);
    this.onVadChange(false);

    // 4. DSL 처리 (실제 백엔드 호출)
    await this.sendToDsl(step.user_input);

    this.currentStepIndex++;
    this.onStatusChange('LISTENING');
  }

  async speak(text: string): Promise<void> {
    // Agent 응답 스트리밍 시뮬레이션
    const words = text.split(' ');
    for (const word of words) {
      await this.sleep(150);
      this.onAgentStreaming(word + ' ');
    }

    this.onAgentTranscript({
      id: crypto.randomUUID(),
      speaker: 'agent',
      text: text,
      status: 'FINAL',
      timestamp: Date.now()
    });
    this.onAgentStreaming(null);

    // 브라우저 TTS로 실제 발화 (선택)
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'ko-KR';
      window.speechSynthesis.speak(utterance);
    }
  }

  private async sendToDsl(transcript: string): Promise<void> {
    // 실제 DSL 엔진 호출 (Mock이어도 로직 테스트)
    const response = await fetch(
      buildApiUrl(`/api/sessions/${this.sessionId}/process`),
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_input: transcript })
      }
    );

    const data = await response.json();
    this.onStepUpdate(data.current_node, data.emergency);
    await this.speak(data.agent_response);
  }
}
```

### 3.4 Mock 테스트 시나리오

**개발자가 제어 가능한 테스트 케이스**:

```typescript
// 정상 플로우
MOCK_SCENARIO=normal_flow pnpm dev

// 응급 키워드 감지
MOCK_SCENARIO=emergency_flow pnpm dev

// 오류 시뮬레이션
MOCK_SCENARIO=error_cases pnpm dev
```

---

## 4. Local Provider 구현 (우선순위 2)

### 4.1 아키텍처

```
┌─────────────┐
│  Browser    │
│  (마이크)   │
└──────┬──────┘
       │ WebSocket or Server-Sent Events
       ▼
┌─────────────────────────────────────┐
│  FastAPI Backend                    │
│  ┌───────────────────────────────┐  │
│  │ LocalRealtimeService          │  │
│  │  - VAD: webrtcvad / silero    │  │
│  │  - STT: faster-whisper        │  │
│  │  - LLM: Ollama (optional)     │  │
│  │  - TTS: browser fallback      │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

### 4.2 기술 스택

| 컴포넌트 | 오픈소스 옵션 | 비고 |
|----------|--------------|------|
| **VAD** | webrtcvad, silero-vad | 로컬 실행 가능 |
| **STT** | faster-whisper, whisper.cpp | GPU 사용 시 실시간 가능 |
| **LLM** | Ollama (qwen2.5, llama3.2) | 선택사항, 텍스트 모델로도 가능 |
| **TTS** | Browser SpeechSynthesis, Piper TTS | 한국어 품질은 브라우저가 나음 |

### 4.3 의존성 추가

**pyproject.toml**:
```toml
[project.optional-dependencies]
local-realtime = [
    "faster-whisper>=1.0.0",
    "webrtcvad>=2.0.10",
    "pydub>=0.25.1",
    "websockets>=12.0",
]
```

### 4.4 LocalRealtimeProvider 핵심 로직

**server/services/local_realtime.py**:
```python
from faster_whisper import WhisperModel
import webrtcvad
import asyncio

class LocalRealtimeService:
    def __init__(self, model_size: str = "base"):
        self.whisper = WhisperModel(model_size, device="cpu")
        self.vad = webrtcvad.Vad(mode=3)  # Aggressive mode

    async def transcribe_stream(self, audio_chunks: AsyncIterator[bytes]):
        """
        실시간 오디오 스트림을 전사
        """
        buffer = []

        async for chunk in audio_chunks:
            # 1. VAD 체크
            is_speech = self.vad.is_speech(chunk, sample_rate=16000)

            if is_speech:
                buffer.append(chunk)
            elif buffer:
                # 2. 침묵 감지 시 버퍼 전사
                audio_data = b''.join(buffer)
                segments, info = self.whisper.transcribe(
                    audio_data,
                    language="ko",
                    beam_size=1,  # 속도 최적화
                    vad_filter=True
                )

                for segment in segments:
                    yield {
                        "type": "transcript.completed",
                        "text": segment.text.strip()
                    }

                buffer.clear()
```

### 4.5 비용 비교

| 작업 | OpenAI Realtime | Local Stack |
|------|-----------------|-------------|
| 10분 통화 STT | ~$0.30 | $0 |
| LLM 응답 (100회) | ~$2.00 | $0 (로컬 Ollama) |
| TTS (1000단어) | ~$0.50 | $0 (브라우저) |
| **합계** | **~$2.80** | **$0** |

---

## 5. 실전 비용 절감 팁 (Real Realtime 사용 시)

### 5.1 Push-to-Talk 모드

**현재 문제**: 마이크가 켜지면 침묵도 계속 전송
**해결**: 버튼을 누를 때만 오디오 전송

```typescript
// apps/web-client/src/components/AudioControls.tsx
const [isPushToTalkMode, setIsPushToTalkMode] = useState(true);
const [isTransmitting, setIsTransmitting] = useState(false);

const handlePushToTalk = (pressed: boolean) => {
  if (pressed) {
    realtimeClient.startMic();
    setIsTransmitting(true);
  } else {
    realtimeClient.stopMic();
    setIsTransmitting(false);
  }
};
```

### 5.2 Modalities 최소화

**개발 중**: `modalities: ['text']`만 사용
**데모/테스트**: `modalities: ['audio', 'text']`

```typescript
speak(text: string, includeAudio: boolean = false): void {
  const modalities = includeAudio ? ['audio', 'text'] : ['text'];

  this.sendEvent({
    type: 'response.create',
    response: {
      modalities,
      instructions: text
    }
  });
}
```

### 5.3 Max Tokens 제한

```python
# server/config.py
realtime_max_tokens: int = Field(
    default=512,  # 4096에서 줄임
    ge=1,
    le=16384
)
```

### 5.4 세션 타임아웃

```typescript
// 5분 무활동 시 자동 종료
const INACTIVITY_TIMEOUT_MS = 5 * 60 * 1000;

private resetInactivityTimer(): void {
  clearTimeout(this.inactivityTimer);
  this.inactivityTimer = setTimeout(() => {
    this.disconnect();
  }, INACTIVITY_TIMEOUT_MS);
}
```

---

## 6. 구현 로드맵

### Phase 1: Mock Provider (1주)
- [ ] `IRealtimeProvider` 인터페이스 정의
- [ ] `MockRealtimeProvider` 구현
- [ ] Mock 시나리오 데이터 작성
- [ ] 환경 변수 기반 Provider 전환 로직
- [ ] UI/DSL 통합 테스트

### Phase 2: Local Provider (2주)
- [ ] faster-whisper 연동
- [ ] WebSocket 기반 오디오 스트리밍
- [ ] VAD 구현
- [ ] 브라우저 TTS fallback 개선
- [ ] Ollama LLM 연동

### Phase 3: OpenAI Provider 최적화 (1주)
- [ ] Push-to-Talk 모드 구현
- [ ] Modalities 동적 전환
- [ ] 세션 타임아웃 구현
- [ ] 비용 모니터링 대시보드

---

## 7. 테스트 전략

### 7.1 개발 단계별 Provider 사용

| 작업 | Provider | 비용 |
|------|----------|------|
| UI 개발 | Mock | $0 |
| DSL 로직 테스트 | Mock | $0 |
| STT 정확도 테스트 | Local | ~$0 |
| 전체 통합 테스트 | OpenAI | ~$1 |
| 데모/발표 | OpenAI | ~$2 |

### 7.2 자동 테스트

```typescript
// apps/web-client/src/__tests__/realtime-providers.test.ts
describe('RealtimeProviders', () => {
  it('Mock: 정상 플로우', async () => {
    const provider = new MockRealtimeProvider({
      scenario: 'normal_flow',
      ...callbacks
    });

    await provider.connect('test-session');
    // assertions...
  });

  it('Local: STT 정확도', async () => {
    const provider = new LocalRealtimeProvider({...});
    // 실제 오디오 파일로 테스트
  });
});
```

---

## 8. 비용 모니터링

### 8.1 사용량 추적

**server/services/usage_tracker.py**:
```python
from datetime import datetime
from typing import Dict

class RealtimeUsageTracker:
    def __init__(self):
        self.sessions: Dict[str, dict] = {}

    def track_session_start(self, session_id: str, provider: str):
        self.sessions[session_id] = {
            "provider": provider,
            "start_time": datetime.now(),
            "audio_seconds": 0,
            "token_count": 0
        }

    def track_audio_duration(self, session_id: str, seconds: float):
        if session_id in self.sessions:
            self.sessions[session_id]["audio_seconds"] += seconds

    def estimate_cost(self, session_id: str) -> float:
        """
        OpenAI Realtime API 비용 추정
        """
        session = self.sessions.get(session_id)
        if not session or session["provider"] != "openai":
            return 0.0

        # 예시 요금 (실제 요금은 OpenAI 문서 참조)
        audio_cost = session["audio_seconds"] / 60 * 0.06  # $0.06/min
        token_cost = session["token_count"] / 1000 * 0.002  # 예시

        return audio_cost + token_cost
```

### 8.2 대시보드

```typescript
// apps/doctor-dashboard/src/components/CostMonitor.tsx
interface UsageStats {
  totalSessions: number;
  mockSessions: number;
  localSessions: number;
  openaiSessions: number;
  estimatedCost: number;
}

export const CostMonitor: React.FC = () => {
  const stats = useCostStats();

  return (
    <Card>
      <h3>Realtime API 사용 현황</h3>
      <Stat label="Mock" value={stats.mockSessions} cost="$0" />
      <Stat label="Local" value={stats.localSessions} cost="~$0" />
      <Stat label="OpenAI" value={stats.openaiSessions} cost={`$${stats.estimatedCost.toFixed(2)}`} />
    </Card>
  );
};
```

---

## 9. 마이그레이션 가이드

### 9.1 기존 코드 수정 지점

**apps/web-client/src/lib/api.ts**:
```typescript
// Before
import { RealtimeClient } from './realtime';

// After
import { createRealtimeProvider } from './providers';

export function createRealtimeClient(options: RealtimeClientOptions) {
  const provider = import.meta.env.VITE_REALTIME_PROVIDER || 'openai';
  return createRealtimeProvider(provider, options);
}
```

**apps/web-client/src/stores/voiceStore.ts**:
```typescript
// 변경 없음 - Provider 인터페이스가 동일하므로
const realtimeClient = createRealtimeClient({
  onStatusChange: (status) => set({ status }),
  onTranscript: (item) => set((state) => ({
    transcripts: [...state.transcripts, item]
  })),
  // ... 기존 콜백 유지
});
```

### 9.2 환경별 설정

**개발 환경**:
```bash
# .env.development
REALTIME_PROVIDER=mock
MOCK_SCENARIO_PATH=server/fixtures/mock_transcripts.json
```

**스테이징 환경**:
```bash
# .env.staging
REALTIME_PROVIDER=local
LOCAL_STT_MODEL=base
```

**프로덕션 환경**:
```bash
# .env.production
REALTIME_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

---

## 10. 참고 자료

### 10.1 오픈소스 도구

- **faster-whisper**: https://github.com/guillaumekln/faster-whisper
- **Piper TTS**: https://github.com/rhasspy/piper
- **Ollama**: https://ollama.ai/
- **webrtcvad**: https://github.com/wiseman/py-webrtcvad

### 10.2 OpenAI 문서

- Realtime API Pricing: https://openai.com/api/pricing/
- Transcription Intent: https://platform.openai.com/docs/guides/realtime

---

## 11. 결론

### 11.1 예상 비용 절감

| 시나리오 | Before (OpenAI 전용) | After (Mixed) | 절감률 |
|----------|---------------------|---------------|--------|
| 1주 개발 (50회 테스트) | ~$50 | ~$5 | **90%** |
| 1개월 개발 | ~$200 | ~$20 | **90%** |
| PoC 완료 (3개월) | ~$600 | ~$60 | **90%** |

### 11.2 기대 효과

1. **비용 효율성**: 개발 단계에서 90% 이상 비용 절감
2. **개발 속도**: API 의존도 감소로 빠른 반복 개발
3. **테스트 커버리지**: Mock으로 엣지 케이스 완벽 검증
4. **오프라인 개발**: Local Provider로 네트워크 없이도 개발 가능
5. **확장성**: 향후 다른 Realtime API(Gemini, Azure 등) 전환 용이

---

**다음 단계**: Phase 1 (Mock Provider) 구현 시작
