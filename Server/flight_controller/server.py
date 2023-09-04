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

throttle_duty = 0
yaw_duty = 0
pitch_duty = 0
roll_duty = 0

throttle = PWM(Pin(0))
throttle.freq(50)
throttle.duty_u16(throttle_duty)
yaw = PWM(Pin(6))
yaw.freq(50)
yaw.duty_u16(yaw_duty)
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

            throttle_duty = rangify(float(data['throttle']), 0, 100)
            yaw_duty = rangify(float(data['yaw']), -100, 100)
            pitch_duty = rangify(float(data['pitch']), -100, 100)
            roll_duty = rangify(float(data['roll']), -100, 100)

            throttle.duty_u16(int(throttle_duty))
            yaw.duty_u16(int(yaw_duty))
            pitch.duty_u16(int(pitch_duty))
            roll.duty_u16(int(roll_duty))
            
            print(data)
        except:
            pass

    
@app.route('/assets/<path:path>')
def assets(request, path):
    return send_file('assets/'+path)


uasyncio.create_task(someLoop())
app.run()
