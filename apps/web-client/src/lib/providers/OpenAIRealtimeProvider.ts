import { RealtimeClient } from '../realtime';
import type { IRealtimeProvider, RealtimeProviderOptions } from './IRealtimeProvider';

export class OpenAIRealtimeProvider
  extends RealtimeClient
  implements IRealtimeProvider
{
  constructor(options: RealtimeProviderOptions) {
    super(options);
  }

  async startMic(): Promise<void> {
    return Promise.resolve();
  }

  stopMic(): void {
    return undefined;
  }
}
