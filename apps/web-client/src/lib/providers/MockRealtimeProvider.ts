import { buildApiUrl } from "../api";
import type { NetworkMetrics, TranscriptItem } from "../../types/voice";
import type {
  IRealtimeProvider,
  RealtimeProviderOptions,
} from "./IRealtimeProvider";
import type { MockScenarioPayload, MockScenarioStep } from "./types";

const DEFAULT_LATENCY_MS = 500;
const STREAM_CHUNK_DELAY_MS = 120;
const AGENT_STREAM_DELAY_MS = 120;
const AUDIO_LEVEL_INTERVAL_MS = 300;
const NETWORK_METRICS_INTERVAL_MS = 1000;

type TimerEntry = {
  id: number;
  resolve: () => void;
};

export class MockRealtimeProvider implements IRealtimeProvider {
  private sessionId: string | null = null;
  private scenario: MockScenarioStep[] = [];
  private currentStepIndex = 0;
  private cancelled = false;
  private isPlaying = false;
  private timers = new Set<TimerEntry>();
  private intervalIds: number[] = [];

  constructor(private readonly options: RealtimeProviderOptions) {}

  async connect(sessionId: string): Promise<void> {
    this.sessionId = sessionId;
    this.cancelled = false;
    this.currentStepIndex = 0;
    try {
      this.scenario = await this.loadScenario();
      this.options.onStatusChange("CONNECTING");
      await this.delay(250);
      this.options.onStatusChange("CONNECTED");
      await this.delay(200);
      this.options.onStatusChange("LISTENING");
      this.startIntervals();
    } catch (error) {
      this.options.onError(error as Error);
      this.options.onStatusChange("FAILED");
    }
  }

  async reconnect(): Promise<void> {
    if (!this.sessionId) {
      return;
    }
    this.options.onStatusChange("RECONNECTING");
    await this.connect(this.sessionId);
  }

  disconnect(): void {
    this.cancelled = true;
    this.clearTimers();
    this.stopIntervals();
    this.options.onStatusChange("IDLE");
  }

  async startMic(): Promise<void> {
    if (this.isPlaying) {
      return;
    }
    this.isPlaying = true;
    while (!this.cancelled && this.currentStepIndex < this.scenario.length) {
      const step = this.scenario[this.currentStepIndex];
      if (step) {
        await this.playStep(step);
      }
      this.currentStepIndex += 1;
    }
    this.isPlaying = false;
  }

  stopMic(): void {
    this.cancelled = true;
    this.clearTimers();
    this.options.onVadChange(false);
    this.options.onStreaming(null);
    this.options.onStatusChange("LISTENING");
  }

  async speak(text: string): Promise<void> {
    if (!text.trim()) {
      return;
    }
    const words = text.split(/\s+/).filter(Boolean);
    let buffer = "";
    for (const word of words) {
      if (this.cancelled) {
        return;
      }
      buffer = `${buffer}${word} `;
      this.options.onAgentStreaming(buffer.trim());
      await this.delay(AGENT_STREAM_DELAY_MS);
    }

    const item: TranscriptItem = {
      id: crypto.randomUUID(),
      speaker: "agent",
      text,
      status: "FINAL",
      timestamp: Date.now(),
    };
    this.options.onAgentTranscript(item);
    this.options.onAgentStreaming(null);

    if ("speechSynthesis" in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = "ko-KR";
      window.speechSynthesis.speak(utterance);
    }
  }

  private async loadScenario(): Promise<MockScenarioStep[]> {
    const response = await fetch(buildApiUrl("/api/mock-scenarios"));
    if (!response.ok) {
      throw new Error(`Mock scenario load failed (${response.status})`);
    }
    const payload = (await response.json()) as MockScenarioPayload;
    const scenarioName =
      (import.meta.env.VITE_MOCK_SCENARIO as string | undefined) ??
      "normal_flow";
    return (
      payload.scenarios[scenarioName] ?? payload.scenarios.normal_flow ?? []
    );
  }

  private async playStep(step: MockScenarioStep): Promise<void> {
    if (this.cancelled) {
      return;
    }
    if (step.trigger_error) {
      this.options.onError(new Error(step.trigger_error));
      this.options.onStatusChange("FAILED");
      this.cancelled = true;
      return;
    }

    await this.delay(step.delay_ms ?? this.getDefaultLatencyMs());
    if (this.cancelled) {
      return;
    }
    this.options.onVadChange(true);
    this.options.onStatusChange("PROCESSING");

    if (step.streaming_chunks?.length) {
      for (const chunk of step.streaming_chunks) {
        if (this.cancelled) {
          return;
        }
        this.options.onStreaming(chunk);
        await this.delay(STREAM_CHUNK_DELAY_MS);
      }
    }

    if (step.vad_duration_ms) {
      await this.delay(step.vad_duration_ms);
    } else {
      await this.delay(200);
    }

    const transcript = (step.user_input ?? "").trim();
    if (transcript) {
      const item: TranscriptItem = {
        id: crypto.randomUUID(),
        speaker: "patient",
        text: transcript,
        status: "CONFIRMED",
        timestamp: Date.now(),
      };
      this.options.onTranscript(item);
      this.options.onStreaming(null);
      await this.sendToDsl(transcript);
    } else {
      this.options.onStreaming(null);
    }

    this.options.onVadChange(false);
    this.options.onStatusChange("LISTENING");
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

  private startIntervals(): void {
    this.intervalIds.push(
      window.setInterval(() => {
        const level = Math.round(10 + Math.random() * 40);
        this.options.onAudioLevel(level);
      }, AUDIO_LEVEL_INTERVAL_MS)
    );
    this.intervalIds.push(
      window.setInterval(() => {
        this.options.onNetworkMetrics(this.getNetworkMetrics());
      }, NETWORK_METRICS_INTERVAL_MS)
    );
  }

  private stopIntervals(): void {
    this.intervalIds.forEach((id) => window.clearInterval(id));
    this.intervalIds = [];
  }

  private getNetworkMetrics(): NetworkMetrics {
    return {
      rttMs: 80,
      jitterMs: 5,
      packetLossPercent: 0,
      quality: "GOOD",
    };
  }

  private getDefaultLatencyMs(): number {
    const raw = Number(import.meta.env.VITE_MOCK_LATENCY_MS);
    if (Number.isFinite(raw) && raw >= 0) {
      return raw;
    }
    return DEFAULT_LATENCY_MS;
  }

  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => {
      const entry: TimerEntry = { id: 0, resolve };
      entry.id = window.setTimeout(() => {
        this.timers.delete(entry);
        resolve();
      }, ms);
      this.timers.add(entry);
    });
  }

  private clearTimers(): void {
    this.timers.forEach((entry) => {
      window.clearTimeout(entry.id);
      entry.resolve();
    });
    this.timers.clear();
  }
}
