import time

import network
from machine import Pin

SSID = 'Shubho'
PASSWORD = '12156891'

wlan = network.WLAN(network.STA_IF)
led = Pin('LED', Pin.OUT)

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
    wlan.disconnect()