'''
This program receives gyroscopic input from the MPU6050 controller and simulates 
the functionality of a BLDC motor by varying the duty cycle of two LEDs connected
'''

from time import sleep

from machine import I2C, PWM, Pin

from imu import MPU6050

i2c = I2C(1, sda=Pin(26), scl=Pin(27), freq=400000)
imu = MPU6050(i2c)

# This LED (Left) simulates the functionality of a clock-wise spinning BLDC motor
led_l = PWM(Pin(14))
led_l.freq(1000)

# This LED (right) simulates the functionality of an anticlock-wise spinning BLDC motor
led_r = PWM(Pin(15))
led_r.freq(1000)

# Above motors are connected via an ESC each

duty_l = 0.5
duty_r = 0.5

while True:
    gy = round(imu.gyro.y)
    duty_delta_l = gy / 500
    led_l.duty_u16(int((duty_delta_l + duty_l) * 65535))

    duty_delta_r = - gy / 500
    led_r.duty_u16(int((duty_delta_r + duty_r) * 65535))

    print("Left LED Duty:", (duty_delta_l + duty_l),
          "\t Right LED Duty:", (duty_delta_r + duty_r))
    sleep(0.1)
