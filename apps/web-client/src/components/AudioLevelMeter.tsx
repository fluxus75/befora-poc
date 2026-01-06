import {
  AUDIO_METER_CONFIG,
  getAudioLevelColor,
} from '../constants/ui';
import type { AudioLevelMeterProps } from '../types/voice';

export function AudioLevelMeter({ level, className }: AudioLevelMeterProps) {
  const color = getAudioLevelColor(level);

  return (
    <div className={`audio-meter ${className ?? ''}`}>
      <div
        className="audio-meter-bar"
        style={{
          width: `${level}%`,
          backgroundColor: color,
          height: AUDIO_METER_CONFIG.height,
          borderRadius: AUDIO_METER_CONFIG.borderRadius,
        }}
      />
    </div>
  );
}
