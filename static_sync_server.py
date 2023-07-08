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
<p>Server has been online for {} seconds</p>
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
        cl_file = client.makefile('rwb', 0)
        while True:
            line = cl_file.readline()
            if not line or line == b'\r\n':
                break

        response = html.format(SSID, time.ticks_cpu() // 1000000)
        
        client.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        client.send(response)
        client.close()


    except OSError as e:
        client.close()
        print('Connection closed')
    
