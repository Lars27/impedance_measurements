# -*- coding: utf-8 -*-
"""
Libraries for communication with Trewmac TE300x network/impedance analysers 
using serial ports.

Open and configure a port
Send commands to configure the analyser
Read results and settings from analyser
Close port

Created on Mon Dec 12 11:36:32 2022

@author: larsh
"""

import serial    # Uses serial communication (COM-ports)
import numpy as np

#%%
class te300x:
    def __init__( self, port='COM1', timeout=10 ):
        self.port = serial.Serial( port, 115200, timeout = timeout )        

        
    def close(self):
        self.port.close()
        return 0      

        
    def version(self):
        self.port.write(b'V')
        return self.port.read_until( expected='\r', size=40 )    

    
    def dataformat(self):
        self.port.write(b'I')
        return self.port.read_until( expected='\r', size=40 )    

    
    def frequencyrange( self, fmin= 300e3, fmax= 20e6, np= 801 ):
        fmin_command = f'S{fmin/1e6:.2f}\r'.encode() 
        fmax_command = f'S{fmax/1e6:.2f}\r'.encode() 
        np_command   = f'P{np:d}\r'.encode() 
        self.port.write( fmin_command  )
        self.port.write( fmax_command )
        self.port.write( np_command )
        return 0

    
    def read_sweep( self ):
        self.port.write(b'I')
        f   = []
        Zmag= []
        Zphi= []        
        val = self.port.read_until( expected=b'END\r', size=200 )   
        val = val.split(b'\r')
        for k in range( 1, len(val)-1 ):
            line=val[k].split(b',')
            f.append(float( line[0] ))
            Zmag.append(float( line[1] ))
            Zphi.append(float( line[2] ))

        self.f     = np.array(f)
        self.Zmag  = np.array(Zmag)
        self.Zphase= np.array(Zphi)
        return 0


# =============================================================================
#     def read_sweep_log( self ):
#         self.port.write(b'G')        
#         return self.port.read_until( expected=b'END\r', size=200 )    
# =============================================================================

    def read_single( self, freq ):
        f_command= f'F{freq/1e6:.2f}\r'.encode()
        self.port.write( f_command )
        return self.port.read_until( expected='\r', size=50 )    


    def set_format( self, dataformat = 'polZ' ):
        dataformat_command = f'{dataformat}\r'.encode()
        self.port.write( dataformat_command )
        return self.port.read_until( expected='\r', size=50 )    


    def averaging ( self, avg = 64 ):  # Check formats below in references
        avg_command = f'Caveraging{avg:d}\r'.encode()
        self.port.write( avg_command )
        return self.port.read_until( expected='\r', size=50 )    


    def output ( self, output = 100 ):  # Check formats below in references
        output_command = f'Coutput{output:d}\r'.encode()
        self.port.write( output_command )
        return self.port.read_until( expected='\r', size=50 )    


    def mode ( self, mode = 'T' ):  # Check formats below in references
        if mode.lower()[0] == 't':
            self.port.write(b'CmodeS11\r')
        else:
            self.port.write(b'CmodeS22\r')
        return self.port.read_until( expected='\r', size=50 )    


    def baudrate( self, baud = 115200 ):  # Check formats below in references
        if baud > 10000:
            self.port.write(b'Cbaud115200\r')
        else:
            self.port.write(b'Cbaud9600\r')
        return self.port.read_until( expected='\r', size=50 )    



