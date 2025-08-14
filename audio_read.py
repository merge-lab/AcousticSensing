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


sd.default.device = (1)
		
class rt_plot(QtWidgets.QMainWindow): # main window
    def __init__(self):
        super().__init__()
        self.threadpool = QtCore.QThreadPool() # creates thread pool to manage threads

        # set up GUI 
        self.box = QtWidgets.QWidget()
        self.box.setMinimumSize(600, 400)  # Set a minimum size for visibility
        self.layout = QtWidgets.QVBoxLayout()
        self.box.setLayout(self.layout)
        self.setCentralWidget(self.box)
        self.canvas = pg.GraphicsLayoutWidget() # graph widget  
        self.layout.addWidget(self.canvas)  # Add canvas to layout

        self.q = queue.Queue(maxsize=20) # for threads

        self.device = sd.default.device[0]
        self.window_length = 1000
        self.downsample = 5
        self.channels = [1] # mono stream
        self.interval = 30 
        self.samplerate = 48000
        self.length  = int(self.window_length*self.samplerate/(1000*self.downsample))
        
        self.plotWidget = self.canvas.addPlot(title='Real-Time Audio Feedback') # set plot        
        self.plotWidget.setLabel("left", "Amplitude")
        self.plotWidget.setLabel("bottom", "Time")
        self.plotWidget.showGrid(x=True, y=True)
        self.plotWidget.setYRange(-1, 1)
        self.audio_plot = self.plotWidget.plot(pen='g')
        
        #self.plotdata = [0]*self.length
        self.plotdata = np.zeros((self.length, len(self.channels)))
        print(self.plotdata.shape)
        
        self.update_plot()
        self.timer = QtCore.QTimer()
        self.timer.setInterval(self.interval) # update interval in ms
        self.timer.timeout.connect(self.update_plot) # call whenever time runs out
        self.timer.start()

        self.start_worker()

    def getAudio(self):
        try:
            def audio_callback(indata, frames, time, status):
                self.q.put(indata[::self.downsample, 0])  # Put in queue
            stream  = sd.InputStream(device = self.device, channels = max(self.channels), samplerate=self.samplerate, callback=audio_callback)
            with stream:
                input()
        except Exception as e:
            print("ERROR: ", e)
            

    def start_worker(self): 
        worker = Worker(self.start_stream, )
        self.threadpool.start(worker)	

    def start_stream(self):
        self.getAudio()

    def update_plot(self):
        try:
            data = [0]
            while not self.q.empty():
                data = self.q.get_nowait() # get new data from queue
          
                shift = len(data)
                #print(data.shape)
                self.plotdata = np.roll(self.plotdata, -shift, axis = 0) # shifts data left to remove old data    
                self.plotdata[-shift:, 0] = data # add the new data to end of plotdata
                print(self.plotdata[:, 0])
                self.audio_plot.setData(self.plotdata[:, 0]) # plot to graph
                #self.plotWidget.plot(self.plotdata[:, 0], pen='g') # plot to graph
                
        except Exception as e:
            #pass
            print("ERROR 1: ", e)


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
          

          
        

        


