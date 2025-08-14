import sys
import matplotlib
matplotlib.use('qtagg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.ticker as ticker
import queue
import numpy as np
import sounddevice as sd
import pyqtgraph as pg
import PyQt6 as pq
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtMultimedia import QAudio
from scipy.signal import medfilt, butter, filtfilt
import collections

mic = 1
speaker = 4
sd.default.device = (mic, speaker) # mic, speaker

history_length = 5  # Number of past frames to average
fft_history = collections.deque(maxlen=history_length)

		
class rt_plot(QtWidgets.QMainWindow): # main window
    def __init__(self):
        super().__init__()
        self.threadpool = QtCore.QThreadPool() # creates thread pool to manage threads

        # set up GUI 
        self.box = QtWidgets.QWidget()
        self.box.setMinimumSize(800, 400)  # Set a minimum size for visibility
        self.layout = QtWidgets.QVBoxLayout()
        self.box.setLayout(self.layout)
        self.setCentralWidget(self.box)
        self.canvas = pg.GraphicsLayoutWidget() # graph widget  
        self.layout.addWidget(self.canvas)  # Add canvas to layout

        self.q = queue.Queue(maxsize=20) # for data

        self.device = sd.default.device
        self.window_length = 1000
        self.downsample = 1
        self.channels = [1] # mono stream
        self.interval = 30 # 60 ms per interval
        self.samplerate = 96000
        self.length  = int(self.window_length*self.samplerate/(1000*self.downsample))

        self.sweep = self.generate_sweep(1)

        
        self.plotWidget = self.canvas.addPlot(title='Real-Time Audio Feedback') # set plot        
        self.plotWidget.setLabel("left", "Magnitude (dB)")
        self.plotWidget.setLabel("bottom", "Frequency (Hz)")
        self.plotWidget.showGrid(x=True, y=True)
        self.plotWidget.setYRange(-100, 0) # for decibel range
        self.audio_plot = self.plotWidget.plot(en='g')
        
        self.plotdata = np.zeros((self.length, len(self.channels)))
        print(self.plotdata.shape)
        
        self.update_plot()
        self.timer = QtCore.QTimer()
        self.timer.setInterval(self.interval) # update interval in ms
        self.timer.timeout.connect(self.update_plot) # call whenever time runs out
        self.timer.start()

        self.start_worker()

    def generate_sweep(self, n): # choose sweep equation   
        duration = 1
        f_start = 100
        f_end = 48000
        sample_rate = 96000  
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False) 

        match n:
            case 0:
                sweep = np.sin(2 * np.pi * f_start * t)   # Simple Sine
            case 1:
                sweep = np.sin(2 * np.pi * (f_start * t + ((f_end - f_start) / (2 * duration)) * (t ** 2))) # Linear Chirp
            case 2:
                k = np.log(f_end / f_start)     # Logarithmic Chirp
                phase = (2 * np.pi * f_start * duration / k) * (np.exp(k * (t / duration)) - 1)
                sweep = np.sin(phase)

        sweep = sweep / np.max(np.abs(sweep)) # normalize sweep to avoid clipping
        sweep = sweep * 0.8
        return sweep

    def input_output(self):
        pos = [0]
        try:
            def callback(indata, outdata, frames, time, status):
                end = pos[0] + frames # end pos for current chunk

                if end > len(self.sweep): # check that slice is within sweep bounds
                    end = len(self.sweep)

                outdata[:end - pos[0]] = self.sweep[pos[0]:end].reshape(-1,1) # slice the sweep data and output

                if end - pos[0] < frames: # if end pos is greater than sweep length, fill the rest with zeros
                    outdata[end - pos[0]:] = 0

                pos[0] = end % len(self.sweep) # update current pos

                self.q.put(indata[::self.downsample, 0]) # Put in queue
                
            with sd.Stream(device = self.device, channels = max(self.channels), samplerate=self.samplerate, callback=callback):
                input()
                
        except Exception as e:
            print("ERROR AUDIO: ", e)

        
    def start_worker(self): 
        worker = Worker(self.start_stream, )
        self.threadpool.start(worker)	

    def start_stream(self):
        self.input_output()

    def update_plot(self):
        try:
            data = [0]
            while not self.q.empty():
                data = self.q.get_nowait() # get new data from queue
                fft_data = np.fft.rfft(data.flatten()) 
                frequencies = np.fft.rfftfreq(len(data), 1 / self.samplerate)
                mag = np.abs(fft_data)
                
                fft_history.append(mag)

                # Compute the rolling average
                avg_mag = np.mean(fft_history, axis=0)

                mag_db = 20 * np.log10(avg_mag + 1e-9)
                self.audio_plot.setData(frequencies[:], mag_db[:])


                
        except Exception as e:
            pass
            #print("ERROR 1: ", e)


class Worker(QtCore.QRunnable): # define worker thread
	def __init__(self, function, *args, **kwargs):
		super(Worker, self).__init__()
		self.function = function
		self.args = args
		self.kwargs = kwargs

	@pyqtSlot()
	def run(self):
		self.function(*self.args, **self.kwargs)
          
app = QtWidgets.QApplication(sys.argv)
mainWindow = rt_plot()
mainWindow.show()
sys.exit(app.exec())