import { describe, expect, it, vi } from 'vitest';

import { LocalRealtimeProvider } from '../lib/providers/LocalRealtimeProvider';
import { MockRealtimeProvider } from '../lib/providers/MockRealtimeProvider';
import { createRealtimeProvider } from '../lib/providers';

describe('createRealtimeProvider', () => {
  it('creates a mock provider', () => {
    const provider = createRealtimeProvider('mock', {
      onStatusChange: vi.fn(),
      onError: vi.fn(),
      onTranscript: vi.fn(),
      onStreaming: vi.fn(),
      onAgentStreaming: vi.fn(),
      onAgentTranscript: vi.fn(),
      onAudioLevel: vi.fn(),
      onVadChange: vi.fn(),
      onNetworkMetrics: vi.fn(),
      onStepUpdate: vi.fn(),
    });

    expect(provider).toBeInstanceOf(MockRealtimeProvider);
  });

  it('creates a local provider', () => {
    const provider = createRealtimeProvider('local', {
      onStatusChange: vi.fn(),
      onError: vi.fn(),
      onTranscript: vi.fn(),
      onStreaming: vi.fn(),
      onAgentStreaming: vi.fn(),
      onAgentTranscript: vi.fn(),
      onAudioLevel: vi.fn(),
      onVadChange: vi.fn(),
      onNetworkMetrics: vi.fn(),
      onStepUpdate: vi.fn(),
    });

    expect(provider).toBeInstanceOf(LocalRealtimeProvider);
  });
});
