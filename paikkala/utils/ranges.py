def parse_number_set(number_set):
    return set(
        int(number)
            for number
            in number_set.split(',')
            if number and number.isdigit()
    )
