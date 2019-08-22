#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import sys
import psycopg2
import lib_sys

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BOARD)
except Exception:
    print('Error init GPIO')
    sys.exit(1)


def sen_handler(channel):
    state = bool(GPIO.input(channel))
    time.sleep(2)
    if bool(GPIO.input(channel)) != state:
        return
    lib_sys.in_log('Handler for sensor pin: {0}'.format(channel), debug=True)
    try:
        cursor = ssy_con.cursor()
        cursor.execute('''UPDATE "sensors" SET "update" = TRUE WHERE "source" = 'pin {0}' AND "enable" = TRUE AND
                       "update" = FALSE'''.format(channel))
        cursor.close()
    except Exception:
        lib_sys.in_log('Error query in sen_handler for pin: {0}'.format(channel))
        return False


def trigger_handler(channel):
    state = not bool(GPIO.input(channel))
    time.sleep(2)
    if not bool(GPIO.input(channel)) != state:
        return
    lib_sys.in_log('Handler for trigger pin: {0} state: {1}'.format(channel, state), debug=True)
    try:
        cursor = ssy_con.cursor()
        cursor.execute('''INSERT INTO "trig_act" ("trig", "value")
                       VALUES ( (SELECT "ID" FROM "trig" WHERE "source" = 'pin {0}'), '{1}') '''
                       .format(channel, state))
        cursor.close()
        return True
    except Exception:
        lib_sys.in_log('Error query in trigger_handler for pin: {0}'.format(channel))
        return False


def init():

    global config
    lib_sys.init('smartsys_gpio.log')
    config = lib_sys.config
    lib_sys.in_log('Start')
    try:
        global ssy_con
        ssy_con = psycopg2.connect(host=config['BD']['smartsys']['host'], port=config['BD']['smartsys']['port'], dbname=config['BD']['smartsys']['dbname'], user=config['BD']['smartsys']['user'], password=config['BD']['smartsys']['password'])
        ssy_con.autocommit = True
        cursor = ssy_con.cursor()
    except Exception:
        lib_sys.in_log('Error opening the smartsys database in init')
        return False
    try:
        cursor.execute('''SELECT "name", "source", "type" FROM "sensors" WHERE "source" LIKE 'pin %' ''')
    except Exception:
        lib_sys.in_log('Error query in init, sensors')
        return False
    if cursor.rowcount > 0:
        res_query = cursor.fetchall()
        for sensor in res_query:
            pin = int(sensor[1][4:])
            if not pin in config['sys']['pins']:
                lib_sys.in_log('Invalid sensor number for sen: {0} pin: {1} type: {2}'.format(sensor[0],pin,sensor[2]))
                continue
            try:
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                if sensor[2] == 'rising': GPIO.add_event_detect(pin, GPIO.RISING)
                elif sensor[2] == 'falling': GPIO.add_event_detect(pin, GPIO.FALLING)
                elif sensor[2] == 'both': GPIO.add_event_detect(pin, GPIO.BOTH)
                else:
                    GPIO.cleanup(pin)
                    lib_sys.in_log('Invalid sensor type for sen: {0} pin: {1} type: {2}'.format(sensor[0], pin, sensor[1]))
                    continue
                GPIO.add_event_callback(pin, sen_handler)
                lib_sys.in_log('Set handler for sen: {0} pin: {1} type: {2}'.format(sensor[0], pin, sensor[2]))
            except Exception:
                lib_sys.in_log('Error ISR init on pin: {0}'.format(pin))
                return False
    try:
        cursor.execute('''SELECT "name", "source" FROM "trig" WHERE "source" LIKE 'pin %' ''')
    except Exception:
        lib_sys.in_log('Error query in init, triggers')
        return False
    if cursor.rowcount > 0:
        res_query = cursor.fetchall()
        for trigger in res_query:
            pin = int(trigger[1][4:])
            if not pin in config['sys']['pins']:
                lib_sys.in_log('Invalid trigger number for trigger: {0} pin: {1}'.format(trigger[0], pin))
                continue
            try:
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                GPIO.add_event_detect(pin, GPIO.BOTH)
                GPIO.add_event_callback(pin, trigger_handler)
            except Exception:
                lib_sys.in_log('Error ISR init on pin: {0}'.format(pin))
                return False
            lib_sys.in_log('Set handler for trigger: {0} pin: {1}'.format(trigger[0], pin))
    cursor.close()
    if lib_sys.test_state:
        GPIO.setup(18, GPIO.OUT, initial=0)
        while not lib_sys.close_triger:
            test_in = input('Enter code: ')
            if len(test_in) == 0: test_in = '_'
            test_in = test_in.split()
            if len(test_in) == 1 and test_in[0] == 'stop':
                lib_sys.close()
            if len(test_in) == 1 and test_in[0] == 'test_up':
                GPIO.output(18, 1)
            if len(test_in) == 1 and test_in[0] == 'test_down':
                GPIO.output(18, 0)
    else:
        while not lib_sys.close_triger:
            time.sleep(30)
    try:
        ssy_con.close()
    except Exception:
        lib_sys.in_log('Error while closing smartsys database')
    try:
        GPIO.cleanup()
    except Exception:
        lib_sys.in_log('Error while cleanup GPIO')
    lib_sys.close()


init()