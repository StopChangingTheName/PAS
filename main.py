import copy
import json
import random
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


def modes_list(phrase):
    return {
        "type": "ItemsList",
        "header": {
            "text": f"{phrase}"
        },
        "items": [
            {
                "title": "Антонимы",
                "description": "Алиса тебе говорит слово, а ты должен подобрать антоним к нему!",
                "button": {
                    "text": "Антонимы"
                }
            },
            {
                "title": "Синонимы",
                "description": "Подбери к слову Алисы верный синонимы!",
                "button": {
                    "text": "Синонимы"
                }
            },
            {
                "title": "Паронимы",
                "description": "Подбери к слову Алисы верный пароним!",
                "button": {
                    "text": "Паронимы"
                }
            },
            {
                "title": "Рейтинг",
                "description": "Узнай, на каком ты месте в нашем топе!",
                "button": {
                    "text": "Рейтинг"
                }
            },
        ]
    }

def handle_dialog(req, res):
    user_id = req['session']['user_id']
    if req['session']['new']:
        sessionStorage[user_id] = {
            'suggests': [
                "Викторина 🎯",
                "Развлечения 🎮",
                "Полезное ✅"
            ],
            'slicedsuggests': [
                "Меню",
                "Не знаю 🤷‍"
            ],
            'test_buttons': [
                "Антонимы",
                "Синонимы",
                "Паронимы",
                "Меню"
            ],
            "nick": None,
            'mode': '',
            'ant': 0,
            'sin': 0,
            'par': 0
        }
        try:
            res['response']['text'] = \
                f"{req['state']['user']['nick']}! Продолжим тренировку! Твои очки: заглушка"
            sessionStorage[user_id]['nick'] = req['state']['user']['nick']
            res['response']['card'] = modes_list(f"Давно не виделись, {sessionStorage[user_id]['nick']}!")
        except Exception:
            res['response']['text'] = 'Добро пожаловать в словесную игру ПАС. Давай знакомиться! Назови свое имя.'
    if sessionStorage[user_id]['nick'] is None:
        tag = str(random.randint(0, 10001))
        sessionStorage[user_id]['nick'] = req['request']['original_utterance'] + "#" + tag
        res['response']['card'] = modes_list(f'Приятно познакомиться! Твой ник с тэгом: {sessionStorage[user_id]["nick"]}\n'
                                             f'У меня есть несколько режимов, просто нажми на кнопку 👇 или скажи, чтобы выбрать их.')

        res['user_state_update'] = {
            'nick': sessionStorage[user_id]['nick']
        }

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
        res['response']['test'] = 'Привет! Добро пожаловать в словесную игру ПАС! Правила я расскажу чуть позже, а сейчас скажи свое имя, пожалуйста:'
        sessionStorage[user_id]['nick'] = req['request']['original_utterance'].lower()




def run():
    app.run(host="0.0.0.0", port=8080)


def keep_alive():
    server = Thread(target=run)
    server.start()


if __name__ == '__main__':
    #keep_alive()
    # app.run()
