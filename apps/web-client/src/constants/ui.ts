/**
 * UI/UX Constants for Phase 3 Voice Integration
 *
 * Based on: docs/PHASE3_UX_GUIDELINES.md
 */

// ============================================================================
// 1. Reconnection Policy
// ============================================================================

export const RECONNECT_CONFIG = {
  maxRetries: 3, // Maximum retry attempts
  baseDelay: 2000, // Initial delay in ms (2 seconds)
  maxDelay: 8000, // Maximum delay in ms (8 seconds)
  backoffMultiplier: 2, // Exponential backoff multiplier
  sessionRestoreTimeout: 60, // Session restore timeout in seconds
} as const;

// ============================================================================
// 2. Audio UI Colors
// ============================================================================

export const AUDIO_UI_COLORS = {
  // Primary: Trustworthy blue
  primary: '#2563EB', // Blue-600
  primaryHover: '#1D4ED8', // Blue-700

  // Success: Green (connected, normal state)
  success: '#10B981', // Green-500
  successLight: '#D1FAE5', // Green-100

  // Warning: Amber (reconnecting)
  warning: '#F59E0B', // Amber-500
  warningLight: '#FEF3C7', // Amber-100

  // Error: Red (connection failed, emergency)
  error: '#EF4444', // Red-500
  errorLight: '#FEE2E2', // Red-100

  // Neutral: Gray (inactive, text)
  neutral: '#6B7280', // Gray-500
  neutralLight: '#F3F4F6', // Gray-100

  // Audio Levels: Gradient colors
  audioLow: '#10B981', // Green
  audioMid: '#F59E0B', // Amber
  audioHigh: '#EF4444', // Red
} as const;

/**
 * Get audio level color based on volume percentage
 */
export function getAudioLevelColor(level: number): string {
  if (level < 30) return AUDIO_UI_COLORS.audioLow;
  if (level < 70) return AUDIO_UI_COLORS.audioMid;
  return AUDIO_UI_COLORS.audioHigh;
}

// ============================================================================
// 3. Network Status Messages
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
  color: keyof typeof AUDIO_UI_COLORS;
  icon: string;
  ariaLabel?: string;
}

export const NETWORK_STATUS_MESSAGES: Record<
  Exclude<NetworkStatus, 'RECONNECTING'>,
  StatusMessage
> = {
  IDLE: {
    text: '대기 중',
    color: 'neutral',
    icon: 'idle',
    ariaLabel: '음성 연결 대기 중',
  },
  CONNECTING: {
    text: '연결 중이에요',
    color: 'warning',
    icon: 'spinner',
    ariaLabel: '음성 연결 중입니다',
  },
  CONNECTED: {
    text: '연결 완료',
    color: 'success',
    icon: 'check',
    ariaLabel: '음성 연결이 완료되었습니다',
  },
  LISTENING: {
    text: '말씀해요',
    color: 'success',
    icon: 'microphone',
    ariaLabel: '음성 입력을 기다리고 있습니다',
  },
  PROCESSING: {
    text: '듣고 있어요',
    color: 'primary',
    icon: 'waveform',
    ariaLabel: '음성을 처리하고 있습니다',
  },
  FAILED: {
    text: '연결 실패예요',
    color: 'error',
    icon: 'alert',
    ariaLabel: '연결에 실패했습니다. 페이지를 새로고침해주세요',
  },
  EMERGENCY: {
    text: '응급이에요',
    color: 'error',
    icon: 'emergency',
    ariaLabel: '응급 증상이 감지되었습니다. 즉시 119에 연락하세요',
  },
};

/**
 * Get reconnecting status message with attempt count
 */
export function getReconnectingMessage(
  attempt: number,
  maxAttempts: number
): StatusMessage {
  return {
    text: `재연결 중이에요 (${attempt}/${maxAttempts})`,
    color: 'warning',
    icon: 'spinner',
    ariaLabel: `재연결 시도 중입니다. ${attempt}번째 시도 중 최대 ${maxAttempts}번`,
  };
}

// ============================================================================
// 4. Button Sizes (Accessibility - Elderly Users)
// ============================================================================

export const BUTTON_SIZES = {
  width: 200, // px
  height: 80, // px
  fontSize: 20, // px
  iconSize: 32, // px
  borderRadius: 40, // px
} as const;

export const MOBILE_BUTTON_SIZES = {
  width: '100%',
  maxWidth: 300, // px
  height: 64, // px
  fontSize: 18, // px
  iconSize: 28, // px
  borderRadius: 32, // px
} as const;

// ============================================================================
// 5. Audio Level Meter Configuration
// ============================================================================

