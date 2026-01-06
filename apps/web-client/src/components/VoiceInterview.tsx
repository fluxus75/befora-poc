import { useMemo } from 'react';

import { AudioControls } from './AudioControls';
import { AudioLevelMeter } from './AudioLevelMeter';
import { NetworkStatus } from './NetworkStatus';
import { TranscriptView } from './TranscriptView';
import { RECONNECT_CONFIG } from '../constants/ui';
import { useVoiceStore } from '../stores/voiceStore';

export function VoiceInterview() {
  const {
    status,
    audioLevel,
    vadActive,
    networkMetrics,
    transcripts,
    currentStreaming,
    agentStreaming,
    currentStep,
    error,
    startVoice,
    stopVoice,
  } = useVoiceStore();

  const buttonState = useMemo(() => {
    if (status === 'CONNECTING' || status === 'RECONNECTING') {
      return 'CONNECTING' as const;
    }
    if (status === 'CONNECTED' || status === 'LISTENING' || status === 'PROCESSING') {
      return 'STOP' as const;
    }
    return 'START' as const;
  }, [status]);

  const handleErrorAction = () => {
    if (!error) return;
    if (error.type === 'SESSION_EXPIRED') {
      window.location.reload();
      return;
    }
    startVoice();
  };

  return (
    <main className="voice-page">
      <section className="voice-card">
        <header className="voice-header">
          <h1>음성 문진</h1>
          <p>마이크를 켜고 간단히 증상을 말씀해 주세요.</p>
        </header>

        <NetworkStatus
          status={status}
          maxRetries={RECONNECT_CONFIG.maxRetries}
          metrics={networkMetrics}
        />

        {currentStep && (
          <div className="step-panel" role="status">
            <span className="step-label">진행 단계</span>
            <span className="step-value">{currentStep}</span>
          </div>
        )}

        <div className="audio-panel">
          <div className="audio-level">
            <span className="audio-label">
              {vadActive ? '말씀 중' : '대기 중'}
            </span>
            <AudioLevelMeter level={audioLevel} />
          </div>
        </div>

        {error && (
          <div className="error-panel" role="alert">
            <h2>{error.title}</h2>
            <p>{error.message}</p>
            <button type="button" onClick={handleErrorAction}>
              {error.action}
            </button>
          </div>
        )}

        <TranscriptView
          transcripts={transcripts}
          currentStreaming={currentStreaming ?? undefined}
          agentStreaming={agentStreaming ?? undefined}
        />

        <div className="controls">
          <AudioControls
            state={buttonState}
            onStart={startVoice}
            onStop={stopVoice}
          />
        </div>
      </section>
    </main>
  );
}
