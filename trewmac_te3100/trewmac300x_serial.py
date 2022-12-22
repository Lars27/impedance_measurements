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
import time

terminator=b'\r'

class te_result:  # Initialise with impossible values. To be set at object creation
    def __init__( self ):
        self.fmin  = 0.0
        self.fmax  = 0.0
        self.np    = 0
        
        self.averaging =-1.0
        self.z0        =-1.0
        self.output    =-1.0
        
        self.format = 'undefined'
        self.mode   = 'undefined'
        self.baudrate = 0.0
        
        self.f     = np.array(0.0)
        self.Zmag  = np.array(0.0)
        self.Zphase= np.array(0.0)
        
        
#%%
class te300x:
    def __init__( self ):
        return       
        
    def connect( self, port = 'COM1', timeout = 5 ):
        try:
            self.port = serial.Serial( port, 115200, timeout = timeout )    
            print (' Successfully opened')
            self.res  = te_result()
            self.set_frequencyrange( fmin= 300e3, fmax= 20e6, np= 500 )
            self.set_averaging ( avg = 16 )
            self.set_z0 ( z0 = 50 )
            self.set_output ( output = 100 )
            self.set_format( dataformat = 'polZ' )
            self.set_mode ( mode = 'T' )
            errorcode = 0
        except: #serial.SerialException:
            print (' Could not open port, return -1')
            self.port = -1            
            errorcode = -1
        return errorcode    
            
    def close(self):
        self.port.close()
        return 0      

    # Utility functions
    def read_text( self, max_length = 1000 ):
        rep = self.port.read_until( expected= terminator, size= max_length )
        return rep.removesuffix( terminator ).decode()
        
    def read_values( self, max_length = 1000 ):
        rep = self.port.read_until( expected= terminator, size= max_length )
        rep = rep.split(b',')
        rep = list(map(float, rep))
        return rep
    
    def read_sweep_values(self):     
        finished = False
        val=b''
        while not(finished):  # Read multiple times until all data acquired
            val = val + self.port.read_until( expected = b'END\r' )   
            finished = (self.port.in_waiting == 0)
        return val.decode()
    
    def read_sweep_line(self):
        f   = Zmag = Zphi = 0
        val = self.read_text()           
        finished = (val=='END') 
        if not(finished):
            line= val.split(',')
            f    = float( line[0] )
            Zmag = float( line[1] )
            Zphi = float( line[2] )
            
        return [f, Zmag, Zphi, finished ]

                               
    def send_configure ( self, parameter, value ):
        command = f'C{parameter}'
        fullcommand =  command.encode() + terminator + value.encode() + terminator
        self.port.write( fullcommand )
        return self.read_text()

    def send_freqrange ( self, parameter, value ):
        fullcommand =  parameter.encode() + value.encode() + terminator
        self.port.write( fullcommand )
        response = self.read_text()
        return float( response.split('=')[1] )

    # Read device information   
    def read_version(self):
        self.port.write(b'V')
        return self.read_text()
    
    def read_format(self):
        self.port.write(b'I')
        return self.read_text()
    
    # Configure device    
    def set_frequencyrange( self, fmin= 300e3, fmax= 20e6, np= 801 ):
        self.res.fmin = self.send_freqrange ( 'S', f'{fmin/1e6:.2f}'  )
        self.res.fmax = self.send_freqrange ( 'E', f'{fmax/1e6:.2f}'  )
        np            = self.send_freqrange ( 'P', f'{np:d}'  ) 
        self.res.np   = int (np )                             
        return 0
    
    def set_format( self, dataformat = 'polZ' ):
        result = self.send_configure ( 'format', dataformat )      
        self.res.format = result.split('=')[1] 
        return self.res.format 
    
    def set_averaging ( self, avg = 64 ):         
        result = self.send_configure ( 'averaging', f'{avg:d}' )     
        self.res.averaging = int( result.split('=')[1] )
        return self.res.averaging

    def set_output ( self, output = 100 ):  
        result = self.send_configure ( 'output', f'{output:.0f}' )      
        value  = result.split('=')[1]
        self.res.output  = float( value.split('%')[0] )
        return self.res.output  
    
    def set_z0 ( self, z0 = 50 ):  
        result = self.send_configure ( 'zo', f'{z0:0.1f}' )    
        self.res.z0  = float( result.split('=')[1] )
        return self.res.z0
    
    def set_mode ( self, mode = 'T' ):  
        if mode.lower()[0] == 't':
            value = 'S11'
        else:
            value= 'S21'
        result = self.send_configure ( 'mode', value )      
        self.res.mode  = result.split('=')[1]
        return self.res.mode 

    def set_baudrate( self, baud = 115200 ):  
        if baud > 10000:
            baud = 115200
        else:
            baud = 9600        
        result = self.send_configure( 'baud', f'{baud:d}' )      
        self.res.baudrate  = result.split(' ')[2]
        return self.res.baudrate            
    
    # Read results
    def read_single( self, freq ):
        f_command= f'F{freq/1e6:.2f}\r'.encode()
        self.port.write( f_command )
        rep = self.read_values()
        self.res.f    = np.array( rep[0] )
        self.res.Zmag = np.array( rep[1] )
        self.res.Zphi = np.array( rep[2] )
        return rep

    def read_sweep( self ):
        f   = []
        Zmag= []
        Zphi= []   
        self.port.reset_input_buffer()
        self.port.write(b'N')
        tic = time.perf_counter()
        val = self.read_sweep_values()
        val = val.split('\r')
        nf  = len(val)-3 
        for k in range( 1, nf+1 ):
            line=val[k].split(',')
            f.append(float( line[0] ))
            Zmag.append(float( line[1] ))
            Zphi.append(float( line[2] ))

        dt = time.perf_counter() - tic 
        self.res.f     = np.array(f)
        self.res.Zmag  = np.array(Zmag)
        self.res.Zphase= np.array(Zphi)
        self.res.nf    = nf
        self.res.dt    = dt
        return 0
    
    def read_sweep_point_by_point( self, resultgraph ):
        f   = []
        Zmag= []
        Zphi= []   
        self.port.write(b'N')
        tic = time.perf_counter()
        header   = self.read_text()
        finished = False
        nf       = 0
        print ('Reading data. Frequencies: ')
        while not(finished):
            ret= self.read_sweep_line()
            finished = ret[3] or (nf > self.res.np)
            if not(finished):
                nf = nf+1                
                f.append( ret[0] )
                Zmag.append( ret[1] )
                Zphi.append( ret[2] )
                
                print ( f' {f[nf-1]/1e6:.2f} ')
                resultgraph[0].set_data( f , Zmag )     
                
        dt = time.perf_counter() - tic    
        self.res.f     = np.array(f)
        self.res.Zmag  = np.array(Zmag)
        self.res.Zphase= np.array(Zphi)
        self.res.nf    = nf
        self.res.dt    = dt
        return 0
    
