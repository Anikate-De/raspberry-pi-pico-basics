import time

import network
import uasyncio
from machine import PWM, Pin
from gpio_lcd import GpioLcd

SSID = 'Uday Karthikeya'
PASSWORD = '87654321'

onboard = Pin('LED', Pin.OUT)

text = 'started'
 
# Create the LCD object
lcd = GpioLcd(rs_pin=Pin(8),
              enable_pin=Pin(9),
              d4_pin=Pin(10),
              d5_pin=Pin(11),
              d6_pin=Pin(12),
              d7_pin=Pin(13),
              num_lines=2, num_columns=16)

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
    <input type="text" name="LCD Content" id="lcd-content">
    <input type="button" value="Submit" id="submit">
    <script>
        document.getElementById('submit').addEventListener('click', (function () {{
            fetch("http://{addr}/lcd=" + document.getElementById('lcd-content').value, {{ method: 'POST', headers: {{}} }});
        }}));
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
    index = request.find('lcd=')
    indexEnd = request.find('HTTP')
    value = request[index + 4:indexEnd]
    

    if index == -1 and indexEnd == -1:
        value = 0

    print('Value:', value)

    global text
    text = value.replace("%20"," ")
    lcd.clear()
    lcd.putstr(str(text))

    writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    writer.write(response)
    await writer.drain()
    await writer.wait_closed()


async def main():
    connect()

    print('Starting server...')
    uasyncio.create_task(uasyncio.start_server(serve, '0.0.0.0', 80))
    global text
    while True:
        # lcd.putstr(str(text))
        await uasyncio.sleep(0.0001)
        # lcd.clear()5

        


try:
    uasyncio.run(main())
    # while True:
    #     led.duty_u16(int(duty * 650.25))
    #     print('Duty:', duty)
    #     time.sleep(0.1)
finally:
    uasyncio.new_event_loop()

