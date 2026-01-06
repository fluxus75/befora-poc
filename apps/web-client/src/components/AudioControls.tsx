import {
  BUTTON_SIZES,
  VOICE_BUTTON_CONFIGS,
} from '../constants/ui';
import type { AudioControlsProps } from '../types/voice';

export function AudioControls({
  state,
  onStart,
  onStop,
  disabled,
}: AudioControlsProps) {
  const config = VOICE_BUTTON_CONFIGS[state];
  const handleClick = () => {
    if (state === 'START') onStart();
    if (state === 'STOP') onStop();
  };

  return (
    <button
      className={`voice-button voice-button-${state.toLowerCase()}`}
      style={{
        backgroundColor: config.backgroundColor,
        width: BUTTON_SIZES.width,
        height: BUTTON_SIZES.height,
        borderRadius: BUTTON_SIZES.borderRadius,
        fontSize: BUTTON_SIZES.fontSize,
      }}
      onClick={handleClick}
      disabled={config.disabled || disabled}
      aria-label={config.ariaLabel}
    >
      <span className={`voice-icon voice-icon-${config.icon}`} />
      <span>{config.text}</span>
    </button>
  );
}
