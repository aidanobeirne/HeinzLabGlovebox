# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 15:55:49 2020

@author: Mrkus A. Huber
"""

import serial
import sys


class ElliptecMotor(serial.Serial):

    def __init__(self, port, ConversionFactorMicrometer, baudrate=460800, bytesize=8, parity='N', timeout=2):
        try:
            #self.motor = s.Serial(port, baud, bytesize, parity)
            super().__init__(port, baudrate, bytesize, parity, timeout)
        except serial.SerialException:
            print('Could not open port %s' % port)
            sys.exit()

        if self.is_open:
            print('Connection established!')
            
            self.ConversionFactorMicrometer = ConversionFactorMicrometer
        
    def getPosition(self, ChannelNumber=0):
        ChanIdent = str(ChannelNumber).zfill(2)
        command = '0A04'.encode('utf-8') + ChanIdent.encode('utf-8') + '000000'.encode('utf-8')
        self.request = command
        self.write(command)
        msg = self.read_until(terminator=b'\n')
        if (not msg.endswith(b'\r\n') or (len(msg) == 0)):
            print('Status/Response may be incomplete!')
            return None
        msg = msg.decode().strip()
        positionMsg = msg[8:11]
        
    
    def setPosition(self):
        
        pass

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