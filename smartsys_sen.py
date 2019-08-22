#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import time
import lib_sys
import lib_db

import smbus2
import bme280


def init():
    global config
    lib_sys.init('smartsys_sen.log')
    config = lib_sys.config
    lib_sys.in_log('Start')
    lib_db.close = lib_sys.close
    lib_db.close_init = lib_sys.close_init
    lib_db.in_log = lib_sys.in_log
    lib_db.db_init()
    global i2c_bus
    try:
        i2c_bus = smbus2.SMBus(int(config['i2c']['port']))
        bme280.load_calibration_params(i2c_bus, int(config['i2c']['pt'][1]))
    except Exception:
        lib_sys.in_log('Error opening i2c port in init')
        lib_sys.close(3)
    read_thread = threading.Thread(target=read_th)
    read_thread.start()
    if lib_sys.test_state:
        test_thread = threading.Thread(target=test_th)
        test_thread.start()
        test_thread.join()
    read_thread.join()
    try:
        i2c_bus.close()
    except Exception:
        lib_sys.in_log('Error while closing i2c port')
    lib_db.db_close()
    lib_sys.close()


def read_th():
    timer_c = 0
    per = 600
    while not lib_sys.close_triger:
        time.sleep(1)
        if timer_c < per:
            timer_c = timer_c + 1
            continue
        timer_c = 0
        data = bme280.sample(i2c_bus, int(config['i2c']['pt'][1]))
        temperature = round(data.temperature, 1)
        humidity = round(data.humidity, 1)
        pressure = round(data.pressure * 0.75006375541921, 1)
        print(temperature, humidity, pressure)
        if not lib_db.db_wr_query('''INSERT INTO "value_thp"
                           ("point", "temp", "humidity", "pressure")
                           VALUES ('{0}', '{1}', '{2}', '{3}') '''
                           .format(1, temperature, humidity, pressure)): continue
    return True


def test_th():
    while not lib_sys.close_triger:
        test_in = input('Enter code: ')
        if len(test_in) == 0: test_in = '_'
        test_in = test_in.split()
        if len(test_in) == 1 and test_in[0] == 'stop':
            lib_sys.close_init()
        elif len(test_in) == 1 and test_in[0] == 'test':
            print('test')
    lib_sys.in_log('TH: normal exit on test_th')
    return True


init()


