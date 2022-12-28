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
import matplotlib.pyplot as plt     # For plotting
import matplotlib                   # For setup with Qt
import us_utilities as us           # Utilities made fro USN ultrasound lab
import trewmac300x_serial as te     # Serial inerface to Trewmac analysers

#%% Set up GUI from Qt5
matplotlib.use('Qt5Agg')
analyser_main_window, QtBaseClass = uic.loadUiType('read_trewmac_gui.ui')


class acquisition_control:  # Initialise with impossible values. To be set at object creation
    def __init__( self ):
        self.freeze   = False
        self.finished = False
       
        
#%% Class and defs
class read_analyser(QtWidgets.QMainWindow, analyser_main_window):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        analyser_main_window.__init__(self)
        self.setupUi(self)

        # Program flow controls        
        self.run_control  = acquisition_control()

        
        # Connect GUI elements
        self.fmin_SpinBox.valueChanged.connect( self.set_frequency_range )
        self.fmax_SpinBox.valueChanged.connect( self.set_frequency_range )
        self.np_SpinBox.valueChanged.connect( self.set_frequency_range )
        self.average_SpinBox.valueChanged.connect( self.set_average )
        self.z0_SpinBox.valueChanged.connect(self.set_z0)       
        self.output_SpinBox.valueChanged.connect( self.set_output )
        self.fscalemin_SpinBox.valueChanged.connect( self.set_f_scale )
        self.fscalemax_SpinBox.valueChanged.connect( self.set_f_scale )       
        self.Zscalemin_comboBox.activated.connect( self.set_Z_scale )
        self.Zscalemax_comboBox.activated.connect( self.set_Z_scale )
        self.connect_button.clicked.connect( self.connect_analyser )
        self.acquire_button.clicked.connect( self.acquire_trace )
        self.save_button.clicked.connect( self.save_results ) 
        self.close_button.clicked.connect( self.close_app ) 
        self.freeze_checkBox.clicked.connect( self.freeze )
        
        # Initialise result graph
        #plt.ion()         # Does not seem to make any difference
        fig, axs = plt.subplots( nrows=2, ncols=1, figsize=(8, 12) )       
        for k in range( 0, 2):   # Commpn for both subplots
            axs[k].set_xlabel('Frequency [MHz]')
            axs[k].set_xlim(0 , 20)   
            axs[k].grid( True )   
            
        axs[0].grid( visible=True, which='minor', axis='y' )
        axs[0].set_ylabel('|Z| [Ohm]')
        axs[1].set_ylabel('arg(Z) [Deg]')       
        axs[0].set_ylim( 1, 1e6 )
        axs[1].set_ylim( -90, 90 )

        # Create handle to datapoints, empty so far
        graphs=[ axs[0].semilogy( [], [] )[0], axs[1].plot( [], [] )[0] ] 
        
        fig.show()
        
        self.graph= graphs
        self.axs  = axs
        self.fig  = fig               

        # Initialise instrument
        self.analyser = te.te300x()

        self.main_tabWidget.setTabEnabled(0, False )
        self.main_tabWidget.setTabEnabled(1, False )
        self.main_tabWidget.setCurrentIndex( 2 )
        
        self.statusBar().showMessage('Program started')
        

    #%% Program run 
    def close_app(self):
        self.statusBar().showMessage( 'Closing' )
        plt.close(self.fig)
        try:
            self.analyser.close()
            errorcode = 0
        except:
            errorcode =-1
        finally:
            self.close()       
        return errorcode 
    
    def freeze( self ): 
        self.res.freeze = self.freeze_checkBox.isChecked()  
        self.update_status( f'Freeze {self.res.freeze}' , append = True )
        self.statusBar().showMessage( f'Display Freeze {self.res.freeze}' )

        return 0
        
    def save_results( self ):
        resultfile = us.find_filename(prefix='ZTE', ext='trc', resultdir='results')
        us.save_impedance_result( resultfile, self.analyser.res )
        self.resultfile_Edit.setText( resultfile ) 
        self.statusBar().showMessage( f'Result saved to {resultfile}' )
        
    def update_status( self, message, append = False ):
        if append:
            old_message = self.status_textEdit.toPlainText()
            message += old_message
        self.status_textEdit.setText(message)  
        return message    
            
    def read_scaled_value (self, valuestr ): 
        # Read value formatted as number with SI-prefix
        valuestr= valuestr.split(' ')
        if len(valuestr) == 1:
            mult = 1
        else:
            if   valuestr[1]== 'k':
                mult = 1e3;
            elif valuestr[1]== 'M':
                mult = 1e6
            elif valuestr[1]== 'G':
                mult = 1e9
            else:
                mult = 1
        value = float( valuestr[0] ) * mult
        return value
   

    #%% Instrument interaction
    def connect_analyser( self ):
        com_port  = self.port_Edit.text()
        errorcode = self.analyser.connect( port = com_port, timeout = 5 )
        if errorcode == -1:
            self.status_textEdit.setText(f'Error: Could not open {com_port}\n' ) 
            self.portstatus_Edit.setText( 'Not Connected' )
            self.portstatus_Edit.setStyleSheet("background-color : red; color : white")
            self.statusBar().showMessage( 'Could not connect analyser' )
        else:
            self.update_status( 'Device connected\n', append=False )           
            self.portstatus_Edit.setStyleSheet("background-color : green; color : white")
            self.set_frequency_range()
            self.set_average( ) 
            self.set_z0( )
            self.set_output( )
            ver = self.analyser.read_version()
            self.update_status( f'Version {ver}\n', append=True)           
            self.portstatus_Edit.setText( 'Connected' )  
            self.main_tabWidget.setTabEnabled(0, True )
            self.main_tabWidget.setTabEnabled(1, True )
            self.statusBar().showMessage( 'Analyser connected' )

        return errorcode 
    
    def set_frequency_range( self ):
        fmin = self.fmin_SpinBox.value()
        fmax = self.fmax_SpinBox.value()
        npts = self.np_SpinBox.value()
        self.analyser.set_frequencyrange( fmin*1e6, fmax*1e6, npts )
        message = f'frange = {fmin:.2f} ... {fmax:.2f} MHz, {npts:4d} pts.\n'
        self.update_status( message, append=True )   
        self.statusBar().showMessage( f'Frequency range changed to {fmin:.2f} to {fmax:.2f} MHz, {npts:4d} pts' )
        return 0
        
    def set_average( self ):
        average = self.average_SpinBox.value()
        average = self.analyser.set_averaging ( average )
        self.update_status( f'average = {average:3d}\n', append=True )
        self.statusBar().showMessage( f'Averaging changed to {average:3d}' )
        return average
        
    def set_output( self ):
        output = self.output_SpinBox.value()
        output = self.analyser.set_output ( output )
        self.update_status( f'Output = {output:.0f} %\n', append=True )
        self.statusBar().showMessage( f'Output level changed to {output:.0f} %' )        
        return output
    
    def set_z0( self ):
        z0 = self.z0_SpinBox.value()
        z0 = self.analyser.set_z0 ( z0 )
        self.update_status( f'Z0 = {z0:.1f} Ohm\n', append=True )
        self.statusBar().showMessage( f'Reference inpedance changed to {z0:.1f} Ohm' )        
        return z0

    def acquire_trace( self ):
        self.resultfile_Edit.setText('Not saved') 
        
        self.res.finished = False
        while not( self.res.finished):
            if not(self.res.freeze):
                self.statusBar().showMessage( 'Reading data from analyser' )        
                self.update_status( 'Reading data from analyser ... \n', append=True )
                self.analyser.read_sweep_point_by_point( self.graph , self.fig )
                self.update_status( 'Finished\n', append=True )
                
                self.fig.canvas.draw()          # --- TRY: Probably not sufficient
                self.fig.canvas.flush_events()  # --- TRY: Probably good
               # self.update_status( f'f[0]={f[0]/1e6:.2f} MHz, Zmag[0]={Zmag[0]:.2f} Ohm  \n', append=True )                
        self.statusBar().showMessage( 'Reading from analyser finished' )        
        return 0
                
    #%% Display results          
