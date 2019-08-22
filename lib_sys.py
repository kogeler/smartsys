import sys
import threading
import time
import os
import signal
import yaml

# Глобальные переменные
close_triger = False
close_code_err = -1
close_init_lock = threading.RLock()
log_lock = threading.RLock()


def init(log_name):
    global log_file
    global config
    global debug_state
    global test_state
    global msg_debug_state
    signal.signal(signal.SIGINT, close_handler)
    signal.signal(signal.SIGTERM, close_handler)
    signal.signal(signal.SIGHUP, close_handler)
    try:
        config = yaml.load(open(os.path.dirname(__file__) + '/config.yml'))
    except Exception:
        print('Error open config file!')
        close(1)
    debug_state = bool(int(config['sys']['debug_mod']))
    test_state = bool(int(config['sys']['test_mod']))
    msg_debug_state = bool(int(config['sys']['debug_msg_mod']))
    try:
        log_file = open(config['sys']['log_path'] + log_name, 'a')
    except Exception:
        print('Error open log file!')
        close(1)


# Обработчик сигнала закрытия
def close_handler(signum, frame):
    close_init()


# Инициализация процесса завершения
def close_init(err_code=0):
    global close_triger, close_code_err
    close_init_lock.acquire()
    if close_code_err == -1: close_code_err = err_code
    close_triger = True
    close_init_lock.release()


# Завершение программы с определением кода выхода
def close(close_code=-1):
    if close_code == -1:
        if close_code_err == -1:
            exit_code = 0
        else:
            exit_code = close_code_err
    else:
        exit_code = close_code
    try:
        in_log('Stop with code: {0}'.format(exit_code))
        log_file.close()
    except Exception:
        pass
    sys.exit(exit_code)


def in_log(mess, debug=False):
    if debug:
        mess = '(DEBUG) {0}'.format(mess)
    else:
        mess = '(LOG) {0}'.format(mess)
    if test_state: print(mess)
    if (not debug) or (debug and debug_state):
        now_time = time.strftime('%Y.%m.%d %H:%M:%S', time.localtime())
        try:
            log_lock.acquire()
            log_file.write('{0}	{1}\n'.format(now_time, mess))
            log_file.flush()
            log_lock.release()
        except Exception:
            print('Error write in log file!')
            close(1)
    return True