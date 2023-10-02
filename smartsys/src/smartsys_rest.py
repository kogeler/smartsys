#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import jsonschema
import os
import psycopg2
import yaml

schema = {
    "type": "object",
    "oneOf": [
        {
            "additionalProperties": False,
            "properties": {
                "type": {"enum": ["sensor"]},
                "id": {"type": "string"},
                "state": {"type": "boolean"}
            },
            "required": ["type", "id", "state"]
        },
        {
            "additionalProperties": False,
            "properties": {
                "type": {"enum": ["triger"]},
                "id": {"type": "string"},
                "state": {"type": "boolean"},
            },
            "required": ["type", "id", "state"]
        }
    ]
}

sql = {
    "req_triger": '''
    SELECT a."name", a."info", b."value"
    FROM "trig" a
    INNER JOIN (
        SELECT "trig", "value"
        FROM "trig_act"
        WHERE "ID" IN
            (SELECT MAX("ID") "ID"
            FROM "trig_act"
            GROUP BY "trig")
    ) b ON a."ID" = b."trig" ''',

    "req_sensor": '''
    SELECT "name", "info", "enable", "update" FROM "sensors"
    '''

}

def db_init():
    try:
        config = yaml.load(open(os.path.dirname(__file__) + '/config.yml'))
    except Exception:
        print('DB: Error open config file!')
    global ssy_con
    try:
        ssy_con = psycopg2.connect(host=config['BD']['smartsys']['host'], port=config['BD']['smartsys']['port'], dbname=config['BD']['smartsys']['dbname'], user=config['BD']['smartsys']['user'], password=config['BD']['smartsys']['password'])
        ssy_con.autocommit = True
    except Exception:
        print('DB: Error opening the smartsys database in init')


def db_close():
    try:
        ssy_con.close()
    except Exception:
        print('DB: Error while closing smartsys database')

def db_query(query):
    res_query = []
    try:
        cursor = ssy_con.cursor()
        cursor.execute(query)
        if cursor.rowcount > 0: res_query = cursor.fetchall()
        cursor.close()
    except Exception:
        print('DB: Error query: {0}'.format(query))
        return False, None
    return True, res_query


def db_wr_query(query):
    try:
        cursor = ssy_con.cursor()
        cursor.execute(query)
        cursor.close()
    except Exception:
        print('DB: Error query: {0}'.format(query))
        return False
    return True


class RequestHandler(BaseHTTPRequestHandler):
    def send_ok(self, body):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        data = []
        query, res_query = db_query(sql['req_sensor'])
        if not query:
            self.send_error(500, 'SQL error')
            return
        for sensor in res_query:
            data.append({'type': 'sensor', 'name': sensor[0], 'info': sensor[1], 'state': sensor[2], 'alarm': sensor[3]})
        query, res_query = db_query(sql['req_triger'])
        if not query:
            self.send_error(500, 'SQL error')
            return
        for triger in res_query:
            data.append({'type': 'triger', 'name': triger[0], 'info': triger[1], 'state': triger[2]})
        if self.path == '/smartsys_rx':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        else:
            self.send_error(404, 'File Not Found {0}'.format(self.path))
            return

    def do_POST(self):
        if self.headers.get('Content-Type') != 'application/json':
            self.send_error(400, 'Content-Type is not "application/json"')
            return
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        try:
            data = json.loads(post_body)
        except Exception:
            self.send_error(400, 'Body is not json: {0}'.format(post_body))
            return
        if self.path == '/smartsys_tx':
            try:
                jsonschema.validate(data, schema)
            except Exception:
                self.send_error(400, 'Validate error: {0}'.format(post_body))
                return
            if data['type'] == 'sensor' and data['state']:
                if not db_wr_query('''UPDATE "sensors" SET "enable" = TRUE, "update" = FALSE, "alarm" = FALSE 
                                   WHERE "name" = '{0}' '''.format(data['id'])):
                    self.send_error(500, 'SQL error')
                    return
                else:
                    self.send_ok(post_body)
            if data['type'] == 'sensor' and not data['state']:
                if not db_wr_query('''UPDATE "sensors" SET "enable" = FALSE, "update" = FALSE, "alarm" = FALSE 
                                   WHERE "name" = '{0}' '''.format(data['id'])):
                    self.send_error(500, 'SQL error')
                    return
                else:
                    self.send_ok(post_body)
        else:
            self.send_error(404, 'File Not Found {0}'.format(self.path))
            return


if __name__ == '__main__':
    db_init()
    server = HTTPServer(('0.0.0.0', 8000), RequestHandler)
    server.serve_forever()