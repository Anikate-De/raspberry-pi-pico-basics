from machine import I2C, PWM, Pin
from MPU6050RPI import MPU6050
from utime import sleep

ESC_START = 3700
ESC_END = 4200

device_address = 0x68

# The offsets are different for each device and should be changed
# accordingly using a calibration procedure
x_accel_offset = 1340  # -150 # 1340
y_accel_offset = -150  # 1447 # -150
z_accel_offset = 3085  # -150 # 3085
x_gyro_offset = 110  # 86
y_gyro_offset = 28  # 19
z_gyro_offset = 9  # 74
enable_debug_output = True

esc_cw = PWM(Pin(0))
esc_cw.freq(50)

esc_acw = PWM(Pin(6))
esc_acw.freq(50)


i2c = I2C(1, scl=Pin(27), sda=Pin(26), freq=400000)
mpu = MPU6050(i2c, device_address, x_accel_offset, y_accel_offset,
              z_accel_offset, x_gyro_offset, y_gyro_offset, z_gyro_offset,
              enable_debug_output)

mpu.dmp_initialize()
mpu.set_DMP_enabled(True)
mpu_int_status = mpu.get_int_status()

packet_size = mpu.DMP_get_FIFO_packet_size()
FIFO_count = mpu.get_FIFO_count()

FIFO_buffer = [0]*64

FIFO_count_list = list()

duty_acw = 0.75
duty_cw = 0.75


def rangify(value, init_start=-15.0, init_end=15.0, final_start=0.0, final_end=65535.0):
    if value < init_start:
        value = init_start
    elif value > init_end:
        value = init_end

    init_range = init_end - init_start
    final_range = final_end - final_start

    ratio = final_range / init_range

    distance = value - init_start
    new_value = distance * ratio + final_start

    return new_value

def calibrate_escs(esc_start=ESC_START):
    print('Calibrating ESCs...')
    esc_cw.duty_u16(esc_start)
    esc_acw.duty_u16(esc_start)
    sleep(6)


def incrementally_start_esc(escs, end=4075, start=ESC_START):
    print('Slow starting ESCs to a duty level of', end, '...')

    for i in range(start, end, 1):
        for esc in escs:
            esc.duty_u16(i)

        print("ESC Duty:", i, end='\r')
        sleep(0.075)

    for esc in escs:
        esc.duty_u16(end)


calibrate_escs()
incrementally_start_esc(escs=[esc_cw, esc_acw])

while True:
    try:
        FIFO_count = mpu.get_FIFO_count()
        mpu_int_status = mpu.get_int_status()

        # If overflow is detected by status or fifo count we want to reset
        if (FIFO_count == 1024) or (mpu_int_status & 0x10):
            mpu.reset_FIFO()
            # print('overflow!')
        # Check if fifo data is ready
        elif (mpu_int_status & 0x02):
            # Wait until packet_size number of bytes are ready for reading, default
            # is 42 bytes
            while FIFO_count < packet_size:
                FIFO_count = mpu.get_FIFO_count()
            FIFO_buffer = mpu.get_FIFO_bytes(packet_size)
            accel = mpu.DMP_get_acceleration_int16(FIFO_buffer)
            quat = mpu.DMP_get_quaternion_int16(FIFO_buffer)
            grav = mpu.DMP_get_gravity(quat)
            roll_pitch_yaw = mpu.DMP_get_euler_roll_pitch_yaw(quat, grav)
            yaw = roll_pitch_yaw.z
            # print(int(roll_pitch_yaw.x), int(roll_pitch_yaw.y), int(yaw), sep='\t')

            duty_delta_acw = rangify(
                yaw, init_start=-30, init_end=30, final_start=-0.25, final_end=0.25)
            duty_acw_range = rangify(
                duty_delta_acw + duty_acw, init_start=0, init_end=1, final_start=0, final_end=65535)
            esc_acw.duty_u16(int(duty_acw_range))

            duty_delta_cw = rangify(-yaw, init_start=-30,
                                    init_end=30, final_start=-0.25, final_end=0.25)
            duty_cw_range = rangify(
                duty_delta_cw + duty_cw, init_start=0, init_end=1, final_start=ESC_START, final_end=4200)
            esc_cw.duty_u16(int(duty_cw_range))
            print("ESC CW Duty:", (duty_cw_range),
                  "\t ESC ACW Duty:", (duty_acw_range))

    except KeyboardInterrupt:
        break
    except:
        pass
