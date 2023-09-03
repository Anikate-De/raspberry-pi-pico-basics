import sys
sys.path.append('../')

import connector

from microdot import Microdot, send_file
from microdot_websocket import with_websocket

app = Microdot()


@app.route('/')
def index(request):
    return send_file('index.html')


@app.route('/echo')
@with_websocket
def echo(request, ws):
    from machine import Pin
    while True:
        data = ws.receive()
        led = Pin(int(data), Pin.OUT)
        if led.value() == 0:
            led.on()
            ws.send("PIN " + data + " ON")
        else:
            led.off()
            ws.send("PIN " + data + " OFF")


app.run()