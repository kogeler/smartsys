#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import time
import lib_sys
import lib_sms
import lib_db

from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater
import telegram.error


def init():
    global config
    lib_sys.init('smartsys.log')
    config = lib_sys.config
    lib_sys.in_log('Start')
    lib_db.close = lib_sys.close
    lib_db.close_init = lib_sys.close_init
    lib_db.in_log = lib_sys.in_log
    lib_db.db_init()
    lib_sms.close = lib_sys.close
    lib_sms.close_init = lib_sys.close_init
    lib_sms.in_log = lib_sys.in_log
    lib_sms.sms_init()
    init_telegram()
    sms_in_thread = threading.Thread(target=sms_in_th)
    alarm_thread = threading.Thread(target=alarm_th)
    service_thread = threading.Thread(target=service_th)
    sms_in_thread.start()
    alarm_thread.start()
    service_thread.start()
    if lib_sys.test_state:
        test_thread = threading.Thread(target=test_th)
        test_thread.start()
        test_thread.join()
    sms_in_thread.join()
    alarm_thread.join()
    service_thread.join()
    close_telegram()
    lib_sms.sms_close()
    lib_db.db_close()
    lib_sys.close()

def init_telegram():
    global t_updater
    try:
        t_updater = Updater(token=config['sys']['tg_token'])
        handler = MessageHandler(Filters.text | Filters.command, t_message_handle)
        t_updater.dispatcher.add_handler(handler)
        t_updater.dispatcher.add_error_handler(t_error_handler)
        t_updater.start_polling()
    except Exception:
        lib_sys.in_log('TG: Error init telegram!')

def close_telegram():
    try:
        t_updater.dispatcher.stop()
        t_updater.stop()
    except Exception:
        lib_sys.in_log('TG: Error close telegram!')


def send_msg(text, *, to='all'):
    lib_sys.in_log('FUN: send msg with the text: "{0}" TO: "{1}"'.format(text, to), debug=True)
    if lib_sys.msg_debug_state and lib_sys.debug_state:
        return True
    if to == 'all':
        query, res_query = lib_db.db_query('''SELECT "type", "address" FROM "clients" WHERE 
                                    "state" = TRUE ''')
    elif to == 'force_all':
        query, res_query = lib_db.db_query('''SELECT "type", "address" FROM "clients" ''')
    else:
        query, res_query = lib_db.db_query('''SELECT "type", "address" FROM "clients" WHERE 
                                    "address" = '{0}' '''.format(to))
    if not query: return False
    for client in res_query:
        if client[0] == 'sms':
            if not lib_sms.send_sms(text, client[1]): return False
        elif client[0] == 'telegram':
            try:
                t_updater.bot.send_message(chat_id=client[1], text=text)
            except Exception:
                lib_sys.in_log('FUN: send error telegram msg with the text: "{0}" TO: "{1}"'.format(text, client[1]))
    return True


