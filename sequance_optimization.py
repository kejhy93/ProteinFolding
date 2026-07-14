#! /usr/bin/python3

def check_valid_index(index, sequance):
    # Check if index is in valid range
    # Return True if index < 0 ; len(sequance)-1 >
    if 0 <= index <= len(sequance) - 1:
        return True
    else:
        return False


def check_hydropholic(amino):
    # Check if amino is hydropholic ( =0 )
    if amino == 0:
        return True
    else:
        return False


def get_first_position(sequance):
    counter = 0
    while check_valid_index(counter, sequance) and check_hydropholic(sequance[counter]):
        counter += 1

    return counter


def get_last_position(sequance):
    counter = len(sequance) - 1
    while check_valid_index(counter, sequance) and check_hydropholic(sequance[counter]):
        counter -= 1

    return counter + 1;


def optimize_sequance(sequance):
    counter_from_begin = get_first_position(sequance)
    counter_from_end = get_last_position(sequance)

    if counter_from_begin > counter_from_end:
        return []

    return sequance[counter_from_begin:counter_from_end]
