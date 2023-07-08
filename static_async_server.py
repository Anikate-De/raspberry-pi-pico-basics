import socket
import time

import network
import uasyncio
from machine import Pin

SSID = 'Shubho'
PASSWORD = '12156891'

led = Pin('LED', Pin.OUT)
html = '''
<html>
<body>
<h1>Raspberry Pi Pico W Server</h1>
<p>Welcome to this Raspberry Pi Pico Server <strong>asynchronously</strong> deployed on the network {}</p>
<p>Server has been online for {} seconds</p>
</body>
</html>
'''


def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.disconnect()

    # Connect to the network
    wlan.connect(SSID, PASSWORD)

    # Wait for connection
    max_attempts = 200
    while max_attempts > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_attempts -= 1
        time.sleep(0.1)
        led.toggle()
        print('Connecting to network...')

    if wlan.isconnected():
        print('Connected to network', SSID)

        # Print network information
        print('Network config:', wlan.ifconfig())
        led.value(1)
    else:
        print('Connection failed to network', SSID)
        led.value(0)


async def serve(reader, writer):
    print('Client connected')

    request = await reader.readline()
    print('Request:', request)

    while True:
        line = await reader.readline()
        if not line or line == b'\r\n':
            break

    response = html.format(SSID, time.ticks_cpu() // 1000000)
    writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    writer.write(response)
    await writer.drain()
    await writer.wait_closed()
    print('Client disconnected')


async def main():
    connect()

    print('Starting server...')
    uasyncio.create_task(uasyncio.start_server(serve, '0.0.0.0', 80))
    while True:
        await uasyncio.sleep(1)


try:
    uasyncio.run(main())
finally:
    uasyncio.new_event_loop()
