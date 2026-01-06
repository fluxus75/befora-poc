import {
  AUDIO_METER_CONFIG,
  DEBUG_CONFIG,
  RECONNECT_CONFIG,
  WEBRTC_AUDIO_CONFIG,
} from '../constants/ui';
import { buildApiUrl } from './api';
import type {
  NetworkMetrics,
  NetworkStatus,
  RealtimeEvent,
  TranscriptItem,
} from '../types/voice';
import type { RealtimeProviderOptions } from './providers/types';

const OPENAI_WEBRTC_ENDPOINT = 'https://api.openai.com/v1/realtime/calls';
const OPENAI_BETA_HEADER = 'realtime=v1';

const DEFAULT_ICE_SERVERS: RTCIceServer[] = [
  { urls: 'stun:stun.l.google.com:19302' },
];

export class RealtimeClient {
  private sessionId: string | null = null;
  private peerConnection: RTCPeerConnection | null = null;
  private dataChannel: RTCDataChannel | null = null;
  private localStream: MediaStream | null = null;
  private remoteAudio: HTMLAudioElement | null = null;
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private meterTimer: number | null = null;
  private statsTimer: number | null = null;
  private reconnectTimer: number | null = null;
  private reconnectAttempts = 0;
  private manualDisconnect = false;

  private readonly onStatusChange: (status: NetworkStatus) => void;
  private readonly onError: (error: Error) => void;
  private readonly onTranscript: (item: TranscriptItem) => void;
  private readonly onStreaming: (text: string | null) => void;
  private readonly onAgentStreaming: (text: string | null) => void;
  private readonly onAgentTranscript: (item: TranscriptItem) => void;
  private readonly onAudioLevel: (level: number) => void;
  private readonly onVadChange: (active: boolean) => void;
  private readonly onNetworkMetrics: (metrics: NetworkMetrics) => void;
  private readonly onStepUpdate: (currentStep: string, emergency: boolean) => void;
  private agentTextBuffer = '';

  constructor(options: RealtimeProviderOptions) {
    this.onStatusChange = options.onStatusChange;
    this.onError = options.onError;
    this.onTranscript = options.onTranscript;
    this.onStreaming = options.onStreaming;
    this.onAgentStreaming = options.onAgentStreaming;
    this.onAgentTranscript = options.onAgentTranscript;
    this.onAudioLevel = options.onAudioLevel;
    this.onVadChange = options.onVadChange;
    this.onNetworkMetrics = options.onNetworkMetrics;
    this.onStepUpdate = options.onStepUpdate;
  }

  async connect(sessionId: string): Promise<void> {
    this.sessionId = sessionId;
    this.manualDisconnect = false;
    this.reconnectAttempts = 0;
    await this.startConnection();
  }

  async reconnect(): Promise<void> {
    if (!this.sessionId) {
      return;
    }
    if (this.reconnectAttempts >= RECONNECT_CONFIG.maxRetries) {
      this.onStatusChange('FAILED');
      return;
    }
    this.onStatusChange('RECONNECTING');
    const delay = Math.min(
      RECONNECT_CONFIG.baseDelay *
        Math.pow(RECONNECT_CONFIG.backoffMultiplier, this.reconnectAttempts),
      RECONNECT_CONFIG.maxDelay
    );
    this.reconnectAttempts += 1;
    await new Promise((resolve) => {
      this.reconnectTimer = window.setTimeout(resolve, delay);
    });
    await this.startConnection();
  }

  disconnect(): void {
    this.manualDisconnect = true;
    this.cleanup();
    this.onStatusChange('IDLE');
  }

  async speak(text: string): Promise<void> {
    if (!text.trim()) {
      return;
    }
    if (!this.dataChannel || this.dataChannel.readyState !== 'open') {
      this.fallbackSpeak(text);
      return;
    }
    this.agentTextBuffer = '';
    this.onAgentStreaming(null);
    const instruction = `다음 문장을 한국어로 그대로 읽어주세요: ${text}`;
    this.sendEvent({
      type: 'response.create',
      response: {
        modalities: ['audio', 'text'],
        instructions: instruction,
      },
    });
  }

