import { TRANSCRIPT_CONFIG } from '../constants/ui';
import type { TranscriptViewProps } from '../types/voice';

export function TranscriptView({
  transcripts,
  currentStreaming,
  agentStreaming,
  maxHeight = TRANSCRIPT_CONFIG.maxHeight,
}: TranscriptViewProps) {
  return (
    <div className="transcript-panel" style={{ maxHeight }}>
      <div className="transcript-list">
        {transcripts.map((item) => (
          <div
            key={item.id}
            className={`transcript-item transcript-${item.speaker}`}
          >
            <span className="transcript-label">
              {item.speaker === 'patient' ? '환자' : '문진'}
            </span>
            <p className="transcript-text">{item.text}</p>
          </div>
        ))}
        {currentStreaming && (
          <div className="transcript-item transcript-patient transcript-streaming">
            <span className="transcript-label">환자</span>
            <p className="transcript-text">
              <em>{currentStreaming}...</em>
            </p>
          </div>
        )}
        {agentStreaming && (
          <div className="transcript-item transcript-agent transcript-streaming">
            <span className="transcript-label">문진</span>
            <p className="transcript-text">
              <em>{agentStreaming}...</em>
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
