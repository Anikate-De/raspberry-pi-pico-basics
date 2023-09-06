from machine import PWM, Pin

esc_a, esc_b = PWM(Pin(0)), PWM(Pin(6))

esc_a.freq(50)
esc_b.freq(50)


def rangify(value):
    init_start = 0
    init_end = 65535

    final_start = 3700  # 2293
    final_end = 4200  # 6553

    init_range = init_end - init_start
    final_range = final_end - final_start

    ratio = final_range / init_range

    distance = value - init_start
    new_value = distance * ratio + final_start

    return int(new_value)

while True:
    duty = int(input('Enter duty cycle (in ms): ')) * 1000
    esc_a.duty_ns(duty)
    esc_b.duty_ns(duty + 35000)
    print("Duty value: (in ns)", duty)
    