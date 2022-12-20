
import sys
from PyQt5 import QtWidgets, uic
import numpy as np
import matplotlib.pyplot as plt

import trewmac300x_serial as te

import matplotlib
matplotlib.use('Qt5Agg')

qtcreator_file  = "read_trewmac_gui.ui" # Enter file here.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtcreator_file)


class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        
        plt.ion()
        resultgraph, ax= plt.subplots(figsize=(10, 8))

        resultgraph.canvas.manager.window.setGeometry(800, 500, 800, 600)
        
        ax.set_xlabel('x [Arb. units]')
        ax.set_ylabel('y [Arb. units]')
        ax.set_xlim(-20 , 20)
        ax.set_ylim(  0, 400)
        ax.set_title('Test plot')
        x0 = np.linspace(0,10,100)
        y0 = np.linspace(0,10,100)
        graph, =ax.plot(x0,y0)
        resultgraph.show()
        
        self.graph=graph
        self.resultgraph = resultgraph               

        self.fmin_SpinBox.valueChanged.connect(self.set_frequency_range)
        self.fmax_SpinBox.valueChanged.connect(self.set_frequency_range)
        self.np_SpinBox.valueChanged.connect(self.set_frequency_range)
        self.average_SpinBox.valueChanged.connect(self.set_average)
        self.output_SpinBox.valueChanged.connect(self.set_output)
        self.z0_SpinBox.valueChanged.connect(self.set_z0)

        self.close_button.clicked.connect(self.CloseApp)
        
        self.analyser  = te.te300x(port='COM7')
        ver = self.analyser.read_version()
        message = f'Version = {ver}'
        self.graph_data.setText(message)    

    def CloseApp(self):
        plt.close(self.resultgraph)
        ok = self.analyser.close()
        self.close()
        
    #%% Read and set measurement parameters
    def set_frequency_range( self ):
        fmin = self.fmin_SpinBox.value()
        fmax = self.fmax_SpinBox.value()
        np   = self.np_SpinBox.value()
        frange_ok = self.analyser.set_frequencyrange( fmin, fmax, np )
        message = f'fmin = {fmin:.2f} MHz \n fmax = {fmax:.2f} MHz \n np = {np:4d} '
        self.graph_data.setText(message)    
        
    def set_output( self ):
        output = self.output_SpinBox.value()
        output = self.analyser.set_output ( output )
        message = f'Output = {output:.0f} %'
        self.graph_data.setText(message)    
        
    def set_average( self ):
        average = self.average_SpinBox.value()
        average = self.analyser.set_averaging ( average )
        message = f'average = {average:3d}'
        self.graph_data.setText(message)        
        
    def set_z0( self ):
        z0 = self.z0_SpinBox.value()
        z0 = self.analyser.set_z0 ( z0 )
        message = f'Z0 = {z0:.1f} Ohm'
        self.graph_data.setText(message)    
        
    #%%     
    def UpdateValues(self):
        self.end.setValue(self.end_slider.value())
        self.start.setValue(self.start_slider.value())
        self.PlotGraph()
            
    def PlotGraph(self):        
        N    = 100
        start = (self.start.value())
        end   = (self.end.value())
        
        x= np.linspace(start,end,N)
        y= x**2
        graph_string= f"Start ={start} \n End ={end}"
        self.graph_data.setText(graph_string)
        
        self.graph.set_xdata(x)
        self.graph.set_ydata(y)
        self.resultgraph.canvas.draw()
        self.resultgraph.canvas.flush_events()

        
    def DisplayResult(self):
        def __init__(self):
            resultgraph, ax= plt.subplots()
            ax.set_xlabel('x [Arb. units]')
            ax.set_ylabel('y [Arb. units]')
            ax.set_title('Test plot')
            ax.plt.show()
            
            self.ax=ax
            

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
