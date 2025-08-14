import sounddevice as sd  #to connect with audio interface
import numpy as np
import matplotlib.pyplot as plt
import scipy.fft as fft


#print(sd.query_devices()) # find audio interface (list available audio devices)

# configure audio interface
speaker = 6 # output index for MAYA44 USB+
mic = 3 # input index for MAYA44 USB+
sd.default.device = (mic, speaker) # set devices globally for sd

# initialize the sweep parameters 
duration = 5 # sweep duration in s
start_freq = 10000 # starting freq in hz
end_freq = 20000
sample_rate = 48000

data = np.zeros((int(sample_rate * duration), 1), dtype='float64')

# generate time array
t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False) 

# generate sweep
f_start = 100
f_end = 20000
# sweep = np.sin(2 * np.pi * 15000 * t) # simple sin wave
# k = np.log(f_end / f_start)     # Logarithmic Chirp
# phase = (2 * np.pi * f_start * duration / k) * (np.exp(k * (t / duration)) - 1)
# sweep = np.sin(phase)
sweep = np.sin(2 * np.pi * (f_start * t + ((f_end - f_start) / (2 * duration)) * (t ** 2))) # Linear Chirp
sweep = sweep / np.max(np.abs(sweep)) # normalize sweep to avoid clipping
sweep = sweep * 0.8

# possibly apply window to reduce impulse noise at start and end
# Apply a Hann window to the sweep signal 
# window = np.hanning(len(sweep))
# sweep = window * sweep

pos = [0]

# Define the callback function 
def callback(indata, outdata, frames, time, status): 
    #print out status messages if there are any
    if status: 
        print(status)

    end = pos[0] + frames # end pos for current chunk

    if end > len(sweep): # check that slice is within sweep bounds
        end = len(sweep)

    outdata[:end - pos[0]] = sweep[pos[0]:end].reshape(-1,1) # slice the sweep data and output

    if end - pos[0] < frames: # if end pos is greater than sweep length, fill the rest with zeros
        outdata[end - pos[0]:] = 0

    pos[0] = end % len(sweep) # update current pos
    data[:frames] = indata[:frames] # record


# play & record sweep
print("start sweep, recording...")

with sd.Stream(channels=1, samplerate=sample_rate, callback=callback): 
     sd.sleep(int(duration * 1000))
print("sweep done, recording done")

# fourier transform recorded signal
fft_data = np.fft.fft(data.flatten()) 
frequencies = np.fft.fftfreq(len(fft_data), 1 / sample_rate)
mag = np.abs(fft_data)
mag = mag / np.max(mag)

# fft output sweep
fft_sweep = np.fft.fft(sweep.flatten())
freq_sweep = np.fft.fftfreq(len(fft_sweep), 1 / sample_rate)
mag_sweep = np.abs(fft_sweep)
mag_sweep = mag_sweep / np.max(mag_sweep)


# stationary figures
# figure + subplots
fig, axs = plt.subplots(2, 1, figsize=(12, 6))
start = start_freq * duration
end = end_freq * duration

# # plot the sweep output fft
#axs[0].plot(t, sweep)
axs[0].plot(freq_sweep[start:end],mag_sweep[start:end])
axs[0].set_title("Speaker Output") 
axs[0].set_xlabel("Frequency [Hz]") 
axs[0].set_ylabel("Magnitude") 
#plt.show()

# Plot the mic input
#axs[1].plot(t, data)
axs[1].plot(frequencies[start:end], mag[start:end])
axs[1].set_title("Mic Input") 
axs[1].set_xlabel("Frequency [Hz]") 
axs[1].set_ylabel("Magnitude") 
plt.tight_layout()
plt.show()


