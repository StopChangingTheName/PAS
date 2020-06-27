import copy
import json
import random
from flask import Flask, request, render_template
from threading import Thread


sessionStorage = {}
app = Flask('')
with open('Data.json', encoding='utf8') as f:
    ant = json.loads(f.read())['antonimy']  # массив из словарей дат
with open('Data.json', encoding='utf8') as f:
    par = json.loads(f.read())['paron']  # массив из словарей дат
with open('Data.json', encoding='utf8') as f:
    sin = json.loads(f.read())['sinonimy']  # массив из словарей дат

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

def write_in_state(user_id):
    return {
        'nick': sessionStorage[user_id]['nick'],
        'par': sessionStorage[user_id]['par'],
        'sin': sessionStorage[user_id]['sin'],
        'ant': sessionStorage[user_id]['ant']
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
            'par': 0,
            'last': False
        }
        try:
            sessionStorage[user_id]['ant'] = req['state']['user']['ant']
            sessionStorage[user_id]['sin'] = req['state']['user']['sin']
            sessionStorage[user_id]['par'] = req['state']['user']['par']
            sessionStorage[user_id]['nick'] = req['state']['user']['nick']

            res['response']['text'] = f'Давно не виделись, {sessionStorage[user_id]["nick"]}! ' \
                f'Твои очки: антонимы: {sessionStorage[user_id]["ant"]}, синонимы: {sessionStorage[user_id]["sin"]} ' \
                f'паронимы: {sessionStorage[user_id]["par"]}'
            res['response']['card'] = modes_list(f"Давно не виделись!")
        except Exception:
            res['response']['text'] = 'Добро пожаловать в словесную игру ПАС. Давай знакомиться! Назови свое имя.'
        return
    print('НУ ЭТО КЛИНИКА РЕБЯТ', sessionStorage[user_id]['nick'])
    if sessionStorage[user_id]['nick'] is None:
        tag = str(random.randint(0, 10001))
        sessionStorage[user_id]['nick'] = req['request']['original_utterance'] + "#" + tag
        res['response']['card'] = modes_list(f'Приятно познакомиться! Твой ник с тэгом: {sessionStorage[user_id]["nick"]}\n')
        res['response']['text'] = f'Приятно познакомиться! Твой ник с тэгом: {sessionStorage[user_id]["nick"]}\n. ' \
            f'У меня есть несколько режимов, просто нажми на кнопку или скажи, чтобы выбрать их.'
        res['user_state_update'] = {
            'nick': sessionStorage[user_id]['nick']
        }
        return
    if 'меню' in req['request']['original_utterance'].lower():
        res["response"]["card"] = modes_list("Меню")
        res["response"]["text"] = "Выбери режим из предложенных!"
        sessionStorage[user_id]['mode'] = ''
        return

    if 'антонимы' in req['request']['original_utterance'].lower():
        sessionStorage[user_id]['mode'] = 'антоним'
        antonym = copy.deepcopy(ant)
        random.shuffle(antonym)
        sessionStorage[user_id]['data'] = antonym
        sessionStorage[user_id]['id'] = 0
        sessionStorage[user_id]['last'] = False

    if 'паронимы' in req['request']['original_utterance'].lower():
        sessionStorage[user_id]['mode'] = 'пароним'
        paronym = copy.deepcopy(par)
        random.shuffle(par)
        sessionStorage[user_id]['data'] = paronym
        sessionStorage[user_id]['id'] = 0
        sessionStorage[user_id]['last'] = False

    if 'синонимы' in req['request']['original_utterance'].lower():
        sessionStorage[user_id]['mode'] = 'синоним'
        sinonym = copy.deepcopy(sin)
        random.shuffle(sin)
        sessionStorage[user_id]['data'] = sinonym
        sessionStorage[user_id]['id'] = 0
        sessionStorage[user_id]['last'] = False

    if sessionStorage[user_id]['mode'] in ['антоним', 'пароним', 'синоним']:
        word = sessionStorage[user_id]['data'][sessionStorage[user_id]['id']]['question']
        if not sessionStorage[user_id]['last']:
            res['response']['text'] = f'Подбери {sessionStorage[user_id]["mode"]} к слову {word}!'
            sessionStorage[user_id]['last'] = True
        else:
            answer = sessionStorage[user_id]['data'][sessionStorage[user_id]['id']-1]['answer']
            if answer == req['request']['original_utterance'].lower():
                res['response']['text'] = "Верно!"
                if sessionStorage[user_id]['mode'] == 'антоним':
                    sessionStorage[user_id]['ant'] += 1
                elif sessionStorage[user_id]['mode'] == 'синоним':
                    sessionStorage[user_id]['sin'] += 1
                elif sessionStorage[user_id]['mode'] == 'пароним':
                    sessionStorage[user_id]['par'] += 1
                write_in_state(user_id)
            else:
                res['response']['text'] = f"Ты ошибся, правильный ответ: {answer}"

            res['response']['text'] += f' Следующий вопрос: подбери {sessionStorage[user_id]["mode"]} к слову {word}!'
            if sessionStorage[user_id]['id'] == len(sessionStorage[user_id]['data']):
                random.shuffle(sessionStorage[user_id]['data'])
                sessionStorage[user_id]['id'] = 0
        sessionStorage[user_id]['id'] += 1
        res['response']['buttons'] = [
            {'title': suggest, 'hide': True}
            for suggest in sessionStorage[user_id]['slicedsuggests']
        ]
    else:
        res["response"]["card"] = modes_list("Меню")
        res["response"]["tts"] = "Извини, я тебя не понимаю. Выбери режим из предложенных!"
    return