  private async startConnection(): Promise<void> {
    try {
      this.cleanupConnection();
      this.onStatusChange('CONNECTING');
      this.localStream = await navigator.mediaDevices.getUserMedia({
        audio: WEBRTC_AUDIO_CONFIG,
      });

      const peerConnection = new RTCPeerConnection({
        iceServers: DEFAULT_ICE_SERVERS,
        bundlePolicy: 'max-bundle',
        rtcpMuxPolicy: 'require',
        iceCandidatePoolSize: 2,
      });
      this.peerConnection = peerConnection;

      const [track] = this.localStream.getAudioTracks();
      peerConnection.addTrack(track, this.localStream);

      this.dataChannel = peerConnection.createDataChannel('oai-events');
      this.dataChannel.onmessage = (event) => this.handleDataMessage(event.data);
      this.dataChannel.onopen = () => {
        this.onStatusChange('LISTENING');
        this.sendSessionUpdate();
      };

      peerConnection.ontrack = (event) => {
        const [remoteStream] = event.streams;
        if (!remoteStream) return;
        this.remoteAudio = new Audio();
        this.remoteAudio.srcObject = remoteStream;
        this.remoteAudio.autoplay = true;
        this.remoteAudio.playsInline = true;
        void this.remoteAudio.play().catch(() => undefined);
      };

      peerConnection.onconnectionstatechange = () => {
        const state = peerConnection.connectionState;
        if (DEBUG_CONFIG.showNetworkLogs) {
          console.info('[realtime] connection state', state);
        }
        if (state === 'connected') {
          this.onStatusChange('CONNECTED');
        }
        if (state === 'failed' || state === 'disconnected') {
          void this.handleDisconnect();
        }
      };

      peerConnection.oniceconnectionstatechange = () => {
        const state = peerConnection.iceConnectionState;
        if (DEBUG_CONFIG.showNetworkLogs) {
          console.info('[realtime] ice state', state);
        }
        if (state === 'failed' || state === 'disconnected') {
          void this.handleDisconnect();
        }
      };

      const offer = await peerConnection.createOffer({
        offerToReceiveAudio: true,
      });
      await peerConnection.setLocalDescription(offer);

      const token = await this.fetchEphemeralToken();
      const response = await fetch(OPENAI_WEBRTC_ENDPOINT, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/sdp',
          'OpenAI-Beta': OPENAI_BETA_HEADER,
        },
        body: offer.sdp ?? '',
      });
      if (!response.ok) {
        throw new Error(`WebRTC 연결 실패 (${response.status})`);
      }
      const answerSdp = await response.text();
      await peerConnection.setRemoteDescription({
        type: 'answer',
        sdp: answerSdp,
      });

