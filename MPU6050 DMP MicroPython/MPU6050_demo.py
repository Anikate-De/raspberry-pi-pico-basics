from MPU6050RPI import MPU6050
from machine import I2C, Pin, PWM

device_address = 0x68

# The offsets are different for each device and should be changed
# accordingly using a calibration procedure
x_accel_offset = 1340 # -150 # 1340
y_accel_offset = -150 # 1447 # -150
z_accel_offset =  3085 # -150 # 3085
x_gyro_offset = 110 # 86
y_gyro_offset = 28 # 19
z_gyro_offset = 9 # 74
enable_debug_output = True

led_pitch = PWM(Pin(0))
led_pitch.freq(100)

led_roll = PWM(Pin(6))
led_roll.freq(100)

led_yaw = PWM(Pin(10))
led_yaw.freq(100)

i2c = I2C(1, scl = Pin(27), sda = Pin(26), freq=400000)
mpu = MPU6050(i2c, device_address, x_accel_offset, y_accel_offset,
              z_accel_offset, x_gyro_offset, y_gyro_offset, z_gyro_offset,
              enable_debug_output)


def rangify(value):
    init_start = -15
    init_end = 15

    if value < init_start:
        value = init_start
    elif value > init_end:
        value = init_end

    final_start = 0 # 2293
    final_end = 65535 #6553

    init_range = init_end - init_start
    final_range = final_end - final_start

    ratio = final_range / init_range

    distance = value - init_start
    new_value = distance * ratio + final_start

    return int(new_value)

mpu.dmp_initialize()
mpu.set_DMP_enabled(True)
mpu_int_status = mpu.get_int_status()

packet_size = mpu.DMP_get_FIFO_packet_size()
FIFO_count = mpu.get_FIFO_count()

FIFO_buffer = [0]*64

FIFO_count_list = list()
while True:
    FIFO_count = mpu.get_FIFO_count()
    mpu_int_status = mpu.get_int_status()

    # If overflow is detected by status or fifo count we want to reset
    if (FIFO_count == 1024) or (mpu_int_status & 0x10):
        mpu.reset_FIFO()
        #print('overflow!')
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
        print(int(roll_pitch_yaw.x), int(roll_pitch_yaw.y), int(roll_pitch_yaw.z), sep='\t')
        
        led_roll.duty_u16(int(rangify(roll_pitch_yaw.x)))
        led_pitch.duty_u16(int(rangify(roll_pitch_yaw.y)))
        led_yaw.duty_u16(int(rangify(roll_pitch_yaw.z)))


