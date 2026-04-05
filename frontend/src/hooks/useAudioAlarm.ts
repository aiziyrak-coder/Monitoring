import { useEffect, useRef } from 'react';
import { useStore } from '../store';

export function useAudioAlarm() {
  const patients = useStore(state => state.patients);
  const isAudioMuted = useStore(state => state.isAudioMuted);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const intervalRef = useRef<number | null>(null);

  const hasCritical = Object.values(patients).some(p => p.alarm.level === 'red');

  useEffect(() => {
    if (hasCritical && !isAudioMuted) {
      if (!audioCtxRef.current) {
        audioCtxRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      }

      if (!intervalRef.current) {
        intervalRef.current = window.setInterval(() => {
          if (!audioCtxRef.current) return;
          
          const osc = audioCtxRef.current.createOscillator();
          const gainNode = audioCtxRef.current.createGain();
          
          osc.type = 'sine';
          osc.frequency.setValueAtTime(800, audioCtxRef.current.currentTime);
          osc.frequency.exponentialRampToValueAtTime(1200, audioCtxRef.current.currentTime + 0.1);
          
          gainNode.gain.setValueAtTime(0, audioCtxRef.current.currentTime);
          gainNode.gain.linearRampToValueAtTime(0.5, audioCtxRef.current.currentTime + 0.05);
          gainNode.gain.linearRampToValueAtTime(0, audioCtxRef.current.currentTime + 0.2);
          
          osc.connect(gainNode);
          gainNode.connect(audioCtxRef.current.destination);
          
          osc.start();
          osc.stop(audioCtxRef.current.currentTime + 0.2);
        }, 1000);
      }
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [hasCritical, isAudioMuted]);

  useEffect(() => {
    return () => {
      void audioCtxRef.current?.close();
      audioCtxRef.current = null;
    };
  }, []);
}