def station_dialog(req, res):
    user_id = req['session']['user_id']
    if res['response']['end_session'] is True:
        #write_in_base(user_id)
        print(0)
    if req['session']['new']:
        sessionStorage[user_id] = {
            "nick": None,
            'mode': '',
            'ant': 0,
            'sin': 0,
            'par': 0,
            'last': False
        }
        try:
            sessionStorage[user_id]['nick'] = req['state']['user']['nick']
            sessionStorage[user_id]['ant'] = req['state']['user']['ant']
            sessionStorage[user_id]['sin'] = req['state']['user']['sin']
            sessionStorage[user_id]['par'] = req['state']['user']['par']
            res['response']['text'] = 'Привет еще раз! Продолжим игру! Выбирай режим: паронимы, антонимы или синонимы.'

        except Exception:
            res['response'][
                'text'] = 'Привет! Добро пожаловать в словесную игру ПАС!' \
                          'Скажи своё имя для сохранения результатов:'

    if sessionStorage[user_id]['nick'] is None:
        tag = str(random.randint(0, 10001))
        sessionStorage[user_id]['nick'] = req['request']['original_utterance'] + "#" + tag
        res['response']['text'] = f'Приятно познакомиться! Твой ник с тэгом: {sessionStorage[user_id]["nick"]}\n' \
                                  'У меня есть 3 режима: паронимы, синонимы, антонимы.'

        res['user_state_update'] = {
            'nick': sessionStorage[user_id]['nick']
        }
        return
    if 'паронимы' in req['request']['original_utterance'].lower():
        sessionStorage[user_id]['mode'] = 'паронимы'
        paron = copy.deepcopy(par)
        random.shuffle(paron)
        sessionStorage[user_id]['data'] = paron
        sessionStorage[user_id]['id'] = 0
        sessionStorage[user_id]['last'] = False
    if 'антонимы' in req['request']['original_utterance'].lower():
        sessionStorage[user_id]['mode'] = 'антонимы'
        antonym = copy.deepcopy(ant)
        random.shuffle(antonym)
        sessionStorage[user_id]['data'] = antonym
        sessionStorage[user_id]['id'] = 0
        sessionStorage[user_id]['last'] = False
    if 'синонимы' in req['request']['original_utterance'].lower():
        sessionStorage[user_id]['mode'] = 'синонимы'
        sinonym = copy.deepcopy(sin)
        random.shuffle(sinonym)
        sessionStorage[user_id]['data'] = sinonym
        sessionStorage[user_id]['id'] = 0
        sessionStorage[user_id]['last'] = False
    if 'помощь' in req['request']['original_utterance'].lower():
        res['response']['text'] = 'У меня есть 3 режима: паронимы, антонимы и синонимы. В каждом режиме я буду говорить тебе слово, а тебе нужно придумать слово из 3 этих категорий.'
    if sessionStorage[user_id]['mode'] in ['антоним', 'пароним', 'синоним']:
        word = sessionStorage[user_id]['data'][sessionStorage[user_id]['id']]['question']
        if not sessionStorage[user_id]['last']:
            res['response']['text'] = f'Подбери {sessionStorage[user_id]["mode"]} к слову {word}!'
            sessionStorage[user_id]['last'] = True
        else:
            answer = sessionStorage[user_id]['data'][sessionStorage[user_id]['id']-1]['answer']
            if answer == req['request']['original_utterance'].lower():
                res['response']['text'] = "Верно!"
                if sessionStorage[user_id]['mode'] == 'антоним':
                    sessionStorage[user_id]['ant'] += 1
                elif sessionStorage[user_id]['mode'] == 'синоним':
                    sessionStorage[user_id]['sin'] += 1
                elif sessionStorage[user_id]['mode'] == 'пароним':
                    sessionStorage[user_id]['par'] += 1
                write_in_state(user_id)
            else:
                res['response']['text'] = f"Ты ошибся, правильный ответ: {answer}"

            res['response']['text'] += f' Следующий вопрос: подбери {sessionStorage[user_id]["mode"]} к слову {word}!'
            if sessionStorage[user_id]['id'] == len(sessionStorage[user_id]['data']):
                random.shuffle(sessionStorage[user_id]['data'])
                sessionStorage[user_id]['id'] = 0
        sessionStorage[user_id]['id'] += 1
    else:
        res['response']['text'] = 'Прости, не понимаю тебя. Скажи помощь, и я расскажу тебе правила игры.'
    return
    


def run():
    app.run(host="0.0.0.0", port=8080)


def keep_alive():
    server = Thread(target=run)
    server.start()


if __name__ == '__main__':
    #from flask_ngrok import run_with_ngrok
    #run_with_ngrok(app)
    #app.run()
    keep_alive()
    # app.run()