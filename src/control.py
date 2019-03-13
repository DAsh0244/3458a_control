
from enum import Enum
import serial
import atexit

PORT = 'COM8'
ADDR = 22
BAUD = 9600
TIMEOUT = 1.0

class Log_Headers(Enum):
    CORRECTION_VALUE = 'CV'
    DAC_VALUE = 'DV'
    DUT_TEMP = 'TP'
    TEMP_SENSOR = 'TM'
    TRIM_VALUE = 'TR'
    MCU_TEMP = 'TH'


class MCU:
    ENCODING = 'ascii'
    def __init__(self, port, baud=BAUD, addr=ADDR, timeout=TIMEOUT):
        self._ser = serial.Serial(port,baud,timeout=timeout)
        atexit.register(self._ser.close)
        self._addr = addr

    # def send_cmd(self, cmd):
    #     self._ser.write((cmd.strip()+'\n').encode(self.ENCODING))
    
    def read_response(self):
        data = self._ser.readline().strip().decode(self.ENCODING)
        header, data = data.split(':')
        header = Log_Headers(header)
        data = float(data)
        return header, data
    
class HP3458a:
    ENCODING = 'ascii'
    CHARS = {
        'space':'\x01',
        'arrow_up_left':'\x02',
        'arrow_down_left':'\x03',
        'arrow_up':'\x04',
        'arrow_down':'\x05',
        'arrow_left':'\x06',
        'arrow_right':'\x07',
        'Delta':'\x08',
        'pi':'\x09',
        'sigma':'\x0b',
        'Sigma':'\x0c',
        'micro':'\x0e',
        'Omega':'\x0f',
        'degree':'\x10',
        'square':'\x11',
        'zero':'\x12',
        'neg_left_triangle':'\x13',
        'under_0':'\x14',
        'under_1':'\x15',
        'under_2':'\x16',
        'under_3':'\x17',
        'under_4':'\x18',
        'under_5':'\x19',
        'under_6':'\x1a',
        'under_7':'\x1b',
        'under_8':'\x1c',
        'under_9':'\x1d',
        'neg_right_triangle':b'\x1e',
        'left_triangle':b'\x1f',
        }
    def __init__(self, port, baud=BAUD, addr=ADDR, timeout=TIMEOUT, buf_clear=True, init_prologix=False):
        self._ser = serial.Serial(port,baud,timeout=timeout)
        atexit.register(self._ser.close)
        self._addr = addr
        if init_prologix:
            self._ser.write(b'++mode 1\n')
            self._ser.write(b'++auto 1\n')
            self._ser.write(b'++addr '+str(self._addr).encode(self.ENCODING)+b'\n')
            self._ser.write(b'++ver\n')
            resp = self._ser.readline().strip().decode(self.ENCODING)
            if 'Prologix GPIB-USB Controller' not in resp:
                raise ValueError('Unable to verify interface is a Prologix GPIB-USB Controller')
        if buf_clear:
            self.stop_readings()
            self.clear_buffer()
            self.send_cmd('ID?')
            self._id = self.read_response()
            if '3458a' not in self._id.lower():
                raise ValueError('Returned ID is not a 3458a')
            self._rev = self.get_rev()

    def get_rev(self):
        self.send_cmd('REV?')
        return tuple(self.read_response().split(','))

    def send_cmd(self, cmd):
        self._ser.write((cmd.strip()+'\n').encode(self.ENCODING))
    
    def read_response(self):
        data = self._ser.readline().strip().decode(self.ENCODING)
        return data

    def clear_buffer(self):
        tmp = self._ser.readline()
        while tmp != b'':
            tmp = self._ser.readline()

    def set_digits(self, precision=9):
        self.send_cmd('NDIG {}'.format(precision))

    def stop_readings(self):
        self.send_cmd('TARM HOLD')

    def reset(self):
        self.send_cmd('RESET')

    def set_display(self, enable=True, content=None):
        if content is None:
            if enable:
                self.send_cmd('DISP ON')
            else:
                self.send_cmd('DISP OFF')
        if content is not None and len(content) <=75:
            self.send_cmd('DISP MSG, {}'.format(content))

    def clear_display(self):
        self.send_cmd('DISP OFF, "{}"'.format(''.join([self.CHARS['space']]*16)))

    def check_ratio(self):
        self.send_cmd('RATIO?')
        return self.read_response()

    def set_sample_rate(self,sample_rate):
        period = 1.0/sample_rate
        self.set_timer(period)

    def set_timer(self,timer_val):
        self.send_cmd('TIMER {}'.format(timer_val))

    def set_ratio(self,enable=True):
        self.send_cmd('RATIO {}'.format(1 if enable else 0))

    def take_readings(self, num_readings=1):
        self.send_cmd('TARM SGL,{}'.format(num_readings))
        readings = [self.read_response() for i in range(0,num_readings)]
        return readings


Agilent3458a = Keysight3458a = HP3458a

if __name__ == "__main__":
    pass