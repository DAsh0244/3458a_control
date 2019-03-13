from control import HP3458a,MCU,Log_Headers
from datetime import datetime
import sys
import time
from argparse import ArgumentParser

# Typical run time in hours
RUN_TIME = 5.5
RANGE = 10
RES = 100e-7
HEADERS = [
    # Log_Headers.CORRECTION_VALUE,
    # Log_Headers.DAC_VALUE,
    Log_Headers.DUT_TEMP,
    Log_Headers.TEMP_SENSOR,
    Log_Headers.TRIM_VALUE,
    Log_Headers.MCU_TEMP
]
MCU_NUM_READINGS = len(HEADERS)

SAMPLE_RATE = 1

parser = ArgumentParser()
parser.add_argument('dmm_port', action='store',type=str,help='dmm serial port address')
parser.add_argument('mcu_port',action='store',type=str,help='mcu serial port address')
parser.add_argument('dut',action='store',type=int,help='device under test number')
parser.add_argument('-run_time','-t',action='store',type=float,default=RUN_TIME,help='number of hours to log')
parser.add_argument('--addr','-a',action='store',type=int,default=22,help='GPIB address of the dmm')
parser.add_argument('--msg','-m',action='store',type=str,help='message to append to file name',default='test')

if __name__ == "__main__":
    args = vars(parser.parse_args())
    dmm = HP3458a(port=args['dmm_port'],baud=9600)
    dmm.stop_readings()
    mcu = MCU(port=args['mcu_port'],baud=9600)
    dmm.set_digits(9)
    dmm.set_sample_rate(SAMPLE_RATE)
    dmm.send_cmd('NRDGS 1 TIMER')
    dmm.send_cmd('TARM AUTO')
    dmm.send_cmd('NPLC 1000')
    dmm.send_cmd('RANGE {},{}'.format(RANGE,RES/RANGE*100))
    # dmm.send_cmd('TRIGGER AUTO')
    timeout = False
    run_time = float(args['run_time'])*3600
    try:
        with open('../logs/unit{}_{}_{}.txt'.format(args['dut'],
                                                    str(datetime.now()).replace(' ','_').replace(':','_'),
                                                    args['msg'].replace(' ','_').replace(':','_'))
                                                    ,'w') as outfile:
            print('logging')
            outfile.write('#{}\n'.format(datetime.now().strftime("%m/%d/%Y, %H:%M:%S")))
            start_time = time.time()
            while not timeout:
                vout = dmm.read_response()
                ts = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                elapsed_time = time.time() - start_time
                mcu_data = {}
                for header in HEADERS:
                    mcu_data = {header: None}
                for i in range(MCU_NUM_READINGS):
                    header, data = mcu.read_response()
                    mcu_data[header] = data
                # print('{},{}\n'.format(ts,vout))
                outfile.write('{},{},'.format(ts,vout))
                for header, data in mcu_data.items():
                    outfile.write('{},'.format(data))
                outfile.write('\n')
                time.sleep(1.5/SAMPLE_RATE)
                timeout = (time.time() - start_time) > run_time
    except KeyboardInterrupt:
        pass
    print('done')
