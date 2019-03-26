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
    Log_Headers.TEMP_SENSOR,
    Log_Headers.DUT_TEMP,
    Log_Headers.TRIM_VALUE,
    Log_Headers.MCU_TEMP
]
MCU_NUM_READINGS = len(HEADERS)

SAMPLE_RATE = 1
CONV_TIME = 1.0

parser = ArgumentParser()
parser.add_argument('dmm_port', action='store',type=str,help='dmm serial port address')
parser.add_argument('mcu_port',action='store',type=str,help='mcu serial port address')
parser.add_argument('dut',action='store',type=int,help='device under test number')
parser.add_argument('-run_time','-t',action='store',type=float,default=RUN_TIME,help='number of hours to log')
parser.add_argument('--addr','-a',action='store',type=int,default=22,help='GPIB address of the dmm')
parser.add_argument('--msg','-m',action='store',type=str,help='message to append to file name',default='test')

if __name__ == "__main__":
    args = vars(parser.parse_args())
    dmm = HP3458a(port=args['dmm_port'],baud=9600,timeout=1.1/SAMPLE_RATE)
    dmm.stop_readings()
    mcu = MCU(port=args['mcu_port'],baud=9600,timeout=0.5)
    dmm.set_digits(9)
    # dmm.set_sample_rate(0.9*SAMPLE_RATE)
    dmm.send_cmd('NRDGS 1 TIMER')
    dmm.send_cmd('NPLC 30')
    dmm.send_cmd('TIMER 0.01')
    dmm.send_cmd('RANGE {},{}'.format(RANGE,RES/RANGE*100))
    dmm.send_cmd('APER {:.6f}'.format(CONV_TIME))
    dmm.send_cmd('TARM AUTO')
    dmm.send_cmd('TRIG AUTO')
    time.sleep(CONV_TIME+2/SAMPLE_RATE)
    timeout = False
    run_time = float(args['run_time'])*3600
    loops = 0
    try:
        mcu_data = {header: None for header in HEADERS}
        with open('../logs/unit{}_{}_{}.txt'.format(args['dut'],
                                                    str(datetime.now()).replace(' ','_').replace(':','_'),
                                                    args['msg'].replace(' ','_').replace(':','_'))
                                                    ,'w') as outfile:
            print('logging')
            outfile.write('#{}\n'.format(datetime.now().strftime("%m/%d/%Y %H:%M:%S")))
            start_time = time.time()
            while not timeout:
                vout = dmm.read_response()
                if not vout:
                    print(loops)
                # while vout == '':
                    # vout = dmm.read_response()
                # ts = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                elapsed_time = time.time() - start_time
                # wait for a proper cycle to come around
                line = mcu.read_response()
                while line != (None,None):
                    line = mcu.read_response()
                for i in range(MCU_NUM_READINGS):
                    header, data = mcu.read_response()
                    mcu_data[header] = data
                # print('{},{}\n'.format(ts,vout))
                outfile.write('{},{},'.format(elapsed_time, vout))
                for header, data in mcu_data.items():
                    outfile.write('{},'.format(data))
                outfile.write('\n')
                time.sleep(1.1/SAMPLE_RATE)
                loops += 1
                # print('looping: {}'.format(loops))
                # timeout = (time.time() - start_time) > run_time
                timeout = elapsed_time > run_time
    except KeyboardInterrupt:
        pass
    print(loops)
    print('done')
