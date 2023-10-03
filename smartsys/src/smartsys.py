#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
import logging
import asyncio
import traceback
import lib_sys
import lib_sms
import lib_db


from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters,
)


def init():
    global logger
    global config
    global application
    lib_sys.init()
    config = lib_sys.config
    logger = logging.getLogger('smartsys')
    lib_sys.setup_logger(logger)
    logger.info('Start')
    lib_db.close = lib_sys.close
    lib_db.close_init = lib_sys.close_init
    lib_db.logger = logger
    lib_db.db_init()
    lib_sms.close = lib_sys.close
    lib_sms.close_init = lib_sys.close_init
    lib_sms.logger = logger
    lib_sms.sms_init()
    application = Application.builder().token(config['sys']['tg_token']).build()

def handle_exceptions(func):
    '''Decorator that handles all exceptions.'''

    def wrap(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f'{func.__name__} function raised the exception, error: "{e}"')
            tb_output = io.StringIO()
            traceback.print_tb(e.__traceback__, file=tb_output)
            logger.debug(f'{func.__name__} function raised the exception, '
                          f'traceback:\n{tb_output.getvalue()}')
            tb_output.close()
            return None
    return wrap


@handle_exceptions
async def init_telegram():
    application.add_handler(MessageHandler(filters.ALL, t_message_handle))
    await application.initialize()
    await application.start()
    await application.updater.start_polling(allowed_updates=Update.ALL_TYPES, timeout=90)


@handle_exceptions
async def t_message_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query, res = lib_db.check_client(update.message.chat_id)
    logger.debug('TG: Сhat id: {0} write: "{1}"'.format(update.effective_message.chat_id, update.effective_message.text))
    if not query: return
    if not res:
        logger.debug('TG: Bad client: {0} write: "{1}"'.format(update.message.chat_id, update.message.text))
        await update.effective_message.reply_text('Ты левак!')
        return
    query, to, res = msg_handler(update.effective_message.text, update.effective_message.chat_id)
    if not query: return
    if res is not None:
        if to == 'all' or to == 'force_all':
            await send_msg(res, to=to)
        elif to == 'one':
            await update.effective_message.reply_text(res)
    else:
        await update.effective_message.reply_text('Неправильная команда!')


@handle_exceptions
async def send_msg(text, *, to='all'):
    if lib_sys.msg_debug_state:
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
        logger.debug(f'FUN: send msg with the text: "{text}" TO: "{client[1]}" via: {client[0]}')
        if client[0] == 'sms':
            if not lib_sms.send_sms(text, client[1]): return False
        elif client[0] == 'telegram':
            await application.bot.send_message(chat_id=client[1], text=text)
    return True


