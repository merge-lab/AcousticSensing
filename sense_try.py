# This file synthesizes test signals (chirp signals) to be used with sensing equipment

import numpy as np
import matplotlib.pyplot as plt
import scipy.fft as fft
import sounddevice as sd

# Audio device selection
# Run sd.query_devices() to find the correct device numbers
mic = 3
speaker = 6
sd.default.device = (mic, speaker)

# Initializing chirp parameters 
duration = 1            # Chirp length in sec
f_start = 5000     # Freq in Hz
f_end = 20000

# General constants
sample_rate = 48000
start = f_start * duration
end = f_end * duration

# List for time
t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

# Constant sinusoid at f_start Hz (for comparison)
sin = np.sin(2 * np.pi * f_start * t)

# Linear Chirp synthesis
chirp_lin = np.sin(2 * np.pi * (f_start * t + ((f_end - f_start) / (2 * duration)) * (t ** 2)))

# Logarithmic Chirp synthesis
k = np.log(f_end / f_start)
phase = (2 * np.pi * f_start * duration / k) * (np.exp(k * (t / duration)) - 1)
chirp_log = np.sin(phase)

# Plotting
fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True, sharey=True)

for ax, data, title in zip(
    axes,
    [sin,      chirp_lin,    chirp_log],
    ["Sinusoid", "Linear Chirp", "Logarithmic Chirp"]
):
    Pxx, freqs, bins, im = ax.specgram(
        data, NFFT=1024, Fs=sample_rate, noverlap=512
    )
    ax.set_title(f"{title} Spectrogram")
    ax.set_ylabel("Frequency [Hz]")

axes[-1].set_xlabel("Time [s]")

# one colorbar for all 3, tied to the last image
# fig.colorbar(im, ax=axes, label="Intensity [dB]")
plt.tight_layout()
plt.show()

# playing chirp signal
sd.play(sin, samplerate=sample_rate)
sd.wait()