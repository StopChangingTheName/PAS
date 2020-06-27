import copy
import json
import logging
import random
from threading import Thread
import psycopg2
from flask import Flask, request, render_template

sessionStorage = {}
app = Flask('')


@app.route('/post', methods=['POST'])
def main():
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        },
    }
    if 'screen' in request.json['meta']['interfaces']:
        handle_dialog(request.json, response)
    else:
        station_dialog(request.json, response)
    return json.dumps(response)


def handle_dialog(req, res):
    if req['session']['new']:
        res['response']['text'] = 'Добро пожаловать в словесную игру ПАС. Давай знакомиться! Назови свое имя.'

def config(user_id):
    sessionStorage[user_id] = {
        "nick": None,
        'mode': '',
        'word_id': 0,
    }

def station_dialog(req, res):
    user_id = req['session']['user_id']
    if res['response']['end_session'] is True:
        write_in_base(user_id)
    if req['session']['new']:
        config(user_id)
        res['response']['test'] = 'Привет! Добро пожаловать в ПАС! Скажи имя:'
        sessionStorage[user_id]['nick'] = 




def run():
    app.run(host="0.0.0.0", port=8080)


def keep_alive():
    server = Thread(target=run)
    server.start()


if __name__ == '__main__':
    keep_alive()
    # app.run()
