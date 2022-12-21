# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 22:20:43 2022

@author: larsh

Contol and read data from Trewmax TE300x impedance analyser
Using serial interface libraries in 'trewmac300x_serial.py'

GUI interface made in Qt Designer, ver. 5

Sets up a GUI to control the system
Communicates using an emulated  COM-port on the computer, default COM7
Reads, plots and saves a complex impedance spectrum (f,Z).
Results are read and saved as frequency, abs(Z) and arg(Z), where Z(f) is complex impedance
"""


#%% Libraries
import sys
from PyQt5 import QtWidgets, uic
import numpy as np
import matplotlib.pyplot as plt

import trewmac300x_serial as te

import matplotlib

#%% Set up GUI in from Qt5
matplotlib.use('Qt5Agg')
qtcreator_file  = "read_trewmac_gui.ui" # Enter file here.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtcreator_file)

#%% Class and defs
class read_analyser(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        
        # Initialise result graph
        plt.ion()
        fig, axs = plt.subplots( nrows=2, ncols=1, figsize=(8, 12) )

        fig.canvas.manager.window.setGeometry(800, 500, 800, 600)
        
        x0 = []
        y0 = x0
        for k in range(0,2):
            axs[k].set_xlabel('Frequency [MHz]')
            axs[k].set_xlim(0 , 20)   
            axs[k].grid( True )   
            
        graphs=[]
        line, = axs[0].semilogy(x0,y0)
        graphs.append(line)
        line, = axs[1].plot(x0,y0)
        graphs.append(line)

        axs[0].set_ylabel('|Z| [Ohm]')
        axs[1].set_ylabel('arg(Z) [Deg]')
        
        axs[0].set_ylim( 1e-1, 1e6 )
        axs[1].set_ylim( -90, 90 )

        fig.show()
        
        self.graph= graphs
        self.axs  = axs
        self.fig  = fig               

        # Connect GUI elements
        self.fmin_SpinBox.valueChanged.connect( self.set_frequency_range )
        self.fmax_SpinBox.valueChanged.connect( self.set_frequency_range )
        self.np_SpinBox.valueChanged.connect( self.set_frequency_range )
        self.average_SpinBox.valueChanged.connect( self.set_average )
        self.output_SpinBox.valueChanged.connect( self.set_output )
        self.fscalemin_SpinBox.valueChanged.connect( self.set_f_scale )
        self.fscalemax_SpinBox.valueChanged.connect( self.set_f_scale )       
        self.Zscalemin_comboBox.activated.connect( self.set_Z_scale )
        self.Zscalemax_comboBox.activated.connect( self.set_Z_scale )

        self.z0_SpinBox.valueChanged.connect(self.set_z0)
        
        self.acquire_button.clicked.connect( self.acquire_trace )
        self.close_button.clicked.connect( self.CloseApp ) 
        
        # Open intrument
        self.analyser  = te.te300x(port='COM7')
        ver = self.analyser.read_version()
        self.update_status( f'Device connected.\nVersion {ver}\n', append=False )
        
    def CloseApp(self):
        plt.close(self.fig)
        ok = self.analyser.close()
        self.close()        
        
    def update_status( self, message, append = False ):
        if append:
            old_message = self.status_textEdit.toPlainText()
            message += old_message
        self.status_textEdit.setText(message)            
        
    #%% Read and set measurement parameters
    def set_frequency_range( self ):
        fmin = self.fmin_SpinBox.value()
        fmax = self.fmax_SpinBox.value()
        np   = self.np_SpinBox.value()
        frange_ok = self.analyser.set_frequencyrange( fmin*1e6, fmax*1e6, np )
        message = f'frange = {fmin:.2f} ... {fmax:.2f} MHz, {np:4d} pts.\n'
        self.update_status( message, append=True )    
        
    def set_output( self ):
        output = self.output_SpinBox.value()
        output = self.analyser.set_output ( output )
        self.update_status( f'Output = {output:.0f} %\n', append=True )
        
    def set_average( self ):
        average = self.average_SpinBox.value()
        average = self.analyser.set_averaging ( average )
        self.update_status( f'average = {average:3d}\n', append=True )
        
    def set_z0( self ):
        z0 = self.z0_SpinBox.value()
        z0 = self.analyser.set_z0 ( z0 )
        self.update_status( f'Z0 = {z0:.1f} Ohm\n', append=True )

    def acquire_trace( self ):
        self.update_status( 'Reading data from analyser ... \n', append=True )
        self.analyser.read_sweep()
        f   = self.analyser.res.f
        Zmag= self.analyser.res.Zmag
        
        self.update_status( f'Finished\n', append=True )
        self.update_status( f'f[0]={f[0]/1e6:.2f} MHz, Zmag[0]={Zmag[0]:.2f} Ohm  \n', append=True )
        self.plot_graph()
        
    #%% Display results          
    def plot_graph(self):    
        self.update_status( 'Plotting graph\n', append=True )        
        f     = self.analyser.res.f
        Zmag  = self.analyser.res.Zmag
        Zphase= self.analyser.res.Zphase
        self.graph[0].set_xdata( f/1e6 )
        self.graph[0].set_ydata( Zmag ) 
        self.graph[1].set_xdata( f/1e6 )
        self.graph[1].set_ydata( Zphase ) 
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        

    def set_f_scale( self ):
        fmin = self.fscalemin_SpinBox.value()
        fmax = self.fscalemax_SpinBox.value()
        if fmin<fmax:
            self.axs[0].set_xlim( fmin, fmax )
            self.axs[1].set_xlim( fmin, fmax )
            
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        
        return 0
        
    def set_Z_scale( self ):
        Zstr = self.Zscalemin_comboBox.currentText()
        Zmin = self.read_scaled_value ( Zstr )
        Zmax = self.read_scaled_value ( self.Zscalemax_comboBox.currentText() )
        if Zmin<Zmax:
            self.axs[0].set_ylim( Zmin, Zmax )
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        
        return 0
    
    
    def read_scaled_value (self, valuestr ):
        valuestr= valuestr.split(' ')
        if len(valuestr) == 1:
            mult = 1
        else:
            if valuestr[1]=='k':
                mult = 1e3;
            elif valuestr[1]=='M':
                mult = 1e6
            else:
                mult = 1
        value = float( valuestr[0] ) * mult
        return value

# =============================================================================
#             if Zmin<Zmax:
#                 self.axs[0].set_ylim( Zmin, Zmax )
#                 
#             self.fig.canvas.draw()
#             self.fig.canvas.flush_events()
#         
# =============================================================================

#%% Main function
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = read_analyser()
    window.show()
    sys.exit(app.exec_())
