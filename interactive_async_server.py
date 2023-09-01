import time

import network
import uasyncio
from machine import Pin

SSID = 'Shubho'
PASSWORD = '12156891'

led = Pin(0, Pin.OUT)
html = '''
<!DOCTYPE html>
<html>

<head>
    <style>
        body {{
            background-color: #f2f2f2;
            font-family: Arial, Helvetica, sans-serif;
            text-align: center;
        }}

        h1 {{
            color: #4CAF50;
            font-size: 6vw;
        }}

        p {{
            font-size: 20px;
            font-size: 4vw;
        }}

        button {{
            border: none;
            color: white;
            padding: 16px 32px;
            text-align: center;
            text-decoration: none;
            font-weight: bold;
            width: 40%;
            aspect-ratio: 1;
            margin: 8rem 10px;
            display: inline-block;
            font-size: 8vw;
        }}

        .buttonON {{
            background-color: #4CAF50;
        }}

        .buttonOFF {{
            background-color: #f44336;
        }}
    </style>
</head>

<body>
    <h1>Raspberry Pi Pico W Server</h1>
    <p>Welcome to this Raspberry Pi Pico Server <strong>asynchronously</strong> deployed on the network {network}</p>
    <p>Control the onboard LED by clicking on the buttons below</p>
    <button class="buttonON">ON</button>
    <button class="buttonOFF">OFF</button>
    <script>
        document.getElementsByClassName('buttonON')[0].addEventListener('click', async function () {{ fetch('http://{addr}/led=on', {{ method: "POST", headers: {{}} }}); }});
        document.getElementsByClassName('buttonOFF')[0].addEventListener('click', async function () {{ fetch('http://{addr}/led=off', {{ method: "POST", headers: {{}} }}); }});
    </script>
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
        global html
        html = html.format(network=SSID, addr=wlan.ifconfig()[0])
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

    response = html

    request = str(request)
    if request.find('led=on') > 0:
        led.value(1)
        print('LED ON')
    elif request.find('led=off') > 0:
        led.value(0)
        print('LED OFF')

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
