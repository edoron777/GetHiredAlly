export const playStartSound = () => {
  try {
    const ctx = new AudioContext();
    const oscillator = ctx.createOscillator();
    const gain = ctx.createGain();
    oscillator.connect(gain);
    gain.connect(ctx.destination);
    oscillator.frequency.value = 440;
    gain.gain.value = 0.1;
    oscillator.start();
    setTimeout(() => {
      oscillator.stop();
      ctx.close();
    }, 200);
  } catch (e) {
  }
};

export const playCompleteSound = () => {
  try {
    const ctx = new AudioContext();
    const oscillator = ctx.createOscillator();
    const gain = ctx.createGain();
    oscillator.connect(gain);
    gain.connect(ctx.destination);
    oscillator.frequency.value = 880;
    gain.gain.value = 0.1;
    oscillator.start();
    setTimeout(() => {
      oscillator.stop();
      ctx.close();
    }, 300);
  } catch (e) {
  }
};
