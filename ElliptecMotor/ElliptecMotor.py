# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 16:08:59 2020

@author: Markus A. Huber 
"""

# This script is actually just a slight adaption to the scripts from
# https://github.com/cdbaird/TL-rotation-control
# and all important features copied in a single file
# not nice, but it works.

import serial
import sys

import serial as s
import serial.tools.list_ports as lp

# Some helper functions for elliptec module

def find_ports():
    avail_ports = []
    for port in lp.comports():
        if port.serial_number:
            #print(port.serial_number)
            try:
                p = s.Serial(port.device)
                p.close()
                avail_ports.append(port)
            except (OSError, s.SerialException):
                print('%s unavailable.\n' % port.device)
                #pass
    return avail_ports

def parse(msg):
    if (not msg.endswith(b'\r\n') or (len(msg) == 0)):
        print('Status/Response may be incomplete!')
        return None
    msg = msg.decode().strip()
    code = msg[1:3]
    try: 
        addr = int(msg[0], 16)
    except ValueError:
        raise ValueError('Invalid Address: %s' % msg[0])

    if (code.upper() == 'IN'):
        info = {'Address' : str(addr),
            'Motor Type' : msg[3:5],
            'Serial No.' : msg[5:13],
            'Year' : msg[13:17],
            'Firmware' : msg[17:19],
            'Thread' : is_metric(msg[19]),
            'Hardware' : msg[20],
            'Range' : (int(msg[21:25], 16)),
            'Pulse/Rev' : (int(msg[25:], 16)) }
        return info

    elif ((code.upper() == 'PO') or code.upper() == 'BO'):
        pos = msg[3:]
        return (code, (s32(int(pos, 16))))

    elif (code.upper() == 'GS'):
        errcode = msg[3:]
        return (code, str(int(errcode, 16)))

    else:
        return (code, msg[3:])


## Fails if message contains hex digit > 9 after code, e.g. '0POFFFFFFFD'. Deprecated
def get_msg_code(msg):
    print('WARNING: get_msg_code does not work correctly. Don\'t use it!')
    code = [c for c in msg if not c.isdigit()]
    return ''.join(code)

def is_metric(num):
    if (num == '0'):
        thread_type = 'Metric'
    elif(num == '1'):
        thread_type = 'Imperial'
    else:
        thread_type = None

    return thread_type

def s32(value): # Convert 32bit signed hex to int
    return -(value & 0x80000000) | (value & 0x7fffffff)

def error_check(status):
    if not status:
        print('Status is None')
    elif (status[0] == "GS"):
        if (status[1] != '0'): # is there an error?        
            err = error_codes[status[1]]
            print('ERROR: %s' % err)
        else:
            print('Status OK')

def move_check(status):
    if not status:
        print('Status is None')
    elif status[0] == 'GS':
        error_check(status)
    elif ((status[0] == "PO") or (status[0] == "BO")):
        print('Move Successful')
    else:
        print('Unknown response code %s' % status[0])

class Parser():
    def __init__(self, request, response):
        if ((request is None) or (response is None)):
            raise ValueError('Parser input cannot be empty!')

        self.request = self.parse(request)
        self.response = self.parse(response)

    def parse(self, msg):
        msg = msg.decode().strip()
        addr = msg[0]
        code = msg[1:3]
        data = msg[3:]
        return (addr, code, data)

get_ = {
    'info' : b'in',
    'status' : b'gs',
    'position': b'gp',
    'stepsize' : b'gj'
    }

set_ = {
    'stepsize' : b'sj',
    'isolate'  : b'is'
    }

mov_ = {
    'home' : b'ho',
    'forward' : b'fw',
    'backward' : b'bw',
    'absolute' : b'ma',
    'relative' : b'mr'
    }

error_codes = {
    '0' : 'Status OK',
    '1' : 'Communication Timeout',
    '2' : 'Mechanical Timeout',
    '3' : 'Command Error',
    '4' : 'Value Out of Range',
    '5' : 'Module Isolated',
    '6' : 'Module Out of Isolation',
    '7' : 'Initialisation Error',
    '8' : 'Thermal Error',
    '9' : 'Busy',
    '10': 'Sensor Error',
    '11': 'Motor Error',
    '12': 'Out of Range',
    '13': 'Over Current Error',
}



class ElliptecMotor(serial.Serial):

    def __init__(self, port, baudrate=9600, bytesize=8, parity='N', timeout=1):
        try:
            #self.motor = s.Serial(port, baud, bytesize, parity)
            super().__init__(port, baudrate=9600, bytesize=8, parity='N', timeout=1)
        except serial.SerialException:
            print('Could not open port %s' % port)
            sys.exit()

        if self.is_open:
            print('Connection established!')
            #self.port = port
            self._get_motor_info()
            #self.conv_factor = float(self.info['Range'])/float(self.info['Pulse/Rev'])
            self.range = self.info['Range']
            self.counts_per_rev = self.info['Pulse/Rev']
            #self.get_('status')
            #self.get_('position')

    def do_(self, req='home', data='0', addr='0'):
        try:
            instruction = mov_[req]
        except KeyError:
            print('Invalid Command: %s' % req)
        else:
            command = addr.encode('utf-8') + instruction
            if data:
                command += data.encode('utf-8')

            self.request = command
            self.write(command)
            self.response = self.read_until(terminator=b'\n')
            self.status = parse(self.response)
            move_check(self.status)

    def set_(self, req='', data='', addr='0'):
        try:
            instruction = set_[req]
        except KeyError:
            print('Invalid Command')
        else:
            command = addr.encode('utf-8') + instruction
            if data:
                command += data.encode('utf-8')

            self.write(command)
            #print(command)
            response = self.read_until(terminator=b'\n')
            #print(response)
            self.status = parse(response)
            error_check(self.status)

    def get_(self, req='status', data='', addr='0'):
        try:
            instruction = get_[req]
        except KeyError:
            print('Invalid Command')
        else:
            command = addr.encode('utf-8') + instruction
            if data:
                command += data.encode('utf-8')

            self.write(command)
            #print(command)
            response = self.read_until(terminator=b'\n')
            print(response)
            self.status = parse(response)
            error_check(self.status)
    
    def moveHome(self):
        self.do_('home')
        
    def moveForward(self):
        self.do_('forward')
        
    def moveBackward(self):
        self.do_('backward')

#    def deg_to_hex(self, deg):
#        factor = self.counts_per_rev//self.range
#        val = hex(deg*factor)
#        return val.replace('0x', '').zfill(8).upper()
#
#    def hex_to_deg(self, hexval):
#        factor = self.counts_per_rev//self.range
#        val = round(int(val,16)/factor)
#        return val
            
          
    def moveToPosition(self, position):
        if int(position) >= 0 and int(position) <= 3:
            self.do_('absolute', hex(int(position)*31).replace('0x','').zfill(8).upper())
        else:
            print("Position out of range. Use integer numbers 0, 1, 2 or 3")
            
        


## Private methods

    def _get_motor_info(self):
            # instruction = cmd['info']
            self.info = self._send_command(get_['info'])

    def _send_command(self, instruction, msg=None, address=b'0'):
        command = address + instruction
        if msg:
            command += msg
        #print(command)
        self.write(command)
        response = self.read_until(terminator=b'\n')
        #print(response)
        return parse(response)

    def __str__(self):
        string = '\nPort - ' + self.port + '\n\n'
        for key in self.info:
            string += (key + ' - ' + str(self.info[key]) + '\n')            
        return string


    


if __name__ =='__main__':
    pass

    










