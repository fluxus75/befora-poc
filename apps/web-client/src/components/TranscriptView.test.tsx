import { render, screen } from '@testing-library/react';

import { TranscriptView } from './TranscriptView';

describe('TranscriptView', () => {
  it('renders transcripts and streaming text', () => {
    render(
      <TranscriptView
        transcripts={[
          {
            id: '1',
            speaker: 'patient',
            text: '머리가 아파요',
            status: 'CONFIRMED',
            timestamp: Date.now(),
          },
          {
            id: '2',
            speaker: 'agent',
            text: '언제부터 아프셨나요?',
            status: 'FINAL',
            timestamp: Date.now(),
          },
        ]}
        currentStreaming="잠시만요"
        agentStreaming="확인해볼게요"
      />
    );

    expect(screen.getByText('머리가 아파요')).toBeInTheDocument();
    expect(screen.getByText('언제부터 아프셨나요?')).toBeInTheDocument();
    expect(screen.getByText('잠시만요...')).toBeInTheDocument();
    expect(screen.getByText('확인해볼게요...')).toBeInTheDocument();
  });
});