      this.startAudioMeter();
      this.startStatsMonitor();
    } catch (error) {
      this.onError(error as Error);
      void this.handleDisconnect();
    }
  }

  private async handleDisconnect(): Promise<void> {
    if (this.manualDisconnect) {
      return;
    }
    this.cleanupConnection();
    await this.reconnect();
  }

  private cleanup(): void {
    this.cleanupConnection();
    this.sessionId = null;
    this.reconnectAttempts = 0;
  }

  private cleanupConnection(): void {
    if (this.reconnectTimer) {
      window.clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.meterTimer) {
      window.clearInterval(this.meterTimer);
      this.meterTimer = null;
    }
    if (this.statsTimer) {
      window.clearInterval(this.statsTimer);
      this.statsTimer = null;
    }
    if (this.dataChannel) {
      this.dataChannel.close();
      this.dataChannel = null;
    }
    if (this.peerConnection) {
      this.peerConnection.close();
      this.peerConnection = null;
    }
    if (this.localStream) {
      this.localStream.getTracks().forEach((track) => track.stop());
      this.localStream = null;
    }
    if (this.audioContext) {
      void this.audioContext.close();
      this.audioContext = null;
      this.analyser = null;
    }
    if (this.remoteAudio) {
      this.remoteAudio.srcObject = null;
      this.remoteAudio = null;
    }
  }

  private async fetchEphemeralToken(): Promise<string> {
    if (!this.sessionId) {
      throw new Error('세션 ID가 없습니다');
    }
    const response = await fetch(buildApiUrl('/api/realtime/token'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: this.sessionId }),
    });
    if (!response.ok) {
      throw new Error(`토큰 발급 실패 (${response.status})`);
    }
    const data = (await response.json()) as { token: string };
    return data.token;
  }

  private handleDataMessage(raw: string): void {
    let event: RealtimeEvent;
    try {
      event = JSON.parse(raw) as RealtimeEvent;
    } catch (error) {
      if (DEBUG_CONFIG.showNetworkLogs) {
        console.warn('[realtime] invalid event', raw);
      }
      return;
    }

    if (DEBUG_CONFIG.showNetworkLogs) {
      console.info('[realtime] event', event.type);
    }

    if (this.isAgentTextDelta(event)) {
      this.appendAgentText(event.delta);
      return;
    }

    if (this.isAgentTextDone(event)) {
      this.commitAgentText(event);
      return;
    }

    switch (event.type) {
      case 'input_audio_buffer.speech_started':
        this.onVadChange(true);
        this.onStatusChange('PROCESSING');
        return;
      case 'input_audio_buffer.speech_stopped':
        this.onVadChange(false);
        this.onStatusChange('LISTENING');
        return;
      default:
        break;
    }

    if (this.isTranscriptDelta(event)) {
      this.onStreaming(event.delta);
      return;
    }

    if (this.isTranscriptCompleted(event)) {
      const transcript = event.transcript.trim();
      if (!transcript) {
        return;
      }
      const item: TranscriptItem = {
        id: crypto.randomUUID(),
        speaker: 'patient',
        text: transcript,
        status: 'CONFIRMED',
        timestamp: Date.now(),
      };
      this.onTranscript(item);
      this.onStreaming(null);
      void this.sendTranscriptToDsl(transcript);
    }
  }

  private isTranscriptDelta(
    event: RealtimeEvent
  ): event is RealtimeEvent & { delta: string } {
    if (typeof event.delta !== 'string') {
      return false;
    }
    return event.type.includes('transcription.delta');
  }

  private isTranscriptCompleted(
    event: RealtimeEvent
  ): event is RealtimeEvent & { transcript: string } {
    if (typeof event.transcript !== 'string') {
      return false;
    }
    return event.type.includes('transcription.completed');
  }

  private isAgentTextDelta(
    event: RealtimeEvent
  ): event is RealtimeEvent & { delta: string } {
    if (typeof event.delta !== 'string') {
      return false;
    }
    return (
      event.type.includes('response.text.delta') ||
      event.type.includes('response.output_text.delta')
    );
  }

  private isAgentTextDone(
    event: RealtimeEvent
  ): event is RealtimeEvent & { text?: string; output_text?: string } {
    return (
      event.type.includes('response.text.done') ||
      event.type.includes('response.output_text.done')
    );
  }

  private appendAgentText(delta: string): void {
    this.agentTextBuffer += delta;
    this.onAgentStreaming(this.agentTextBuffer);
  }

  private commitAgentText(
    event: RealtimeEvent & { text?: string; output_text?: string }
  ): void {
    const finalText =
      (typeof event.text === 'string' && event.text.trim()) ||
      (typeof event.output_text === 'string' && event.output_text.trim()) ||
      this.agentTextBuffer.trim();
    if (!finalText) {
      this.onAgentStreaming(null);
      return;
    }
    const item: TranscriptItem = {
      id: crypto.randomUUID(),
      speaker: 'agent',
      text: finalText,
      status: 'FINAL',
      timestamp: Date.now(),
    };
    this.onAgentTranscript(item);
    this.onAgentStreaming(null);
    this.agentTextBuffer = '';
  }

  private async sendTranscriptToDsl(transcript: string): Promise<void> {
    if (!this.sessionId) {
      return;
    }
    try {
      const response = await fetch(
        buildApiUrl(`/api/sessions/${this.sessionId}/process`),
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_input: transcript }),
        }
      );
      if (!response.ok) {
        throw new Error(`DSL 처리 실패 (${response.status})`);
      }
      const data = (await response.json()) as {
        agent_response: string;
        emergency: boolean;
        current_node: string;
      };
      this.onStepUpdate(data.current_node, data.emergency);
      await this.speak(data.agent_response);
    } catch (error) {
      this.onError(error as Error);
    }
  }

  private startAudioMeter(): void {
    if (!this.localStream) return;
    this.audioContext = new AudioContext();
    const source = this.audioContext.createMediaStreamSource(this.localStream);
    this.analyser = this.audioContext.createAnalyser();
    this.analyser.fftSize = 512;
    source.connect(this.analyser);

    const buffer = new Float32Array(this.analyser.fftSize);
    this.meterTimer = window.setInterval(() => {
      if (!this.analyser) return;
      this.analyser.getFloatTimeDomainData(buffer);
      let sum = 0;
      for (let i = 0; i < buffer.length; i += 1) {
        sum += buffer[i] * buffer[i];
      }
      const rms = Math.sqrt(sum / buffer.length);
      const level = Math.min(100, Math.round(rms * 200));
      this.onAudioLevel(level);
    }, AUDIO_METER_CONFIG.updateInterval);
  }

  private startStatsMonitor(): void {
    if (!this.peerConnection) return;
    this.statsTimer = window.setInterval(async () => {
      if (!this.peerConnection) return;
      const stats = await this.peerConnection.getStats();
      const metrics = extractNetworkMetrics(stats);
      this.onNetworkMetrics(metrics);
    }, 1000);
  }

  private sendEvent(payload: Record<string, unknown>): void {
    if (!this.dataChannel || this.dataChannel.readyState !== 'open') {
      return;
    }
    this.dataChannel.send(JSON.stringify(payload));
  }

  private sendSessionUpdate(): void {
    this.sendEvent({
      type: 'session.update',
      session: {
        modalities: ['audio', 'text'],
        input_audio_transcription: { model: 'whisper-1' },
        turn_detection: { type: 'server_vad' },
      },
    });
  }

  private fallbackSpeak(text: string): void {
    if (!('speechSynthesis' in window)) {
      return;
    }
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'ko-KR';
    window.speechSynthesis.speak(utterance);
  }
}