@handle_exceptions
def msg_handler(msg, client):
    msg = msg.split()
    # Включить рассылку для всех
    if len(msg) == 3 and msg[0] == 'уведомления' and msg[1] == 'всем' and msg[2] == 'включить':
        logger.debug('Handler: set notification for all')
        if lib_db.set_notif():
            return True, 'force_all', 'Включена рассылка для всех'
        else:
            return False, None, None
    # Выключить рассылку для всех
    elif len(msg) == 3 and msg[0] == 'уведомления' and msg[1] == 'всем' and msg[2] == 'выключить':
        logger.debug('Handler: unset notification for all')
        if lib_db.unset_notif():
            return True, 'force_all', 'Выключена рассылка для всех'
        else:
            return False, None, None
    # Включить рассылку для одного клиента
    elif len(msg) == 3 and msg[0] == 'уведомления' and msg[1] == 'мне' and msg[2] == 'включить':
        logger.debug('Handler: set notification for: {0}'.format(client))
        if lib_db.set_notif(client):
            return True, 'one', 'Для вас включена рассылка'
        else:
            return False, None, None
    # Выключить рассылку для одного сенсора
    elif len(msg) == 3 and msg[0] == 'уведомления' and msg[1] == 'мне' and msg[2] == 'выключить':
        logger.debug('Handler: unset notification for: {0}'.format(client))
        if lib_db.unset_notif(client):
            return True, 'one', 'Для вас выключена рассылка'
        else:
            return False, None, None
    # Включить мотирониг всех сенсоров
    elif len(msg) == 3 and msg[0] == 'мониторинг' and msg[1] == 'всех' and msg[2] == 'включить':
        logger.debug('Handler: monitoring all on')
        if lib_db.set_alarm():
            return True, 'all', 'Включен мотирониг всех сенсоров'
        else:
            return False, None, None
    # Выключить мотирониг всех сенсоров
    elif len(msg) == 3 and msg[0] == 'мониторинг' and msg[1] == 'всех' and msg[2] == 'выключить':
        logger.debug('Handler: monitoring all off')
        if lib_db.unset_alarm():
            return True, 'all', 'Выключен мотирониг всех сенсоров'
        else:
            return False, None, None
    # Включить мониторинг одного сенсора
    elif len(msg) == 3 and msg[0] == 'мониторинг' and msg[1] != 'всех' and msg[2] == 'включить':
        query, res = lib_db.check_alarm(msg[1])
        if not query: return False, None, None
        if res:
            logger.debug('Handler: monitoring one {0} on'.format(msg[1]))
            if lib_db.set_alarm(msg[1]):
                return True, 'all', 'Включен мониторинг сенсора: {0}'.format(msg[1])
            else:
                return False, None, None
        else:
            logger.debug('Handler: the {0} does not exist!'.format(msg[1]))
            return True, 'one', 'Сенсор {0} несуществует!'.format(msg[1])
    # Выключить мониторинг одного сенсора
    elif len(msg) == 3 and msg[0] == 'мониторинг' and msg[1] != 'всех' and msg[2] == 'выключить':
        query, res = lib_db.check_alarm(msg[1])
        if not query: return False, None, None
        if res:
            logger.debug('Handler: monitoring one {0} off'.format(msg[1]))
            if lib_db.unset_alarm(msg[1]):
                return True, 'all', 'Выключен мониторинг сенсора: {0}'.format(msg[1])
            else:
                return False, None, None
        else:
            logger.debug('Handler: the {0} does not exist!'.format(msg[1]))
            return True, 'one', 'Сенсор {0} несуществует!'.format(msg[1])
    # Сброс всех сенсоров
    elif len(msg) == 2 and msg[0] == 'сбросить' and msg[1] == 'все':
        logger.debug('Handler: reset all')
        if lib_db.reset_alarm():
            return True, 'all', 'Сброшены все сенсоры'
        else:
            return False, None, None
    # Сброс одного сенсора
    elif len(msg) == 2 and msg[0] == 'сбросить' and msg[1] != 'все':
        query, res = lib_db.check_alarm(msg[1])
        if not query: return False, None, None
        if res:
            logger.debug('Handler: reset one {0}'.format(msg[1]))
            if lib_db.reset_alarm(msg[1]):
                return True, 'all', 'Сброшен сенсор: {0}'.format(msg[1])
            else:
                return False, None, None
        else:
            logger.debug('Handler: the {0} does not exist!'.format(msg[1]))
            return True, 'one', 'Сенсор {0} несуществует!'.format(msg[1])
    # Запрор показаний одного датчика
    elif len(msg) == 2 and msg[0] == 'запросить':
        query, res = lib_db.check_point(msg[1])
        if not query: return False, None, None
        if res:
            logger.debug('Handler: get for {0}'.format(msg[1]))
            query, res = lib_db.get_last(msg[1])
            if not query: return False, None, None
            return True, 'one', res
        else:
            logger.debug('Handler: the {0} does not exist!'.format(msg[1]))
            return True, 'one', 'Датчик {0} не существует!'.format(msg[1])
    else:
        return True, None, None


# def t_error_handler(Bot, Update, TelegramError):
#     try:
#         raise TelegramError
#     except telegram.error.Unauthorized:
#         logger.error('TG: Unauthorized')
#     except telegram.error.BadRequest:
#         logger.error('TG: BadRequest')
#     except telegram.error.TimedOut:
#         logger.error('TG: TimedOut')
#     except telegram.error.NetworkError:
#         logger.error('TG: NetworkError')
#     except telegram.error.ChatMigrated as e:
#         logger.error('TG: the chat_id of a group has changed, use {0} instead'.format(e.new_chat_id))
#     except telegram.error.TelegramError:
#         logger.error('TG: other telegram related errors')


@handle_exceptions
async def closing_task():
    while not lib_sys.close_triger:
        # if not application.running:
        #     logger.error('TG: Telegram break! Updater running: {0}'.format(application.running))
        #     close_telegram()
        #     init_telegram()
        #     await asyncio.sleep(10)
        await asyncio.sleep(0.1)
    logger.info('Closing started...')
    application.stop_running()
    lib_sms.sms_close()
    lib_db.db_close()
    pending = asyncio.all_tasks(loop=main_loop)
    group = asyncio.gather(*pending)
    main_loop.run_until_complete(group)
    main_loop.close()
    return True


