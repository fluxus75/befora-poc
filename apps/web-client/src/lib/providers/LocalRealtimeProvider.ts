import { buildApiUrl } from "../api";
import type { NetworkMetrics, TranscriptItem } from "../../types/voice";
import type {
  IRealtimeProvider,
  RealtimeProviderOptions,
} from "./IRealtimeProvider";

const DEFAULT_SAMPLE_RATE = 16000;
const AUDIO_LEVEL_INTERVAL_MS = 300;
const NETWORK_METRICS_INTERVAL_MS = 1000;

type LocalEvent =
  | { type: "vad"; active: boolean }
  | { type: "transcript"; text: string }
  | { type: "error"; message: string }
  | { type: "status"; state: string };

export class LocalRealtimeProvider implements IRealtimeProvider {
  private sessionId: string | null = null;
  private socket: WebSocket | null = null;
  private localStream: MediaStream | null = null;
  private audioContext: AudioContext | null = null;
  private processor: ScriptProcessorNode | null = null;
  private analyser: AnalyserNode | null = null;
  private meterTimer: number | null = null;
  private metricsTimer: number | null = null;
  private manualDisconnect = false;

  constructor(private readonly options: RealtimeProviderOptions) {}

  async connect(sessionId: string): Promise<void> {
    this.sessionId = sessionId;
    this.manualDisconnect = false;
    this.options.onStatusChange("CONNECTING");
    const sampleRate = this.getSampleRate();
    const wsUrl = this.buildWebSocketUrl(
      `/api/local-realtime/ws?session_id=${encodeURIComponent(sessionId)}&sample_rate=${sampleRate}`
    );
    await this.openSocket(wsUrl);
  }

  async reconnect(): Promise<void> {
    if (!this.sessionId) {
      return;
    }
    this.options.onStatusChange("RECONNECTING");
    await this.connect(this.sessionId);
  }

  disconnect(): void {
    this.manualDisconnect = true;
    this.cleanupAudio();
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    this.options.onStatusChange("IDLE");
  }

  async startMic(): Promise<void> {
    await this.ensureSocketReady();
    if (this.localStream) {
      return;
    }
    this.localStream = await navigator.mediaDevices.getUserMedia({
      audio: true,
    });
    const sampleRate = this.getSampleRate();
    this.audioContext = new AudioContext();
    const source = this.audioContext.createMediaStreamSource(this.localStream);
    this.analyser = this.audioContext.createAnalyser();
    this.analyser.fftSize = 512;
    source.connect(this.analyser);

    const processor = this.audioContext.createScriptProcessor(4096, 1, 1);
    const gain = this.audioContext.createGain();
    gain.gain.value = 0;
    processor.onaudioprocess = (event) => {
      const input = event.inputBuffer.getChannelData(0);
      const downsampled = downsampleBuffer(
        input,
        this.audioContext?.sampleRate ?? sampleRate,
        sampleRate
      );
      const pcm = floatTo16BitPCM(downsampled);
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.socket.send(pcm.buffer);
      }
    };
    source.connect(processor);
    processor.connect(gain);
    gain.connect(this.audioContext.destination);
    this.processor = processor;

