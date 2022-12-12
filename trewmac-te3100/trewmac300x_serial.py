# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 11:36:32 2022

@author: larsh
"""

import serial

class tw300x:
    def __init__(self, port='COM7', time_out = 10 ):
        ser = serial.Serial( port, 115200, timeout=time_out )
        return ser
        
    def open(self):
        self.open()
        return 0

    def close(self):
        self.close()
        return 0      
       
    def ver(self):
        self.write('V')
        return self.read_until( expected='\r', size=40 )    
    
    def dataformat(self):
        self.write('I')
        return self.read_until( expected='\r', size=40 )    
    
    def frequencyrange( self, fmin= 300e3, fmax= 20e6, np= 801 ):
        self.write(f'S{fmin/1e6:.2f}\r')
        self.write(f'E{fmax/1e6:.2f}\r')
        self.write(f'P{np:d}\r')
        return 0
    
    def read_sweep( self ):
        self.write('I')        
        return self.read_until( expected='END\r', size=200 )    

    def read_sweep_log( self ):
        self.write('G')        
        return self.read_until( expected='END\r', size=200 )    

    def read_single( self, freq ):
        self.write(f'F{freq/1e6:.2f}\r')
        return self.read_until( expected='\r', size=50 )    

    def set_format( self, dataformat = 'polZ' ):
        self.write(f'{dataformat}\r')
        return self.read_until( expected='\r', size=50 )    

    def averaging ( self, avg = 64 ):  # Check formats below in references
        self.write(f'Caveraging{avg:d}\r')
        return self.read_until( expected='\r', size=50 )    

    def output ( self, output = 100 ):  # Check formats below in references
        self.write(f'Coutput{output:d}\r')
        return self.read_until( expected='\r', size=50 )    

    def mode ( self, mode = 'T' ):  # Check formats below in references
        if mode.lower()[0] == 't':
            self.write('CmodeS11\r')
        else:
            self.write('CmodeS22\r')
        return self.read_until( expected='\r', size=50 )    

    def baudrate( self, baud = 115200 ):  # Check formats below in references
        if baud > 10000:
            self.write('Cbaud115200\r')
        else:
            self.write('Cbaud9600\r')
        return self.read_until( expected='\r', size=50 )    



