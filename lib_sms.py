
import os
import psycopg2
import yaml

close = object()
close_init = object()
in_log = object()


def sms_init():
    try:
        config = yaml.load(open(os.path.dirname(__file__) + '/config.yml'))
    except Exception:
        print('SMS: Error open config file!')
        close(1)
    global sms_con
    try:
        sms_con = psycopg2.connect(host=config['BD']['sms']['host'], port=config['BD']['sms']['port'], dbname=config['BD']['sms']['dbname'], user=config['BD']['sms']['user'], password=config['BD']['sms']['password'])
        sms_con.autocommit = True
    except Exception:
        in_log('SMS: Error opening the smsd database in init')
        close(2)


def sms_close():
    try:
        sms_con.close()
    except Exception:
        in_log('SMS: Error while closing smsd database')


def send_sms(text, to):
    in_log('SMS: send msg with the text: "{0}" TO: "{1}"'.format(text, to), debug=True)
    try:
        cursor = sms_con.cursor()
        cursor.execute('''INSERT INTO outbox
                       ("DestinationNumber", "TextDecoded", "CreatorID", "Coding")
                       VALUES ('{0}', '{1}', 'smartsys', 'Unicode_No_Compression') '''.format(to, text))
        cursor.close()
    except Exception:
        in_log('SMS: Error send sms')
        close_init(2)
        return False
    return True


def delete_sms(ID):
    try:
        cursor = sms_con.cursor()
        cursor.execute('''DELETE FROM "inbox" WHERE "ID" = {0} '''.format(ID))
        cursor.close()
    except Exception:
        in_log('SMS: Error delete sms')
        close_init(2)
        return False
    return True


def get_sms():
    res_query = []
    try:
        cursor = sms_con.cursor()
        cursor.execute('''SELECT "ID", "SenderNumber", "TextDecoded" FROM "inbox" ''')
        if cursor.rowcount > 0: res_query = cursor.fetchall()
        cursor.close()
    except Exception:
        in_log('SMS: Error get sms')
        close_init(2)
    return res_query
