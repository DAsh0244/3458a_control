from control import HP3458a
import sys
import time
import datetime

PORT = 'COM3'

if __name__ == "__main__":
    dmm = HP3458a(port=PORT)
    dmm.stop_readings()
    dmm.clear_buffer()
    dmm.set_digits(9)
    dmm.set_sample_rate(1)
    dmm.send_cmd('NRDGS 1 TIMER')
    try: 
        with open('log.txt','w') as outfile:
            while True:
                data = dmm.read_response()
                print(data)
                outfile.write(data+'\n')
    except KeyboardInterrupt:
        pass