def msg_handler(msg, client):
    msg = msg.split()
    # Включить рассылку для всех
    if len(msg) == 3 and msg[0] == 'уведомления' and msg[1] == 'всем' and msg[2] == 'включить':
        lib_sys.in_log('Handler: set notification for all', debug=True)
        if lib_db.set_notif():
            return True, 'force_all', 'Включена рассылка для всех'
        else:
            return False, None, None
    # Выключить рассылку для всех
    elif len(msg) == 3 and msg[0] == 'уведомления' and msg[1] == 'всем' and msg[2] == 'выключить':
        lib_sys.in_log('Handler: unset notification for all', debug=True)
        if lib_db.unset_notif():
            return True, 'force_all', 'Выключена рассылка для всех'
        else:
            return False, None, None
    # Включить рассылку для одного клиента
    elif len(msg) == 3 and msg[0] == 'уведомления' and msg[1] == 'мне' and msg[2] == 'включить':
        lib_sys.in_log('Handler: set notification for: {0}'.format(client), debug=True)
        if lib_db.set_notif(client):
            return True, 'one', 'Для вас включена рассылка'
        else:
            return False, None, None
    # Выключить рассылку для одного сенсора
    elif len(msg) == 3 and msg[0] == 'уведомления' and msg[1] == 'мне' and msg[2] == 'выключить':
        lib_sys.in_log('Handler: unset notification for: {0}'.format(client), debug=True)
        if lib_db.unset_notif(client):
            return True, 'one', 'Для вас выключена рассылка'
        else:
            return False, None, None
    # Включить мотирониг всех сенсоров
    elif len(msg) == 3 and msg[0] == 'мониторинг' and msg[1] == 'всех' and msg[2] == 'включить':
        lib_sys.in_log('Handler: monitoring all on', debug=True)
        if lib_db.set_alarm():
            return True, 'all', 'Включен мотирониг всех сенсоров'
        else:
            return False, None, None
    # Выключить мотирониг всех сенсоров
    elif len(msg) == 3 and msg[0] == 'мониторинг' and msg[1] == 'всех' and msg[2] == 'выключить':
        lib_sys.in_log('Handler: monitoring all off', debug=True)
        if lib_db.unset_alarm():
            return True, 'all', 'Выключен мотирониг всех сенсоров'
        else:
            return False, None, None
    # Включить мониторинг одного сенсора
    elif len(msg) == 3 and msg[0] == 'мониторинг' and msg[1] != 'всех' and msg[2] == 'включить':
        query, res = lib_db.check_alarm(msg[1])
        if not query: return False, None, None
        if res:
            lib_sys.in_log('Handler: monitoring one {0} on'.format(msg[1]), debug=True)
            if lib_db.set_alarm(msg[1]):
                return True, 'all', 'Включен мониторинг сенсора: {0}'.format(msg[1])
            else:
                return False, None, None
        else:
            lib_sys.in_log('Handler: the {0} does not exist!'.format(msg[1]), debug=True)
            return True, 'one', 'Сенсор {0} несуществует!'.format(msg[1])
    # Выключить мониторинг одного сенсора
    elif len(msg) == 3 and msg[0] == 'мониторинг' and msg[1] != 'всех' and msg[2] == 'выключить':
        query, res = lib_db.check_alarm(msg[1])
        if not query: return False, None, None
        if res:
            lib_sys.in_log('Handler: monitoring one {0} off'.format(msg[1]), debug=True)
            if lib_db.unset_alarm(msg[1]):
                return True, 'all', 'Выключен мониторинг сенсора: {0}'.format(msg[1])
            else:
                return False, None, None
        else:
            lib_sys.in_log('Handler: the {0} does not exist!'.format(msg[1]), debug=True)
            return True, 'one', 'Сенсор {0} несуществует!'.format(msg[1])
    # Сброс всех сенсоров
    elif len(msg) == 2 and msg[0] == 'сбросить' and msg[1] == 'все':
        lib_sys.in_log('Handler: reset all', debug=True)
        if lib_db.reset_alarm():
            return True, 'all', 'Сброшены все сенсоры'
        else:
            return False, None, None
    # Сброс одного сенсора
    elif len(msg) == 2 and msg[0] == 'сбросить' and msg[1] != 'все':
        query, res = lib_db.check_alarm(msg[1])
        if not query: return False, None, None
        if res:
            lib_sys.in_log('Handler: reset one {0}'.format(msg[1]), debug=True)
            if lib_db.reset_alarm(msg[1]):
                return True, 'all', 'Сброшен сенсор: {0}'.format(msg[1])
            else:
                return False, None, None
        else:
            lib_sys.in_log('Handler: the {0} does not exist!'.format(msg[1]), debug=True)
            return True, 'one', 'Сенсор {0} несуществует!'.format(msg[1])
    # Запрор показаний одного датчика
    elif len(msg) == 2 and msg[0] == 'запросить':
        query, res = lib_db.check_point(msg[1])
        if not query: return False, None, None
        if res:
            lib_sys.in_log('Handler: get for {0}'.format(msg[1]), debug=True)
            query, res = lib_db.get_last(msg[1])
            if not query: return False, None, None
            return True, 'one', res
        else:
            lib_sys.in_log('Handler: the {0} does not exist!'.format(msg[1]), debug=True)
            return True, 'one', 'Датчик {0} не существует!'.format(msg[1])
    else:
        return True, None, None


def t_message_handle(bot, update):
    query, res = lib_db.check_client(update.message.chat_id)
    lib_sys.in_log('TG: Сhat id: {0} write: "{1}"'.format(update.message.chat_id, update.message.text), debug=True)
    if not query: return
    if not res:
        lib_sys.in_log('TG: Bad client: {0} write: "{1}"'.format(update.message.chat_id, update.message.text), debug=True)
        send_msg('Ты левак!', to=update.message.chat_id)
        return
    query, to, res = msg_handler(update.message.text, update.message.chat_id)
    if not query: return
    if res is not None:
        if to == 'all' or to == 'force_all':
            send_msg(res, to=to)
        elif to == 'one':
            send_msg(res, to=update.message.chat_id)
    else:
        send_msg('Неправильная команда!', to=update.message.chat_id)


def t_error_handler(Bot, Update, TelegramError):
    try:
        raise TelegramError
    except telegram.error.Unauthorized:
        lib_sys.in_log('TG: Unauthorized')
    except telegram.error.BadRequest:
        lib_sys.in_log('TG: BadRequest')
    except telegram.error.TimedOut:
        lib_sys.in_log('TG: TimedOut')
    except telegram.error.NetworkError:
        lib_sys.in_log('TG: NetworkError')
    except telegram.error.ChatMigrated as e:
        lib_sys.in_log('TG: the chat_id of a group has changed, use {0} instead'.format(e.new_chat_id))
    except telegram.error.TelegramError:
        lib_sys.in_log('TG: other telegram related errors')

