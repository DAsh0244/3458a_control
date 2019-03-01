from control import HP3458a
from datetime import datetime
import sys
import time
from argparse import ArgumentParser

# Typical run time in hours
RUN_TIME = 5.5

parser = ArgumentParser()
parser.add_argument('port', action='store',type=str,help='dmm serial port address')
parser.add_argument('dut',action='store',type=int,help='device under test number')
parser.add_argument('-run_time','-t',action='store',type=float,default=RUN_TIME,help='number of hours to log')
parser.add_argument('--addr','-a',action='store',type=int,default=22,help='GPIB address of the dmm')

if __name__ == "__main__":
    args = vars(parser.parse_args())
    dmm = HP3458a(port=args['port'],baud=9600)
    dmm.stop_readings()
    dmm.set_digits(9)
    dmm.set_sample_rate(1)
    dmm.send_cmd('NRDGS 1 TIMER')
    dmm.send_cmd('TARM AUTO')
    # dmm.send_cmd('TRIGGER AUTO')
    timeout = False
    run_time = float(args['run_time'])*3600
    try:
        with open('../logs/unit{}_{}_.txt'.format(args['dut'], str(datetime.now()).replace(' ','_').replace(':','_')),'w') as outfile:
            print('logging')
            start_time = time.time()
            while not timeout:
                vout = dmm.read_response()
                ts = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                # print('{},{}\n'.format(ts,vout))
                outfile.write('{},{}\n'.format(ts,vout))
                timeout = (time.time() - start_time) > run_time
    except KeyboardInterrupt:
        pass
    print('done')
