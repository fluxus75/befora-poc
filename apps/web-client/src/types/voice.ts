/**
 * Type definitions for Phase 3 Voice Integration
 */

// ============================================================================
// Network Status Types
// ============================================================================

export type NetworkStatus =
  | 'IDLE'
  | 'CONNECTING'
  | 'CONNECTED'
  | 'LISTENING'
  | 'PROCESSING'
  | 'RECONNECTING'
  | 'FAILED'
  | 'EMERGENCY';

export interface StatusMessage {
  text: string;
  color: 'primary' | 'success' | 'warning' | 'error' | 'neutral';
  icon: string;
  ariaLabel?: string;
}

// ============================================================================
// Voice Button Types
// ============================================================================

export type VoiceButtonState = 'START' | 'CONNECTING' | 'STOP';

export interface VoiceButtonConfig {
  text: string;
  backgroundColor: string;
  hoverColor: string;
  icon: string;
  ariaLabel: string;
  disabled?: boolean;
}

// ============================================================================
// Audio Types
// ============================================================================

export interface AudioLevel {
  volume: number; // 0-100
  timestamp: number;
}

export interface AudioMetadata {
  durationMs: number;
  transcriptConfidence?: number;
  volume?: number;
}

// ============================================================================
// Transcript Types
// ============================================================================

export type TranscriptStatus = 'STREAMING' | 'CONFIRMED' | 'FINAL';

export interface TranscriptItem {
  id: string;
  speaker: 'patient' | 'agent';
  text: string;
  status: TranscriptStatus;
  timestamp: number;
  confidence?: number;
}

export interface TranscriptState {
  items: TranscriptItem[];
  currentStreaming: string | null;
  agentStreaming?: string | null;
}

// ============================================================================
// Session Types
// ============================================================================

export interface VoiceSession {
  sessionId: string;
  status: NetworkStatus;
  startedAt: number;
  endedAt?: number;
  reconnectAttempts: number;
  lastDisconnectTime?: number;
}

export type NetworkQuality = 'GOOD' | 'FAIR' | 'POOR' | 'UNKNOWN';

export interface NetworkMetrics {
  rttMs: number | null;
  jitterMs: number | null;
  packetLossPercent: number | null;
  quality: NetworkQuality;
}

// ============================================================================
// WebRTC Connection Types
// ============================================================================

export interface WebRTCConfig {
  iceServers: RTCIceServer[];
}

export interface EphemeralToken {
  token: string;
  expiresIn: number; // seconds
  expiresAt: number; // timestamp
}

export interface ReconnectConfig {
  maxRetries: number;
  baseDelay: number;
  maxDelay: number;
  backoffMultiplier: number;
  sessionRestoreTimeout: number;
}

// ============================================================================
// Error Types
// ============================================================================

export type VoiceErrorType =
  | 'MICROPHONE_PERMISSION_DENIED'
  | 'MICROPHONE_NOT_FOUND'
  | 'NETWORK_ERROR'
  | 'SESSION_EXPIRED'
  | 'UNKNOWN_ERROR';

export interface VoiceError {
  type: VoiceErrorType;
  title: string;
  message: string;
  action: string;
  originalError?: Error;
}

// ============================================================================
// Component Props Types
// ============================================================================

export interface AudioControlsProps {
  state: VoiceButtonState;
  onStart: () => void;
  onStop: () => void;
  disabled?: boolean;
}

export interface AudioLevelMeterProps {
  level: number; // 0-100
  className?: string;
}

export interface NetworkStatusProps {
  status: NetworkStatus;
  retryCount?: number;
  maxRetries?: number;
  metrics?: NetworkMetrics;
}

export interface TranscriptViewProps {
  transcripts: TranscriptItem[];
  currentStreaming?: string;
  agentStreaming?: string;
  maxHeight?: string;
  autoScroll?: boolean;
}

// ============================================================================
// Store State Types (Zustand)
// ============================================================================

export interface VoiceStore {
  // Session state
  session: VoiceSession | null;
  status: NetworkStatus;

  // Audio state
  audioLevel: number;
  isMuted: boolean;
  vadActive: boolean;
  networkMetrics: NetworkMetrics;

  // Transcript state
  transcripts: TranscriptItem[];
  currentStreaming: string | null;
  agentStreaming: string | null;
  currentStep: string | null;

  // Error state
  error: VoiceError | null;

  // Actions
  startVoice: () => Promise<void>;
  stopVoice: () => void;
  updateAudioLevel: (level: number) => void;
  updateNetworkMetrics: (metrics: NetworkMetrics) => void;
  setVadActive: (active: boolean) => void;
  addTranscript: (item: TranscriptItem) => void;
  updateStreamingText: (text: string | null) => void;
  setError: (error: VoiceError | null) => void;
  reconnect: () => Promise<void>;
  reset: () => void;
}

// ============================================================================
// API Request/Response Types
// ============================================================================

export interface CreateSessionRequest {
  patientId?: string;
}

export interface CreateSessionResponse {
  session_id: string;
  status: string;
  created_at: string;
}

export interface GetTokenRequest {
  sessionId: string;
}

export interface GetTokenResponse {
  token: string;
  expires_in: number;
}

export interface ProcessTurnRequest {
  userInput: string;
  audioMetadata?: AudioMetadata;
}

export interface ProcessTurnResponse {
  agent_response: string;
  current_node: string;
  completed: boolean;
  emergency: boolean;
  slots: Record<string, unknown>;
}

// ============================================================================
// OpenAI Realtime API Types (Subset)
// ============================================================================

export interface RealtimeSessionConfig {
  type: 'realtime';
  model: string;
  modalities: ('text' | 'audio')[];
  instructions: string;
  voice: string;
  inputAudioFormat: string;
  outputAudioFormat: string;
  inputAudioTranscription?: {
    model: string;
  };
  turnDetection?: {
    type: string;
    threshold: number;
    prefixPaddingMs: number;
    silenceDurationMs: number;
  };
  temperature: number;
  maxResponseOutputTokens: number;
}

export interface RealtimeEvent {
  type: string;
  eventId?: string;
  // Event-specific fields will vary
  [key: string]: unknown;
}

// ============================================================================
// Utility Types
// ============================================================================

export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type Nullable<T> = T | null;