@handle_exceptions
async def sms_task():
    while not lib_sys.close_triger:
        res_query = lib_sms.get_sms()
        for sms in res_query:
            logger.debug(sms)
            sms_id = sms[0]
            sms_number = sms[1]
            sms_text = sms[2]
            query, res = lib_db.check_client(sms_number)
            if not query: continue
            if not res:
                logger.debug('TH: Bad client: {0} write: "{1}"'.format(sms_number, sms_text))
                if not lib_sms.delete_sms(sms_id): continue
                continue
            if len(sms_text) == 0:
                logger.debug('TH: delete empty sms!')
                if not lib_sms.delete_sms(sms_id): continue
                continue
            query, to, res = msg_handler(sms_text, sms_number)
            if not query: return
            if res is not None:
                if to == 'all' or to == 'force_all':
                    await send_msg(res, to=to)
                elif to == 'one':
                    if not await send_msg(res, to=sms_number): continue
            else:
                if not await send_msg('Неправильная команда!', to=sms_number): continue
            if not lib_sms.delete_sms(sms_id): continue
        await asyncio.sleep(0.1)
    logger.info('TH: normal exit on sms_in_th')
    return True


@handle_exceptions
async def alarm_task():
    while not lib_sys.close_triger:
        query, res_query = lib_db.db_query('''SELECT "ID", "name", "info" FROM "sensors" WHERE 
                                    "enable" = TRUE AND "update" = TRUE AND "alarm" = FALSE ''')
        if not query: continue
        if len(res_query) > 0:
            for sensor in res_query:
                logger.info('TH: UP sensor: {0} !'.format(sensor[1]))
                if not await send_msg('Сработал датчик: {0} Описание: {1}'.format(sensor[1], sensor[2])): continue
                if not lib_db.db_wr_query('''UPDATE "sensors" SET "alarm" = TRUE WHERE "ID" = {0} '''
                                   .format(sensor[0])): continue
        query, res_query = lib_db.db_query('''SELECT "trig_act"."ID", "trig"."name", "trig"."info",
                                    "trig_act"."DateTime", "trig_act"."value", "trig"."up_text", "trig"."down_text"
                                    FROM "trig", "trig_act"
                                    WHERE "trig_act"."trig" = "trig"."ID" AND "trig_act"."alarm" = TRUE ''')
        if not query: continue
        if len(res_query) > 0:
            for trigger in res_query:
                logger.info('TH: trigger: {0} !'.format(trigger[1]))
                state = trigger[5] if trigger[4] else trigger[6]
                if not await send_msg('{0} {1} в {2}'.format(trigger[2], state, trigger[3])): continue
                if not lib_db.db_wr_query('''UPDATE "trig_act" SET "alarm" = FALSE WHERE "ID" = {0} '''
                                   .format(trigger[0])): continue
        await asyncio.sleep(0.1)
    logger.info('TH: normal exit on alarm_th')
    return True


@handle_exceptions
async def test_task():
    while not lib_sys.close_triger:
        test_in = input('Enter code: ')
        if len(test_in) == 0: test_in = '_'
        test_in = test_in.split()
        if len(test_in) == 1 and test_in[0] == 'stop':
            lib_sys.close_init()
        elif len(test_in) == 1 and test_in[0] == 'send_sms_all':
            await send_msg('привет2')
        elif len(test_in) == 1 and test_in[0] == 'send_sms_only':
            await send_msg('привет3', to='+79115000964')
        elif len(test_in) == 1 and test_in[0] == 'sen_state':
            print(lib_db.test_sen_state())
        elif len(test_in) == 1 and test_in[0] == 'num_state':
            print(lib_db.test_clients_state())
        elif len(test_in) == 1 and test_in[0] == 'sen_test':
            lib_db.test_alarm()
        elif len(test_in) == 2 and test_in[0] == 'sen_test':
            lib_db.test_alarm(test_in[1])
    logger.info('TH: normal exit on test_th')
    return True


if __name__ == '__main__':
    init()

    main_loop = asyncio.get_event_loop()

    main_loop.create_task(sms_task(), name="sms task")
    main_loop.create_task(alarm_task(), name="alarm task")
    main_loop.create_task(init_telegram(), name="init telegram task")
    main_loop.create_task(closing_task(), name="closing task")
    if lib_sys.test_state:
        main_loop.create_task(test_task(), name="test task")

    main_loop.run_forever()

    lib_sys.close()
