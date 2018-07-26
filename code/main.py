import logging
from json import load
from os.path import isdir
from time import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def get_setting(arg_setting_name, arg_settings):
    if arg_setting_name in arg_settings.keys():
        result = arg_settings[arg_setting_name]
        return result
    else:
        logger.warning('required key %s is not in the settings. Quitting.' % arg_setting_name)
        quit()


def check_exists(arg_folder_name, arg_descriptor):
    folder_exists = isdir(arg_folder_name)
    if folder_exists:
        logger.debug('using %s as the %s folder' % (arg_folder_name, arg_descriptor))
    else:
        logger.warning('%s %s does not exist. Quitting.' % (arg_descriptor, arg_folder_name))
        quit()


def get_latitude(arg_field):
    int_field = int(arg_field[:8])
    direction = arg_field[8]
    result = float(int_field) * 1e-6
    if direction == 'S':
        result *= -1.0
    return result


def get_longitude(arg_field):
    int_field = int(arg_field[9:-1])
    direction = arg_field[-1]
    result = float(int_field) * 1e-6
    if direction == 'W':
        result *= -1.0
    return result


if __name__ == '__main__':
    start_time = time()

    formatter = logging.Formatter('%(asctime)s : %(name)s :: %(levelname)s : %(message)s')
    logger = logging.getLogger('main')
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    console_handler.setLevel(logging.DEBUG)
    logger.debug('started')

    with open('./settings-main.json') as settings_fp:
        settings = load(settings_fp)
        logger.debug(settings)

    input_folder = get_setting('input_folder', settings)
    check_exists(input_folder, 'input')
    input_file = get_setting('input_file', settings)
    full_input_file = input_folder + input_file
    logger.debug('loading data from input file %s' % full_input_file)
    skiprows = get_setting('skiprows', settings)
    separator = get_setting('separator', settings)
    data = pd.read_csv(full_input_file, sep=separator, skiprows=skiprows)
    logger.debug(data.shape)
    for index, item in enumerate(list(data)):
        logger.debug('%d : %s' % (index, item))
    logger.debug(data.head(10))

    columns_of_interest = get_setting('columns_of_interest', settings)
    subset = data[columns_of_interest]
    logger.debug(subset.shape)
    location_id = get_setting('location_id', settings)
    subset = subset[~subset[location_id].isnull()]
    logger.debug(subset.shape)
    subset['latitude'] = subset[location_id].apply(get_latitude)
    subset['longitude'] = subset[location_id].apply(get_longitude)
    logger.debug(subset.head(10))

    subset.plot.scatter('longitude', 'latitude')
    output_folder = get_setting('output_folder', settings)
    output_file = 'geolocations.png'
    full_output_file = output_folder + output_file
    logger.debug('writing to %s' % full_output_file)
    plt.savefig(full_output_file)

    logger.debug('done')
    finish_time = time()
    elapsed_hours, elapsed_remainder = divmod(finish_time - start_time, 3600)
    elapsed_minutes, elapsed_seconds = divmod(elapsed_remainder, 60)
    logger.info("Time: {:0>2}:{:0>2}:{:05.2f}".format(int(elapsed_hours), int(elapsed_minutes), elapsed_seconds))
    console_handler.close()
    logger.removeHandler(console_handler)
