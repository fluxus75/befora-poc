import { create } from 'zustand';

import { ERROR_MESSAGES } from '../constants/ui';
import { buildApiUrl } from '../lib/api';
import { createRealtimeProvider } from '../lib/providers';
import type { IRealtimeProvider } from '../lib/providers';
import type {
  NetworkMetrics,
  VoiceError,
  VoiceSession,
  VoiceStore,
} from '../types/voice';

const defaultNetworkMetrics: NetworkMetrics = {
  rttMs: null,
  jitterMs: null,
  packetLossPercent: null,
  quality: 'UNKNOWN',
};

let realtimeClient: IRealtimeProvider | null = null;

async function createSession(): Promise<VoiceSession> {
  const response = await fetch(buildApiUrl('/api/sessions'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({}),
  });
  if (!response.ok) {
    throw new Error(`세션 생성 실패 (${response.status})`);
  }
  const data = (await response.json()) as { session_id: string };
  return {
    sessionId: data.session_id,
    status: 'CONNECTING',
    startedAt: Date.now(),
    reconnectAttempts: 0,
  };
}

function buildError(error: Error): VoiceError {
  const domError = error as DOMException;
  const name = domError.name?.toLowerCase();
  const message = error.message.toLowerCase();
  if (name?.includes('notallowed') || message.includes('permission')) {
    return {
      type: 'MICROPHONE_PERMISSION_DENIED',
      ...ERROR_MESSAGES.MICROPHONE_PERMISSION_DENIED,
      originalError: error,
    };
  }
  if (name?.includes('notfound') || message.includes('notfound')) {
    return {
      type: 'MICROPHONE_NOT_FOUND',
      ...ERROR_MESSAGES.MICROPHONE_NOT_FOUND,
      originalError: error,
    };
  }
  if (message.includes('token') || message.includes('network')) {
    return {
      type: 'NETWORK_ERROR',
      ...ERROR_MESSAGES.NETWORK_ERROR,
      originalError: error,
    };
  }
  return {
    type: 'UNKNOWN_ERROR',
    ...ERROR_MESSAGES.UNKNOWN_ERROR,
    originalError: error,
  };
}

export const useVoiceStore = create<VoiceStore>((set, get) => ({
  session: null,
  status: 'IDLE',
  audioLevel: 0,
  isMuted: false,
  vadActive: false,
  networkMetrics: defaultNetworkMetrics,
  transcripts: [],
  currentStreaming: null,
  agentStreaming: null,
  currentStep: null,
  error: null,

  startVoice: async () => {
    set({ status: 'CONNECTING', error: null });
    try {
      const session = await createSession();
      const provider =
        (import.meta.env.VITE_REALTIME_PROVIDER as string | undefined) ??
        'openai';
      const client =
        realtimeClient ??
        createRealtimeProvider(provider, {
          onStatusChange: (status) =>
            set((state) =>
              state.status === 'EMERGENCY'
                ? state
                : {
                    status,
                    error: status === 'FAILED' ? state.error : null,
                  }
            ),
          onError: (error) => set({ error: buildError(error) }),
          onTranscript: (item) =>
            set((state) => ({
              transcripts: [...state.transcripts, item],
              error: null,
            })),
          onStreaming: (text) => set({ currentStreaming: text, error: null }),
          onAgentStreaming: (text) =>
            set({ agentStreaming: text, error: null }),
          onAudioLevel: (level) => set({ audioLevel: level }),
          onVadChange: (active) => set({ vadActive: active }),
          onNetworkMetrics: (metrics) => set({ networkMetrics: metrics }),
          onAgentTranscript: (item) =>
            set((state) => ({
              transcripts: [...state.transcripts, item],
              agentStreaming: null,
              error: null,
            })),
          onStepUpdate: (currentStep, emergency) =>
            set((state) => ({
              currentStep,
              status: emergency ? 'EMERGENCY' : state.status,
              error: null,
            })),
        });
      realtimeClient = client;
      await client.connect(session.sessionId);
      await client.startMic();
      set({ session });
    } catch (error) {
      set({ status: 'FAILED', error: buildError(error as Error) });
    }
  },

  stopVoice: () => {
    realtimeClient?.stopMic();
    realtimeClient?.disconnect();
    set({
      session: null,
      status: 'IDLE',
      audioLevel: 0,
      vadActive: false,
      agentStreaming: null,
      currentStep: null,
      currentStreaming: null,
      networkMetrics: defaultNetworkMetrics,
      error: null,
    });
  },

  updateAudioLevel: (level) => set({ audioLevel: level }),
  updateNetworkMetrics: (metrics) => set({ networkMetrics: metrics }),
  setVadActive: (active) => set({ vadActive: active }),
  addTranscript: (item) =>
    set((state) => ({ transcripts: [...state.transcripts, item] })),
  updateStreamingText: (text) => set({ currentStreaming: text }),
  setError: (error) => set({ error }),

  reconnect: async () => {
    if (!realtimeClient || !get().session) {
      return;
    }
    set({ status: 'RECONNECTING' });
    await realtimeClient.reconnect();
  },

  reset: () =>
    set({
      session: null,
      status: 'IDLE',
      audioLevel: 0,
      isMuted: false,
      vadActive: false,
      networkMetrics: defaultNetworkMetrics,
      transcripts: [],
      currentStreaming: null,
      agentStreaming: null,
      currentStep: null,
      error: null,
    }),
}));
