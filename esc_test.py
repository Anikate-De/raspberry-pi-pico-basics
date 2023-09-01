from machine import ADC, PWM, Pin

esc = PWM(Pin(0))
pot = ADC(26)

esc.freq(50)


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
    pot_val = pot.read_u16()
    duty = rangify(pot_val)
    print("Potentiometer value: ", pot_val, ' Duty: ', duty)
    esc.duty_u16(duty)