# =============================================================================
#     def plot_graph(self):    
#         self.update_status( 'Plotting graph\n', append=True )        
#         f     = self.analyser.res.f
#         Zmag  = self.analyser.res.Zmag
#         Zphase= self.analyser.res.Zphase
#         self.graph[0].set_xdata( f/1e6 )
#         self.graph[0].set_ydata( Zmag ) 
#         self.graph[1].set_xdata( f/1e6 )
#         self.graph[1].set_ydata( Zphase ) 
#         self.fig.canvas.draw()
#         self.fig.canvas.flush_events()
#         return 0        
# 
# =============================================================================
    def set_f_scale( self ):
        fmin = self.fscalemin_SpinBox.value()
        fmax = self.fscalemax_SpinBox.value()
        if fmin<fmax:
            self.axs[0].set_xlim( fmin, fmax )
            self.axs[1].set_xlim( fmin, fmax )            
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()  
            self.statusBar().showMessage( 'Frequency axis changed' ) 
        return 0
        
    def set_Z_scale( self ):
        Zstr = self.Zscalemin_comboBox.currentText()
        Zmin = self.read_scaled_value ( Zstr )
        Zmax = self.read_scaled_value ( self.Zscalemax_comboBox.currentText() )
        if Zmin<Zmax:
            self.axs[0].set_ylim( Zmin, Zmax )        
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()        
            self.statusBar().showMessage( 'Impedance axis changed' ) 
        return 0


#%% Main function
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = read_analyser()
    window.show()
    sys.exit(app.exec_())