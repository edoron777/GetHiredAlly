/**
 * Scanner Sound Effects - Web Audio API
 * Pleasant, professional sounds for scanning animations
 */

class ScannerSounds {
  private audioContext: AudioContext | null = null;
  private enabled: boolean = true;

  private init(): AudioContext {
    if (!this.audioContext) {
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    }
    return this.audioContext;
  }

  setEnabled(enabled: boolean): void {
    this.enabled = enabled;
  }

  playStartSound(): void {
    if (!this.enabled) return;
    
    try {
      const ctx = this.init();
      const now = ctx.currentTime;

      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.type = 'sine';
      osc.frequency.setValueAtTime(523, now);
      osc.frequency.setValueAtTime(659, now + 0.15);

      gain.gain.setValueAtTime(0, now);
      gain.gain.linearRampToValueAtTime(0.3, now + 0.05);
      gain.gain.linearRampToValueAtTime(0.2, now + 0.15);
      gain.gain.linearRampToValueAtTime(0, now + 0.4);

      osc.start(now);
      osc.stop(now + 0.4);
    } catch (e) {}
  }

  playTickSound(): void {
    if (!this.enabled) return;

    try {
      const ctx = this.init();
      const now = ctx.currentTime;

      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.type = 'sine';
      osc.frequency.setValueAtTime(1000, now);

      gain.gain.setValueAtTime(0.05, now);
      gain.gain.linearRampToValueAtTime(0, now + 0.05);

      osc.start(now);
      osc.stop(now + 0.05);
    } catch (e) {}
  }

  playCompleteSound(): void {
    if (!this.enabled) return;

    try {
      const ctx = this.init();
      const now = ctx.currentTime;

      const osc1 = ctx.createOscillator();
      const gain1 = ctx.createGain();
      osc1.connect(gain1);
      gain1.connect(ctx.destination);
      osc1.type = 'sine';
      osc1.frequency.setValueAtTime(523, now);
      gain1.gain.setValueAtTime(0, now);
      gain1.gain.linearRampToValueAtTime(0.25, now + 0.05);
      gain1.gain.linearRampToValueAtTime(0, now + 0.5);
      osc1.start(now);
      osc1.stop(now + 0.5);

      const osc2 = ctx.createOscillator();
      const gain2 = ctx.createGain();
      osc2.connect(gain2);
      gain2.connect(ctx.destination);
      osc2.type = 'sine';
      osc2.frequency.setValueAtTime(659, now + 0.1);
      gain2.gain.setValueAtTime(0, now + 0.1);
      gain2.gain.linearRampToValueAtTime(0.25, now + 0.15);
      gain2.gain.linearRampToValueAtTime(0, now + 0.6);
      osc2.start(now + 0.1);
      osc2.stop(now + 0.6);

      const osc3 = ctx.createOscillator();
      const gain3 = ctx.createGain();
      osc3.connect(gain3);
      gain3.connect(ctx.destination);
      osc3.type = 'sine';
      osc3.frequency.setValueAtTime(784, now + 0.2);
      gain3.gain.setValueAtTime(0, now + 0.2);
      gain3.gain.linearRampToValueAtTime(0.3, now + 0.25);
      gain3.gain.linearRampToValueAtTime(0, now + 0.8);
      osc3.start(now + 0.2);
      osc3.stop(now + 0.8);
    } catch (e) {}
  }

  playErrorSound(): void {
    if (!this.enabled) return;

    try {
      const ctx = this.init();
      const now = ctx.currentTime;

      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.type = 'sine';
      osc.frequency.setValueAtTime(330, now);
      osc.frequency.setValueAtTime(294, now + 0.15);

      gain.gain.setValueAtTime(0, now);
      gain.gain.linearRampToValueAtTime(0.2, now + 0.05);
      gain.gain.linearRampToValueAtTime(0.15, now + 0.2);
      gain.gain.linearRampToValueAtTime(0, now + 0.4);

      osc.start(now);
      osc.stop(now + 0.4);
    } catch (e) {}
  }
}

const scannerSounds = new ScannerSounds();

export const playStartSound = (): void => scannerSounds.playStartSound();
export const playCompleteSound = (): void => scannerSounds.playCompleteSound();
export const playErrorSound = (): void => scannerSounds.playErrorSound();
export const playTickSound = (): void => scannerSounds.playTickSound();
export const setSoundEnabled = (enabled: boolean): void => scannerSounds.setEnabled(enabled);
