# -*- coding: utf-8 -*-
"""
Created on Mon Dec 19 14:17:40 2022

@author: lah
"""

import trewmac300x_serial
analyser=trewmac300x_serial.te300x(port='COM7')

ver = analyser.read_version()
