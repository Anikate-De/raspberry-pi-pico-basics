import sys
sys.path.append('../')

import connector

from microdot_asyncio import Microdot, send_file
from microdot_asyncio_websocket import with_websocket

import uasyncio
import ujson

from machine import Pin, PWM

sys.path.append('../../')

from utils import *

throttle_cw_duty = 0
throttle_acw_duty = 0

pitch_duty = 0
roll_duty = 0

throttle_cw = PWM(Pin(0))
throttle_cw.freq(50)
throttle_cw.duty_u16(throttle_cw_duty)

throttle_acw = PWM(Pin(6))
throttle_acw.freq(50)
throttle_acw.duty_u16(throttle_acw_duty)

pitch = PWM(Pin(10))
pitch.freq(50)
pitch.duty_u16(pitch_duty)

roll = PWM(Pin(14))
roll.freq(50)
roll.duty_u16(roll_duty)


# Simulating some infinite action in the background
async def someLoop():
    i = 0
    while True:
        i += 1
        print('Some task has been running for', i, 'seconds...', end='\r')
        await uasyncio.sleep(1)


app = Microdot()


@app.route('/')
def index(request):
    return send_file('index.html')


@app.route('/control')
@with_websocket
async def controls(request, ws):
    while True:
        try:
            data = await ws.receive()

            data = ujson.loads(data)

            throttle_cw_duty = throttle_acw_duty = rangify(float(data['throttle']), 0, 100)
            throttle_delta =  rangify(float(data['yaw']), -100, 100, -16384, 16384)

            throttle_acw_duty += throttle_delta
            throttle_cw_duty -= throttle_delta

            if throttle_acw_duty < 0:
                throttle_acw_duty = 0
            elif throttle_acw_duty > 65535:
                throttle_acw_duty = 65535

            if throttle_cw_duty < 0:
                throttle_cw_duty = 0
            elif throttle_cw_duty > 65535:
                throttle_cw_duty = 65535

            pitch_duty = rangify(float(data['pitch']), -100, 100, 1400, 7900)
            roll_duty = rangify(float(data['roll']), -100, 100, 1400, 7900)

            throttle_cw.duty_u16(int(rangify(throttle_cw_duty, 0, 65535)))
            throttle_acw.duty_u16(int(rangify(throttle_acw_duty, 0, 65535, 3700, 4200)))
            pitch.duty_u16(int(pitch_duty))
            roll.duty_u16(int(roll_duty))
            
            print(rangify(throttle_cw_duty, 0, 65535, 3700, 4200), rangify(throttle_acw_duty, 0, 65535, 3700, 4200), pitch_duty, roll_duty)
        except:
            pass

    
@app.route('/assets/<path:path>')
def assets(request, path):
    return send_file('assets/'+path)


uasyncio.create_task(someLoop())
app.run()
