#! /usr/bin/python3 

import os
import re
import time

from data.data import Data
from data.vector import Vector

INCREASE = 1
DECREASE = 0

RESULT_FOLDER = "result"


def parse(PATH):
    content_of_test_file = ""

    with open(PATH, 'r', encoding="utf-8") as f:
        content_of_test_file = f.read()

    parsed_content = content_of_test_file.split()

    test_set = []
    counter = 0
    for line in parsed_content:
        parsed_line = []
        for number in line:
            parsed_line.append(int(number))

        data = Data(parsed_line, counter)
        test_set.append(data)
        counter += 1

    return test_set


def zero_or_one(number):
    if number == "1":
        return 1
    else:
        return 0


def sort(test_set, STYLE):
    """
    Sort by selection sort
    """
    count_of_sorted = 0

    comparator = None
    if STYLE == DECREASE:
        comparator = is_first_lower
    elif STYLE == INCREASE:
        comparator = is_first_higher

    for index in range(len(test_set) - 1, 0, -1):
        lowest_index = 0
        for find_index in range(1, index + 1):
            if comparator(test_set[find_index].get_count_of_hydro(), test_set[lowest_index].get_count_of_hydro()):
                lowest_index = find_index

        tmp = test_set[index]
        test_set[index] = test_set[lowest_index]
        test_set[lowest_index] = tmp

        count_of_sorted += 1

    return test_set


def is_first_lower(first, second):
    if first < second:
        return True
    else:
        return False


def is_first_higher(first, second):
    if first > second:
        return True
    else:
        return False


def create_index(index):
    if index < 10:
        indexStr = "00" + str(index)
    elif index < 100:
        indexStr = "0" + str(index)
    else:
        indexStr = str(index)

    return indexStr


def create_filename(index):
    name = "file_" + create_index(index)

    return name


def append_to_file(configuration, free_energy, index):
    path_to_file = os.path.join(RESULT_FOLDER, create_filename(index))

    if not os.path.exists(RESULT_FOLDER):
        os.makedirs(RESULT_FOLDER)

    content_to_write = str(free_energy) + " " + str(configuration.get_configuration()) + "\n"

    if not os.path.exists(path_to_file):
        with open(path_to_file, 'w', encoding='utf-8') as f:
            f.write(content_to_write)
    else:
        with open(path_to_file, 'a', encoding='utf-8') as f:
            f.write(content_to_write)


def create_filesize_set(test_files):
    filesize_set = []
    for test_file in test_files:
        content_of_file = ""
        filename = os.path.join(RESULT_FOLDER, create_filename(test_file.get_counter()))

        if not os.path.exists(RESULT_FOLDER):
            filesize_set.append(0)
        elif not os.path.exists(filename):
            filesize_set.append(0)
        else:
            with open(filename, 'r', encoding='utf-8') as f:
                content_of_file = f.read()

            splited_file = content_of_file.split("\n")
            filesize_set.append(len(splited_file))

    return filesize_set


def sort_by_size_of_result_file(TEST_SET, FILE_SIZE_SET):
    comparator = is_first_higher

    for index in range(len(TEST_SET) - 1, 0, -1):
        lowest_index = 0
        for find_index in range(1, index + 1):
            if comparator(FILE_SIZE_SET[find_index], FILE_SIZE_SET[lowest_index]):
                lowest_index = find_index

        tmp = TEST_SET[index]
        TEST_SET[index] = TEST_SET[lowest_index]
        TEST_SET[lowest_index] = tmp

        tmp = FILE_SIZE_SET[index]
        FILE_SIZE_SET[index] = FILE_SIZE_SET[lowest_index]
        FILE_SIZE_SET[lowest_index] = tmp

    return TEST_SET


def sort_by_test_size(TEST_FILE):
    file_size_set = create_filesize_set(TEST_FILE)

    TEST_FILE = sort_by_size_of_result_file(TEST_FILE, file_size_set)

    return TEST_FILE


def get_time_in_millis():
    return int(round(time.time() * 1000))


def millis_to_second(time_in_millis):
    return time_in_millis / 1000


def get_string_of_computed_times(start_times, end_times, methods):
    string_time = ""

    max_length_of_methods = 0
    for method in methods:
        if len(method) > max_length_of_methods:
            max_length_of_methods = len(method)

    max_length_of_methods += 2
    format_string = "Time in {:" + str(max_length_of_methods) + "} {:5.3f} sec\n"

    for start, end, method in zip(start_times, end_times, methods):
        string_time += format_string.format(method, millis_to_second(end - start))

    return string_time


def find_min_value_in(content):
    min_val = 1000000000000000000000

    split_content = content.split("\n")
    for line in split_content:
        if line != "":
            split_line = line.split()
            val = float(split_line[0])

            if val < min_val:
                min_val = val

    return min_val


def read_minimal_energy_from_file(ID):
    filename = create_filename(ID)

    fullpath_name = os.path.join(RESULT_FOLDER, filename)

    minimal_value = None

    if not os.path.exists(fullpath_name):
        return None
    else:
        content = ""
        with open(fullpath_name, 'r', encoding='utf-8') as f:
            content = f.read()

        minimal_value = find_min_value_in(content)

    return minimal_value


def read_configuration_history(path_to_file, amino_sequance):
    """
    Read history of configuration from file
    """
    history = []

    if not os.path.exists(path_to_file):
        return history

    content_of_file = ""
    with open(path_to_file, 'r', encoding='utf-8') as f:
        content_of_file = f.read()
    # print(content_of_file)

    history = parse_configuration_history(content_of_file, amino_sequance)

    # print(history)
    return history


def parse_configuration_history(content_of_file, amino_sequance):
    history = []
    splited_content_of_file = content_of_file.split("\n")

    for line in splited_content_of_file:
        vector = Vector(amino_sequance)
        line = re.sub('[\[,\]]', '', line)
        removed_free_energy = line.split()
        # print(removed_free_energy)

        for index in range(1, len(removed_free_energy)):
            vector.set_configuration_at_index(index - 1, complex(removed_free_energy[index]))

        history.append(vector)

    return history
