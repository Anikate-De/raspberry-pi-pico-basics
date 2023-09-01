import time

import network
import uasyncio
from machine import PWM, Pin

SSID = 'Shubho'
PASSWORD = '12156891'

onboard = Pin('LED', Pin.OUT)

led = PWM(Pin(0))
duty = 0

led.freq(1000)
led.duty_u16(duty)

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

        .slider {{
            width: 100%;
            height: 15px;
            border-radius: 5px;
            background: #d3d3d3;
            outline: none;
            opacity: 0.7;
            transition: opacity .2s;
        }}
    </style>
</head>

<body>
    <h1>Raspberry Pi Pico W Server</h1>
    <p>Welcome to this Raspberry Pi Pico Server <strong>asynchronously</strong> deployed on the network {network}</p>
    <p>This server simulates the working of a potentiometer using controls in a web application</p>
    <p>Drag the slider below to adjust the brightness of the LED</p>
    <input type="range" min="1" max="100" value="50" class="slider" id="potentiometer">
    <p>Value: <span id="value"></span></p>
    <script>
        var slider = document.getElementById("potentiometer");
        var output = document.getElementById("value");

        output.innerHTML = slider.value;
        slider.oninput = async function () {{
             output.innerHTML = String(this.value).padStart(3, '0');
            fetch('http://{addr}/led=' + String(this.value).padStart(3, '0'), {{method: 'POST', headers: {{}}}});
        }}
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
        onboard.toggle()
        print('Connecting to network...')

    if wlan.isconnected():
        print('Connected to network', SSID)

        # Print network information
        print('Network config:', wlan.ifconfig())
        onboard.value(1)
        global html
        html = html.format(network=SSID, addr=wlan.ifconfig()[0])
    else:
        print('Connection failed to network', SSID)
        onboard.value(0)


async def serve(reader, writer):

    request = await reader.readline()

    while True:
        line = await reader.readline()
        if not line or line == b'\r\n':
            break

    response = html

    request = str(request)
    index = request.find('led=')
    value = request[index + 4:index + 7]

    if index == -1:
        value = 0

    print('Value:', value)
    value = int(value)

    global duty
    duty = value

    writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    writer.write(response)
    await writer.drain()
    await writer.wait_closed()


async def main():
    connect()

    print('Starting server...')
    uasyncio.create_task(uasyncio.start_server(serve, '0.0.0.0', 80))
    global duty
    while True:
        led.duty_u16(int(duty * 650.25))
        await uasyncio.sleep(0.0001)


try:
    uasyncio.run(main())
    # while True:
    #     led.duty_u16(int(duty * 650.25))
    #     print('Duty:', duty)
    #     time.sleep(0.1)
finally:
    uasyncio.new_event_loop()
