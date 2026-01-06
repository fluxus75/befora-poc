import type { NetworkMetrics, NetworkStatus, TranscriptItem } from '../../types/voice';

export type StatusHandler = (status: NetworkStatus) => void;
export type ErrorHandler = (error: Error) => void;
export type TranscriptHandler = (item: TranscriptItem) => void;
export type StreamingHandler = (text: string | null) => void;
export type AgentStreamingHandler = (text: string | null) => void;
export type StepUpdateHandler = (currentStep: string, emergency: boolean) => void;
export type AudioLevelHandler = (level: number) => void;
export type VadHandler = (active: boolean) => void;
export type NetworkHandler = (metrics: NetworkMetrics) => void;

export interface RealtimeProviderOptions {
  onStatusChange: StatusHandler;
  onError: ErrorHandler;
  onTranscript: TranscriptHandler;
  onStreaming: StreamingHandler;
  onAgentStreaming: AgentStreamingHandler;
  onAgentTranscript: TranscriptHandler;
  onAudioLevel: AudioLevelHandler;
  onVadChange: VadHandler;
  onNetworkMetrics: NetworkHandler;
  onStepUpdate: StepUpdateHandler;
}

export interface MockScenarioStep {
  step: string;
  user_input?: string;
  delay_ms?: number;
  vad_duration_ms?: number;
  streaming_chunks?: string[];
  trigger_error?: string;
}

export interface MockScenarioPayload {
  scenarios: Record<string, MockScenarioStep[]>;
}
