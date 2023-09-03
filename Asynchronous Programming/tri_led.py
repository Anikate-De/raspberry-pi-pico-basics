import uasyncio
from machine import Pin


async def blink(led, period_ms):
    while True:
        led.toggle()
        await uasyncio.sleep_ms(period_ms)


async def main(led1, led2, led3):
    uasyncio.create_task(blink(led1, 500))
    uasyncio.create_task(blink(led2, 1000))
    uasyncio.create_task(blink(led3, 2000))
    while True:
        await uasyncio.sleep(0)

uasyncio.run(main(Pin(0, Pin.OUT), Pin(6, Pin.OUT), Pin(10, Pin.OUT)))