    this.startAudioMeter();
    this.startMetrics();
  }

  stopMic(): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({ type: "stop" }));
    }
    this.cleanupAudio();
  }

  async speak(text: string): Promise<void> {
    if (!text.trim()) {
      return;
    }
    if ("speechSynthesis" in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = "ko-KR";
      window.speechSynthesis.speak(utterance);
    }
  }

  private async openSocket(url: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const socket = new WebSocket(url);
      socket.onopen = () => {
        this.socket = socket;
        this.options.onStatusChange("CONNECTED");
        this.options.onStatusChange("LISTENING");
        resolve();
      };
      socket.onerror = () => {
        reject(new Error("local_realtime_ws_error"));
      };
      socket.onclose = () => {
        this.socket = null;
        if (!this.manualDisconnect) {
          this.options.onStatusChange("FAILED");
        }
      };
      socket.onmessage = (event) => this.handleMessage(event);
    });
  }

  private async ensureSocketReady(): Promise<void> {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      throw new Error("local_realtime_ws_not_ready");
    }
  }

  private handleMessage(event: MessageEvent): void {
    if (typeof event.data !== "string") {
      return;
    }
    let payload: LocalEvent;
    try {
      payload = JSON.parse(event.data) as LocalEvent;
    } catch (error) {
      this.options.onError(error as Error);
      return;
    }

    switch (payload.type) {
      case "vad":
        this.options.onVadChange(payload.active);
        this.options.onStatusChange(
          payload.active ? "PROCESSING" : "LISTENING"
        );
        return;
      case "transcript":
        this.handleTranscript(payload.text);
        return;
      case "error":
        this.options.onError(new Error(payload.message));
        return;
      case "status":
      default:
        return;
    }
  }

  private handleTranscript(text: string): void {
    const transcript = text.trim();
    if (!transcript) {
      return;
    }
    const item: TranscriptItem = {
      id: crypto.randomUUID(),
      speaker: "patient",
      text: transcript,
      status: "CONFIRMED",
      timestamp: Date.now(),
    };
    this.options.onTranscript(item);
    this.options.onStreaming(null);
    void this.sendToDsl(transcript);
  }

  private async sendToDsl(transcript: string): Promise<void> {
    if (!this.sessionId) {
      return;
    }
    try {
      const response = await fetch(
        buildApiUrl(`/api/sessions/${this.sessionId}/process`),
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
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
      this.options.onStepUpdate(data.current_node, data.emergency);
      await this.speak(data.agent_response);
    } catch (error) {
      this.options.onError(error as Error);
    }
  }

  private startAudioMeter(): void {
    if (!this.analyser) return;
    const buffer = new Float32Array(this.analyser.fftSize);
    this.meterTimer = window.setInterval(() => {
      if (!this.analyser) return;
      this.analyser.getFloatTimeDomainData(buffer);
      let sum = 0;
      for (let i = 0; i < buffer.length; i += 1) {
        const sample = buffer[i] ?? 0;
        sum += sample * sample;
      }
      const rms = Math.sqrt(sum / buffer.length);
      const level = Math.min(100, Math.round(rms * 200));
      this.options.onAudioLevel(level);
    }, AUDIO_LEVEL_INTERVAL_MS);
  }

  private startMetrics(): void {
    this.metricsTimer = window.setInterval(() => {
      this.options.onNetworkMetrics(this.getNetworkMetrics());
    }, NETWORK_METRICS_INTERVAL_MS);
  }

  private getNetworkMetrics(): NetworkMetrics {
    return {
      rttMs: 60,
      jitterMs: 4,
      packetLossPercent: 0,
      quality: "GOOD",
    };
  }

  private cleanupAudio(): void {
    if (this.meterTimer) {
      window.clearInterval(this.meterTimer);
      this.meterTimer = null;
    }
    if (this.metricsTimer) {
      window.clearInterval(this.metricsTimer);
      this.metricsTimer = null;
    }
    if (this.processor) {
      this.processor.disconnect();
      this.processor.onaudioprocess = null;
      this.processor = null;
    }
    if (this.audioContext) {
      void this.audioContext.close();
      this.audioContext = null;
    }
    if (this.localStream) {
      this.localStream.getTracks().forEach((track) => track.stop());
      this.localStream = null;
    }
    this.analyser = null;
  }

  private buildWebSocketUrl(path: string): string {
    const base = import.meta.env.VITE_API_BASE_URL as string | undefined;
    const url = base
      ? new URL(path, base)
      : new URL(path, window.location.origin);
    url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
    return url.toString();
  }

  private getSampleRate(): number {
    const raw = Number(import.meta.env.VITE_LOCAL_SAMPLE_RATE);
    if (Number.isFinite(raw) && raw > 0) {
      return raw;
    }
    return DEFAULT_SAMPLE_RATE;
  }
}

function downsampleBuffer(
  buffer: Float32Array,
  inputSampleRate: number,
  targetSampleRate: number
): Float32Array {
  if (targetSampleRate === inputSampleRate) {
    return buffer;
  }
  const sampleRateRatio = inputSampleRate / targetSampleRate;
  const newLength = Math.round(buffer.length / sampleRateRatio);
  const result = new Float32Array(newLength);
  let offsetResult = 0;
  let offsetBuffer = 0;
  while (offsetResult < result.length) {
    const nextOffsetBuffer = Math.round((offsetResult + 1) * sampleRateRatio);
    let sum = 0;
    let count = 0;
    for (
      let i = offsetBuffer;
      i < nextOffsetBuffer && i < buffer.length;
      i += 1
    ) {
      sum += buffer[i] ?? 0;
      count += 1;
    }
    result[offsetResult] = count > 0 ? sum / count : 0;
    offsetResult += 1;
    offsetBuffer = nextOffsetBuffer;
  }
  return result;
}

function floatTo16BitPCM(input: Float32Array): Int16Array {
  const output = new Int16Array(input.length);
  for (let i = 0; i < input.length; i += 1) {
    const s = Math.max(-1, Math.min(1, input[i] ?? 0));
    output[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
  }
  return output;
}
