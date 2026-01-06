import type { RealtimeProviderOptions } from './types';

export interface IRealtimeProvider {
  connect(sessionId: string): Promise<void>;
  reconnect(): Promise<void>;
  disconnect(): void;
  startMic(): Promise<void>;
  stopMic(): void;
  speak(text: string): Promise<void>;
}

export type { RealtimeProviderOptions };
