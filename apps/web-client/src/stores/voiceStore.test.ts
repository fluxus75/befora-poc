import { act } from 'react-dom/test-utils';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { useVoiceStore } from './voiceStore';

vi.mock('../lib/providers', () => {
  return {
    createRealtimeProvider: () => {
      return {
        connect: () => Promise.resolve(),
        reconnect: () => Promise.resolve(),
        disconnect: () => undefined,
        startMic: () => Promise.resolve(),
        stopMic: () => undefined,
        speak: () => Promise.resolve(),
      };
    },
  };
});

describe('voiceStore', () => {
  beforeEach(() => {
    useVoiceStore.setState({
      session: null,
      status: 'IDLE',
      audioLevel: 0,
      isMuted: false,
      vadActive: false,
      networkMetrics: {
        rttMs: null,
        jitterMs: null,
        packetLossPercent: null,
        quality: 'UNKNOWN',
      },
      transcripts: [],
      currentStreaming: null,
      agentStreaming: null,
      currentStep: null,
      error: null,
    });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('creates a session and transitions to connecting', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ session_id: 'session-1' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    );
    vi.stubGlobal('fetch', fetchMock);

    await act(async () => {
      await useVoiceStore.getState().startVoice();
    });

    const state = useVoiceStore.getState();
    expect(state.session?.sessionId).toBe('session-1');
    expect(state.status).toBe('CONNECTING');
  });

  it('maps microphone permission errors', async () => {
    const fetchMock = vi.fn().mockRejectedValue(
      new DOMException('Permission denied', 'NotAllowedError')
    );
    vi.stubGlobal('fetch', fetchMock);

    await act(async () => {
      await useVoiceStore.getState().startVoice();
    });

    const state = useVoiceStore.getState();
    expect(state.status).toBe('FAILED');
    expect(state.error?.type).toBe('MICROPHONE_PERMISSION_DENIED');
  });
});
