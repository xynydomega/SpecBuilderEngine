import React, { useEffect, useRef } from 'react';
import WaveSurfer from 'wavesurfer.js';

interface WaveformVisualizerProps {
  displayName: string;
}

export const WaveformVisualizer: React.FC<WaveformVisualizerProps> = ({ displayName }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const wavesurfer = useRef<WaveSurfer | null>(null);

  useEffect(() => {
    if (containerRef.current) {
      wavesurfer.current = WaveSurfer.create({
        container: containerRef.current,
        waveColor: '#4F4A85',
        progressColor: '#383351',
      });
    }
    return () => wavesurfer.current?.destroy();
  }, []);

  return (
    <div className="waveform-container">
      <h3>{displayName}</h3>
      <div ref={containerRef} />
    </div>
  );
};
