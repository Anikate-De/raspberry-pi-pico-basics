def rangify(value, init_start, init_end, final_start=0.0, final_end=65535.0):
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

    