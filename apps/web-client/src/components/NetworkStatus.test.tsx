import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { NetworkStatus } from './NetworkStatus';

describe('NetworkStatus', () => {
  it('renders connecting message', () => {
    render(<NetworkStatus status="CONNECTING" />);
    expect(screen.getByText('연결 중이에요')).toBeInTheDocument();
  });

  it('renders reconnecting message and metrics', () => {
    render(
      <NetworkStatus
        status="RECONNECTING"
        retryCount={2}
        maxRetries={3}
        metrics={{ rttMs: 120, jitterMs: null, packetLossPercent: null, quality: 'GOOD' }}
      />
    );

    expect(screen.getByText('재연결 중이에요 (2/3)')).toBeInTheDocument();
    expect(screen.getByText('120ms')).toBeInTheDocument();
    expect(screen.getByText('좋음')).toBeInTheDocument();
  });
});