def service_th():
    while not lib_sys.close_triger:
        if not t_updater.dispatcher.running or not t_updater.running:
            lib_sys.in_log('TG: Telegram break! Updater running: {0}. Dispatcher running: {1}.'.format(t_updater.running, t_updater.dispatcher.running))
            close_telegram()
            init_telegram()
            time.sleep(10)
        time.sleep(0.1)
    lib_sys.in_log('TH: normal exit on service_th')
    return True


def sms_in_th():
    while not lib_sys.close_triger:
        res_query = lib_sms.get_sms()
        for sms in res_query:
            lib_sys.in_log(sms, debug=True)
            sms_id = sms[0]
            sms_number = sms[1]
            sms_text = sms[2]
            query, res = lib_db.check_client(sms_number)
            if not query: continue
            if not res:
                lib_sys.in_log('TH: Bad client: {0} write: "{1}"'.format(sms_number, sms_text), debug=True)
                if not lib_sms.delete_sms(sms_id): continue
                continue
            if len(sms_text) == 0:
                lib_sys.in_log('TH: delete empty sms!', debug=True)
                if not lib_sms.delete_sms(sms_id): continue
                continue
            query, to, res = msg_handler(sms_text, sms_number)
            if not query: return
            if res is not None:
                if to == 'all' or to == 'force_all':
                    send_msg(res, to=to)
                elif to == 'one':
                    if not send_msg(res, to=sms_number): continue
            else:
                if not send_msg('Неправильная команда!', to=sms_number): continue
            if not lib_sms.delete_sms(sms_id): continue
        time.sleep(0.1)
    lib_sys.in_log('TH: normal exit on sms_in_th')
    return True


def alarm_th():
    while not lib_sys.close_triger:
        query, res_query = lib_db.db_query('''SELECT "ID", "name", "info" FROM "sensors" WHERE 
                                    "enable" = TRUE AND "update" = TRUE AND "alarm" = FALSE ''')
        if not query: continue
        if len(res_query) > 0:
            for sensor in res_query:
                lib_sys.in_log('TH: UP sensor: {0} !'.format(sensor[1]))
                if not send_msg('Сработал датчик: {0} Описание: {1}'.format(sensor[1], sensor[2])): continue
                if not lib_db.db_wr_query('''UPDATE "sensors" SET "alarm" = TRUE WHERE "ID" = {0} '''
                                   .format(sensor[0])): continue
        query, res_query = lib_db.db_query('''SELECT "trig_act"."ID", "trig"."name", "trig"."info",
                                    "trig_act"."DateTime", "trig_act"."value", "trig"."up_text", "trig"."down_text"
                                    FROM "trig", "trig_act"
                                    WHERE "trig_act"."trig" = "trig"."ID" AND "trig_act"."alarm" = TRUE ''')
        if not query: continue
        if len(res_query) > 0:
            for trigger in res_query:
                lib_sys.in_log('TH: trigger: {0} !'.format(trigger[1]))
                state = trigger[5] if trigger[4] else trigger[6]
                if not send_msg('{0} {1} в {2}'.format(trigger[2], state, trigger[3])): continue
                if not lib_db.db_wr_query('''UPDATE "trig_act" SET "alarm" = FALSE WHERE "ID" = {0} '''
                                   .format(trigger[0])): continue
        time.sleep(0.1)
    lib_sys.in_log('TH: normal exit on alarm_th')
    return True


def test_th():
    while not lib_sys.close_triger:
        test_in = input('Enter code: ')
        if len(test_in) == 0: test_in = '_'
        test_in = test_in.split()
        if len(test_in) == 1 and test_in[0] == 'stop':
            lib_sys.close_init()
        elif len(test_in) == 1 and test_in[0] == 'send_sms_all':
            send_msg('привет2')
        elif len(test_in) == 1 and test_in[0] == 'send_sms_only':
            send_msg('привет3', to='+7911000000')
        elif len(test_in) == 1 and test_in[0] == 'sen_state':
            print(lib_db.test_sen_state())
        elif len(test_in) == 1 and test_in[0] == 'num_state':
            print(lib_db.test_clients_state())
        elif len(test_in) == 1 and test_in[0] == 'sen_test':
            lib_db.test_alarm()
        elif len(test_in) == 2 and test_in[0] == 'sen_test':
            lib_db.test_alarm(test_in[1])
    lib_sys.in_log('TH: normal exit on test_th')
    return True


init()