export const AUDIO_METER_CONFIG = {
  height: 24, // px
  borderRadius: 12, // px
  transitionDuration: 100, // ms
  updateInterval: 50, // ms (20 FPS)
} as const;

// ============================================================================
// 6. Transcript Display Configuration
// ============================================================================

export const TRANSCRIPT_CONFIG = {
  maxHeight: '50vh', // Mobile: 40vh
  fontSize: 16, // px
  lineHeight: 1.6,
  padding: 16, // px
  showTimestamps: false, // PoC: false for simplicity
} as const;

// ============================================================================
// 7. Breakpoints (Responsive Design)
// ============================================================================

export const BREAKPOINTS = {
  mobile: 640, // px
  tablet: 768, // px
  desktop: 1024, // px
} as const;

// ============================================================================
// 8. Animation Durations
// ============================================================================

export const ANIMATION_DURATIONS = {
  fast: 150, // ms
  normal: 200, // ms
  slow: 300, // ms
  spinner: 1000, // ms (1 full rotation)
} as const;

// ============================================================================
// 9. Voice Button States
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

export const VOICE_BUTTON_CONFIGS: Record<VoiceButtonState, VoiceButtonConfig> =
  {
    START: {
      text: '시작하기',
      backgroundColor: AUDIO_UI_COLORS.primary,
      hoverColor: AUDIO_UI_COLORS.primaryHover,
      icon: 'microphone',
      ariaLabel: '음성 문진 시작하기',
      disabled: false,
    },
    CONNECTING: {
      text: '연결 중...',
      backgroundColor: AUDIO_UI_COLORS.warning,
      hoverColor: AUDIO_UI_COLORS.warning,
      icon: 'spinner',
      ariaLabel: '음성 연결 중입니다',
      disabled: true,
    },
    STOP: {
      text: '대화 중지',
      backgroundColor: AUDIO_UI_COLORS.error,
      hoverColor: '#DC2626', // Red-600
      icon: 'stop',
      ariaLabel: '음성 대화 중지하기',
      disabled: false,
    },
  };

// ============================================================================
// 10. Accessibility (WCAG 2.1 Level AA)
// ============================================================================

export const ACCESSIBILITY = {
  // Minimum touch target size (iOS/Android guidelines)
  minTouchTarget: 44, // px

  // Minimum font size (prevent auto-zoom on mobile)
  minFontSize: 16, // px

  // Color contrast ratios
  textContrast: 4.5, // 4.5:1 for normal text
  uiContrast: 3, // 3:1 for UI components

  // Focus outline
  focusOutlineWidth: 2, // px
  focusOutlineColor: AUDIO_UI_COLORS.primary,
  focusOutlineOffset: 2, // px
} as const;

// ============================================================================
// 11. WebRTC Audio Configuration
// ============================================================================

export const WEBRTC_AUDIO_CONFIG = {
  echoCancellation: true,
  noiseSuppression: true,
  autoGainControl: true,
  sampleRate: 24000, // 24kHz (OpenAI Realtime default)
  channelCount: 1, // Mono
} as const;

// ============================================================================
// 12. Error Messages (User-Friendly)
// ============================================================================

export const ERROR_MESSAGES = {
  MICROPHONE_PERMISSION_DENIED: {
    title: '마이크 권한이 필요해요',
    message:
      '음성 문진을 위해 마이크 권한이 필요합니다.\n브라우저 설정에서 마이크 권한을 허용해주세요.',
    action: '설정으로 이동',
  },
  MICROPHONE_NOT_FOUND: {
    title: '마이크를 찾을 수 없어요',
    message: '마이크가 연결되어 있는지 확인해주세요.',
    action: '다시 시도',
  },
  NETWORK_ERROR: {
    title: '연결에 실패했어요',
    message: '인터넷 연결을 확인하고 다시 시도해주세요.',
    action: '다시 시도',
  },
  SESSION_EXPIRED: {
    title: '세션이 만료되었어요',
    message: '페이지를 새로고침하여 다시 시작해주세요.',
    action: '새로고침',
  },
  UNKNOWN_ERROR: {
    title: '오류가 발생했어요',
    message: '잠시 후 다시 시도해주세요.\n문제가 지속되면 관리자에게 문의하세요.',
    action: '다시 시도',
  },
} as const;

// ============================================================================
// 13. Development/Debug Flags
// ============================================================================

export const DEBUG_CONFIG = {
  showNetworkLogs: import.meta.env.DEV, // Show console logs in dev mode
  showAudioLevels: import.meta.env.DEV, // Show audio level numbers
  enableMockMode: false, // Use mock data instead of real API
} as const;
