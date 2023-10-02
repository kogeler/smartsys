import os
import psycopg2
import yaml

close = object()
close_init = object()
logger = object()


def db_init():
    try:
        config = yaml.load(open(os.path.dirname(__file__) + '/config.yml'), Loader=yaml.FullLoader)
    except Exception:
        print('DB: Error open config file!')
        close(1)
    global ssy_con
    try:
        ssy_con = psycopg2.connect(host=config['BD']['smartsys']['host'], port=config['BD']['smartsys']['port'], dbname=config['BD']['smartsys']['dbname'], user=config['BD']['smartsys']['user'], password=config['BD']['smartsys']['password'])
        ssy_con.autocommit = True
    except Exception:
        logger.error('DB: Error opening the smartsys database in init')
        close(2)


def db_close():
    try:
        ssy_con.close()
    except Exception:
        logger.error('DB: Error while closing smartsys database')

def db_query(query):
    res_query = []
    try:
        cursor = ssy_con.cursor()
        cursor.execute(query)
        if cursor.rowcount > 0: res_query = cursor.fetchall()
        cursor.close()
    except Exception:
        logger.error('DB: Error query: {0}'.format(query))
        close_init(2)
        return False, None
    return True, res_query


def db_wr_query(query):
    try:
        cursor = ssy_con.cursor()
        cursor.execute(query)
        cursor.close()
    except Exception:
        logger.error('DB: Error query: {0}'.format(query))
        close_init(2)
        return False
    return True


def check_client(address):
    query, res_query = db_query('''SELECT "ID" FROM "clients" WHERE 
                                "address" = '{0}' '''.format(address))
    if not query: return False, None
    if len(res_query) == 0:
        return True, False
    else:
        return True, True


def set_notif(address='all'):
    if address == 'all':
        logger.debug('DB: set notification for all')
        if not db_wr_query('''UPDATE "clients" SET "state" = TRUE WHERE "state" = FALSE '''): return False
    else:
        logger.debug('DB: set notification for: {0}'.format(address))
        if not db_wr_query('''UPDATE "clients" SET "state" = TRUE WHERE 
                           "state" = FALSE AND "address" = '{0}' '''.format(address)): return False
    return True


def unset_notif(address='all'):
    if address == 'all':
        logger.deug('DB: unset notification for all')
        if not db_wr_query('''UPDATE "clients" SET "state" = FALSE WHERE "state" = TRUE '''): return False
    else:
        logger.debug('DB: unset notification for: {0}'.format(address))
        if not db_wr_query('''UPDATE "clients" SET "state" = FALSE WHERE 
                           "state" = TRUE AND "address" = '{0}' '''.format(address)): return False
    return True


def set_alarm(sen='all'):
    if sen == 'all':
        logger.debug('DB: set all sen')
        if not db_wr_query('''UPDATE "sensors" SET
                       "enable" = TRUE, "update" = FALSE, "alarm" = FALSE WHERE "enable" = FALSE '''): return False
    else:
        logger.debug('DB: set one {0}'.format(sen))
        if not db_wr_query('''UPDATE "sensors" SET "enable" = TRUE, "update" = FALSE, "alarm" = FALSE
                       WHERE "enable" = FALSE AND "name" = '{0}' '''.format(sen)): return False
    return True


def unset_alarm(sen='all'):
    if sen == 'all':
        logger.debug('DB: unset all sen')
        if not db_wr_query('''UPDATE "sensors" SET
                       "enable" = FALSE, "update" = FALSE, "alarm" = FALSE WHERE "enable" = TRUE '''): return False
    else:
        logger.debug('DB: unset one {0}'.format(sen))
        if not db_wr_query('''UPDATE "sensors" SET "enable" = FALSE, "update" = FALSE, "alarm" = FALSE
                       WHERE "enable" = TRUE AND "name" = '{0}' '''.format(sen)): return False
    return True


def reset_alarm(sen='all'):
    if sen == 'all':
        logger.debug('DB: reset all sen')
        if not db_wr_query('''UPDATE "sensors" SET "update" = FALSE, "alarm" = FALSE 
                       WHERE "enable" = TRUE AND "update" = TRUE AND "alarm" = TRUE '''): return False
    else:
        logger.debug('DB: reset one {0}'.format(sen))
        if not db_wr_query('''UPDATE "sensors" SET "update" = FALSE, "alarm" = FALSE 
                    WHERE "enable" = TRUE AND "update" = TRUE AND "alarm" = TRUE
                    AND "name" = '{0}' '''.format(sen)): return False
    return True


def check_alarm(sen):
    query, res_query = db_query('''SELECT "name" FROM "sensors" WHERE "name" = '{0}' '''.format(sen))
    if not query: return False, None
    if len(res_query) == 0:
        return True, False
    else:
        return True, True

def check_point(pt):
    query, res_query = db_query('''SELECT "name" FROM "point" WHERE "name" = '{0}' '''.format(pt))
    if not query: return False, None
    if len(res_query) == 0:
        return True, False
    else:
        return True, True

def get_last(pt):
    query, res_query = db_query('''SELECT "ID", "type" FROM "point" WHERE "name" = '{0}' '''.format(pt))
    if not query: return False, None
    id = res_query[0][0]
    pt_type = res_query[0][1]
    if pt_type == 'thp':
        query, res_query = db_query('''SELECT "temp", "humidity", "pressure" FROM "value_thp"
                                    WHERE "point" = '{0}' ORDER BY "ID" DESC LIMIT 1 '''.format(id))
        if not query: return False, None
        if len(res_query) > 0:
            return True, 'Температура: ' + str(res_query[0][0]) + ' °C Влажность: ' + \
                   str(res_query[0][1]) + ' % Давление: ' + str(res_query[0][2]) + ' мм рт.ст.'
    return True, 'пусто'


def test_sen_state():
    query, res_query = db_query('''SELECT * FROM "sensors" ''')
    if not query: return False
    return res_query


def test_clients_state():
    query, res_query = db_query('''SELECT * FROM "clients" ''')
    if not query: return False
    return res_query


def test_alarm(sen='all'):
    if sen == 'all':
        logger.debug('DB: test all sen')
        if not db_wr_query('''UPDATE "sensors" SET "update" = TRUE WHERE
                       AND "enable" = TRUE AND "update" = FALSE'''): return False
    else:
        logger.debug('DB: test one {0}'.format(sen))
        if not db_wr_query('''UPDATE "sensors" SET "update" = TRUE WHERE "name" = '{0}'
                    AND "enable" = TRUE AND "update" = FALSE'''.format(sen)): return False
    return True