function extractNetworkMetrics(stats: RTCStatsReport): NetworkMetrics {
  let rttMs: number | null = null;
  let jitterMs: number | null = null;
  let packetLossPercent: number | null = null;

  stats.forEach((report) => {
    if (report.type === 'candidate-pair' && report.state === 'succeeded') {
      const currentRtt = report.currentRoundTripTime as number | undefined;
      if (typeof currentRtt === 'number') {
        rttMs = Math.round(currentRtt * 1000);
      }
    }
    if (report.type === 'inbound-rtp' && report.kind === 'audio') {
      const jitter = report.jitter as number | undefined;
      if (typeof jitter === 'number') {
        jitterMs = Math.round(jitter * 1000);
      }
      const packetsLost = report.packetsLost as number | undefined;
      const packetsReceived = report.packetsReceived as number | undefined;
      if (
        typeof packetsLost === 'number' &&
        typeof packetsReceived === 'number' &&
        packetsReceived > 0
      ) {
        packetLossPercent = Math.round(
          (packetsLost / (packetsLost + packetsReceived)) * 100
        );
      }
    }
  });

  const quality = classifyQuality(rttMs, packetLossPercent);
  return { rttMs, jitterMs, packetLossPercent, quality };
}

function classifyQuality(
  rttMs: number | null,
  packetLoss: number | null
): NetworkMetrics['quality'] {
  if (rttMs === null && packetLoss === null) {
    return 'UNKNOWN';
  }
  if (packetLoss !== null && packetLoss > 5) {
    return 'POOR';
  }
  if (rttMs !== null && rttMs > 300) {
    return 'POOR';
  }
  if (rttMs !== null && rttMs > 180) {
    return 'FAIR';
  }
  return 'GOOD';
}
