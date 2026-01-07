/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly DEV: boolean;
  readonly PROD: boolean;
  readonly MODE: string;
  readonly VITE_API_BASE_URL?: string;
  readonly VITE_REALTIME_PROVIDER?: "openai" | "local" | "mock";
  readonly VITE_HEYGEN_ENABLED?: string;
  readonly VITE_LOCAL_WHISPER_URL?: string;
  readonly VITE_LOCAL_TTS_URL?: string;
  readonly VITE_LOCAL_SAMPLE_RATE?: string;
  readonly VITE_MOCK_SCENARIO?: string;
  readonly VITE_MOCK_LATENCY_MS?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
