import sys

sys.path.append('../')

import connector
import uasyncio
from microdot_asyncio import Microdot, send_file
from microdot_asyncio_websocket import with_websocket


# Simulating some infinite action in the background
async def someLoop():
    from machine import Pin
    led = Pin(0, Pin.OUT)
    while True:
        led.toggle()
        await uasyncio.sleep(1)

app = Microdot()


@app.route('/')
def index(request):
    return send_file('index.html')


@app.route('/echo')
@with_websocket
async def echo(request, ws):
    from machine import Pin
    while True:
        data = await ws.receive()
        led = Pin(int(data), Pin.OUT)
        if led.value() == 0:
            led.on()
            await ws.send("PIN " + data + " ON")
        else:
            led.off()
            await ws.send("PIN " + data + " OFF")


uasyncio.create_task(someLoop())
app.run()
