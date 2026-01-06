import {
  AUDIO_UI_COLORS,
  NETWORK_STATUS_MESSAGES,
  getReconnectingMessage,
} from '../constants/ui';
import type { NetworkStatusProps } from '../types/voice';

export function NetworkStatus({
  status,
  retryCount,
  maxRetries,
  metrics,
}: NetworkStatusProps) {
  const message =
    status === 'RECONNECTING'
      ? getReconnectingMessage(retryCount ?? 1, maxRetries ?? 3)
      : NETWORK_STATUS_MESSAGES[status];
  const color = AUDIO_UI_COLORS[message.color];

  return (
    <div className="network-status" aria-live="polite">
      <span className="network-dot" style={{ backgroundColor: color }} />
      <span className="network-text">{message.text}</span>
      {metrics?.rttMs !== null && (
        <span className="network-metric">{metrics.rttMs}ms</span>
      )}
      {metrics?.quality && (
        <span className={`network-quality network-quality-${metrics.quality}`}>
          {metrics.quality === 'GOOD'
            ? '좋음'
            : metrics.quality === 'FAIR'
              ? '보통'
              : metrics.quality === 'POOR'
                ? '불안정'
                : '확인 중'}
        </span>
      )}
    </div>
  );
}
