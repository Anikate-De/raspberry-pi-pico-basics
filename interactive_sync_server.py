import socket
import time

import network
from machine import Pin

SSID = 'Shubho'
PASSWORD = '12156891'

led = Pin('LED', Pin.OUT)

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


html = '''
<html>
<body>
<h1>Raspberry Pi Pico W Server</h1>
<p>Welcome to this Raspberry Pi Pico Server deployed on the network {}</p>
<p>Control the onboard LED by clicking on the buttons below</p>
<button onclick="window.location.href = '/led=on';" {}>ON</button>
<button onclick="window.location.href = '/led=off';" {}>OFF</button>
</body>
</html>
'''

address = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(address)
s.listen(1)

print('Listening on', address)

while True:
    try:
        client, address = s.accept()
        print('Client connected from', address)

        request = client.recv(64)
        print('Request is', request)
        request = str(request)

        response = html.format(SSID, 'disabled', '')

        if request.find('led=on') > 0:
            led.value(1)
            response = html.format(SSID, 'disabled', '')
            print('LED ON')
        elif request.find('led=off') > 0:
            led.value(0)
            response = html.format(SSID, '', 'disabled')
            print('LED OFF')

        cl_file = client.makefile('rwb', 0)
        while True:
            line = cl_file.readline()
            if not line or line == b'\r\n':
                break

        client.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        client.send(response)
        client.close()

    except OSError as e:
        client.close()
        print('Connection closed')
