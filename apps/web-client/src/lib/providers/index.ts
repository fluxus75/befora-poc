import { MockRealtimeProvider } from './MockRealtimeProvider';
import { LocalRealtimeProvider } from './LocalRealtimeProvider';
import { OpenAIRealtimeProvider } from './OpenAIRealtimeProvider';
import type { IRealtimeProvider, RealtimeProviderOptions } from './IRealtimeProvider';

export function createRealtimeProvider(
  provider: string,
  options: RealtimeProviderOptions
): IRealtimeProvider {
  switch (provider) {
    case 'mock':
      return new MockRealtimeProvider(options);
    case 'local':
      return new LocalRealtimeProvider(options);
    case 'openai':
    default:
      return new OpenAIRealtimeProvider(options);
  }
}

export type { IRealtimeProvider, RealtimeProviderOptions };
