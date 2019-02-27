from control import HP3458a
from datetime import datetime
import sys

if __name__ == "__main__":
    dmm = HP3458a(port=sys.argv[1],baud=9600)
    dmm.stop_readings()
    dmm.set_digits(9)
    dmm.set_sample_rate(1)
    dmm.send_cmd('NRDGS 1 TIMER')
    dmm.send_cmd('TARM AUTO')
    dmm.send_cmd('TRIGGER AUTO')
    try:
        with open('log_{}.txt'.format(str(datetime.now()).replace(' ','_').replace(':','_')),'w') as outfile:
            while True:
                vout = dmm.read_response()
                ts = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                print('{},{}\n'.format(ts,vout))
                outfile.write('{},{}\n'.format(ts,vout))
    except KeyboardInterrupt:
        pass