from math import atan, pi, sqrt
from time import sleep

from machine import I2C, PWM, Pin

from imu import MPU6050

i2c = I2C(1, sda=Pin(26), scl=Pin(27), freq=400000)
imu = MPU6050(i2c)

esc_pitch = PWM(Pin(5))
esc_pitch.freq(50)

esc_roll = PWM(Pin(13))
esc_roll.freq(50)

gx_cal = 0
gy_cal = 0
gz_cal = 0

kalman_angle_roll = 0
kalman_uncertainty_angle_roll = 4

kalman_angle_pitch = 0
kalman_uncertainty_angle_pitch = 4

kalman_1d_output = [0, 0]

duty = 0


def calculateAngles(ax, ay, az):
    angle_roll = atan(ay/sqrt(ax**2 + az**2)) * (180 / pi)
    angle_pitch = -atan(ax/sqrt(ay**2 + az**2)) * (180 / pi)
    return angle_roll, angle_pitch


def calibrateGyro():
    global gx_cal, gy_cal, gz_cal

    gyro_cal_count = 1000

    for i in range(gyro_cal_count):
        print("Calibrating gyroscope...", i, end="\r")

        gx_cal += imu.gyro.x
        gy_cal += imu.gyro.y
        gz_cal += imu.gyro.z

        sleep(0.001)  # sleep for 10ms

    gx_cal /= gyro_cal_count
    gy_cal /= gyro_cal_count
    gz_cal /= gyro_cal_count

    print("Gyroscope calibration complete! :", gx_cal, gy_cal, gz_cal)

    input("Press any key then enter to start...")


def kalman_1d(kalman_state, kalman_uncertainty, kalman_input, kalman_measurement):
    global kalman_1d_output

    kalman_state += (0.004 * kalman_input)
    kalman_uncertainty += ((0.004 ** 2) * (8**2))
    kalman_gain = kalman_uncertainty * 1 / (1 * kalman_uncertainty + 3 * 3)
    kalman_state += kalman_gain * (kalman_measurement - kalman_state)
    kalman_uncertainty *= (1 - kalman_gain)

    kalman_1d_output[0] = kalman_state
    kalman_1d_output[1] = kalman_uncertainty


def rangify(value):
    init_start = -45
    init_end = 45

    final_start = 3700  # 2293
    final_end = 4200  # 6553

    init_range = init_end - init_start
    final_range = final_end - final_start

    ratio = final_range / init_range

    distance = value - init_start
    new_value = distance * ratio + final_start

    return int(new_value)


if __name__ == "__main__":

    calibrateGyro()

    while True:

        ax = imu.accel.x - 0.06  # calibration
        ay = imu.accel.y + 0.01  # calibration
        az = imu.accel.z + 0.116  # calibration

        gx = imu.gyro.x - gx_cal
        gy = imu.gyro.y - gy_cal
        gz = imu.gyro.z - gz_cal

        tem = imu.temperature

        roll, pitch = calculateAngles(ax, ay, az)

        kalman_1d(kalman_angle_roll, kalman_uncertainty_angle_roll, gx, roll)
        kalman_angle_roll = kalman_1d_output[0]
        kalman_uncertainty_angle_roll = kalman_1d_output[1]

        kalman_1d(kalman_angle_pitch,
                  kalman_uncertainty_angle_pitch, gy, pitch)
        kalman_angle_pitch = kalman_1d_output[0]
        kalman_uncertainty_angle_pitch = kalman_1d_output[1]

        print("Roll:", kalman_angle_roll, "Pitch:", kalman_angle_pitch)

        if kalman_angle_pitch < -15:
            duty = 0
        elif kalman_angle_pitch > 15:
            duty = 65535
        else:
            duty = rangify(kalman_angle_pitch)

        esc_pitch.duty_u16(duty)

        if kalman_angle_roll < -15:
            duty = 0
        elif kalman_angle_roll > 15:
            duty = 65535
        else:
            duty = rangify(kalman_angle_roll)

        esc_roll.duty_u16(duty)
