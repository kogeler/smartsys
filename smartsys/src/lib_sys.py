import sys
import threading
import os
import signal
import yaml
import logging

# Глобальные переменные
close_triger = False
close_code_err = -1
close_init_lock = threading.RLock()


def init():
    global logger
    global config
    global test_state
    global msg_debug_state
    signal.signal(signal.SIGINT, close_handler)
    signal.signal(signal.SIGTERM, close_handler)
    signal.signal(signal.SIGHUP, close_handler)
    try:
        config = yaml.load(open(os.path.dirname(__file__) + '/config.yml'), Loader=yaml.FullLoader)
    except Exception:
        print('Error open config file!')
        close(1)
    test_state = config['sys']['test_mod']
    msg_debug_state = config['sys']['debug_msg_mod']


def setup_logger(logger):
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    if config['sys']['debug']:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logger.setLevel(log_level)
    formatter = logging.Formatter(log_format)
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    if config['sys']['log_path']:
        fh = logging.FileHandler(os.path.join(config['sys']['log_path'], logger.name + '.log'))
        fh.setFormatter(formatter)
        logger.addHandler(fh)

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
        logger.error('Stop with code: {0}'.format(exit_code))
    except Exception:
        pass
    print(f'Stop with code: {exit_code}')
    sys.exit(exit_code)
