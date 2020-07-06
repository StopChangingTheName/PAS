import copy
import json
import random
from flask import Flask, request, render_template
from threading import Thread
import psycopg2


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
                "title": "Мультиплеер",
                "description": "Нечем заняться с другом? Сыграй с ним в наш навык! Счет до 10 очков.",
                "button": {
                    "text": "Мультиплеер"
                }
            },
            {
                "title": "Рейтинг",
                "description": "Узнай, на каком ты месте в нашем топе!",
                "button": {
                    "text": "Рейтинг"
                }
            }
        ]
    }

def write_in_state(user_id):
    return {
        'nick': sessionStorage[user_id]['nick'],
        'par': sessionStorage[user_id]['par'],
        'sin': sessionStorage[user_id]['sin'],
        'ant': sessionStorage[user_id]['ant']
    }
def write_in_base(user_id):
    con = psycopg2.connect(user="indmfojfvoiiem",
                           password="facdfb9fe6e90a07401ae02ef4e2297fa93c2bf6d205648e5d7e062c0c8da8bb",
                           host="ec2-54-247-78-30.eu-west-1.compute.amazonaws.com",
                           port="5432",
                           database="dd2pdbo5s56kui")
    cur = con.cursor()
    par_count =  sessionStorage[user_id]['par']
    sin_count = sessionStorage[user_id]['sin']
    ant_count = sessionStorage[user_id]['ant']
    summa = par_count + sin_count + ant_count
    cur.execute(f"SELECT * FROM u WHERE nick = '{sessionStorage[user_id]['nick']}';")
    if cur.fetchone() is None:

        cur.execute(
            f"INSERT INTO u VALUES (DEFAULT,'{sessionStorage[user_id]['nick']}',{par_count},{ant_count},{sin_count},{summa});")
    else:
        cur.execute(
            f"UPDATE u SET (paronims, antonims, sinonims, summa) = ({par_count},{ant_count},{sin_count},{summa}) WHERE nick = '{sessionStorage[user_id]['nick']}';")
    con.commit()
    con.close()


def handle_dialog(req, res):
    user_id = req['session']['user_id']
    if res['response']['end_session'] is True:
        write_in_base(user_id)
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
            if 'test_count' in res['user_state_update']:
                res['user_state_update'] = {"nick": None,
          "test_count": None,
          "pic_count": None,
          "ter_count": None,
          "cul_count": None}
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

    if 'мультиплеер' in req['request']['original_utterance'].lower():
        sessionStorage[user_id]['mode'] = 'мультиплеер'
        sessionStorage[user_id]['names'] = []
        antonym = copy.deepcopy(ant)
        paronym = copy.deepcopy(par)
        sinonym = copy.deepcopy(sin)
        data = antonym + paronym + sinonym
        random.shuffle(data)
        sessionStorage[user_id]['data'] = data[:20]
        res['response']['text'] = 'Назови имена тех, кто будет играть, например, Аня и Петя'
        return

    if sessionStorage[user_id]['mode'] in ['антоним', 'пароним', 'синоним']:
        word = sessionStorage[user_id]['data'][sessionStorage[user_id]['id']]['question']
        if not sessionStorage[user_id]['last']:
            res['response']['text'] = f'{word}!'
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
                res['user_state_update'] = write_in_state(user_id)
                write_in_base(user_id)
            else:
                res['response']['text'] = f"Ты ошибся, правильный ответ: {answer}"

            res['response']['text'] += f' Следующий вопрос: {word}!'
            if sessionStorage[user_id]['id'] == len(sessionStorage[user_id]['data']):
                write_in_base(user_id)
                random.shuffle(sessionStorage[user_id]['data'])
                sessionStorage[user_id]['id'] = 0
        sessionStorage[user_id]['id'] += 1
        res['response']['buttons'] = [
            {'title': suggest, 'hide': True}
            for suggest in sessionStorage[user_id]['slicedsuggests']
        ]
    elif sessionStorage[user_id]['mode'] == 'мультиплеер':
        if not sessionStorage[user_id]['names']:
            entity_length = get_first_name(req)
            if entity_length <= 1:
                res['response']['text'] = 'Маловато игроков. Вас должно быть двое! Назови два имени, пожалуйста!'
                return
            elif entity_length >= 3:
                res['response']['text'] = 'Многовато игроков. Вас должно быть двое! Назови два имени, пожалуйста!'
                return
            else:
                sessionStorage[user_id]['names'] = req['request']['original_utterance'].split() # нужна def с поиском интентов
                print(sessionStorage[user_id]['names'])
                res['response']['text'] = 'Я задам каждому по десять вопросов!\n' \
                                          'Немного терминологии.\n' \
                                          'Паронимы — это слова, сходные по звучанию, но различающиеся лексическим значением, например, адресат — адресант.\n' \
                                          'Антонимы — это слова, имеющие прямо противоположные лексические значения, например, огонь — вода.\n' \
                                          'Синонимы — это слова, разные по написанию, но имеющие схожее значение, например, ветер — бриз.\n' \
                                          'Скажи "Поехали!" — и мы начинаем!\n'
                sessionStorage[user_id]['isPlaying'] = sessionStorage[user_id]['names'][0]
                sessionStorage[user_id]['multCount'] = {
                    sessionStorage[user_id]['names'][0]: 0,
                    sessionStorage[user_id]['names'][1]: 0
                }
                sessionStorage[user_id]['multID'] = 0
        else:
            if sessionStorage[user_id]['multID'] == 0:
                res['response']['text'] = f"Играет {sessionStorage[user_id]['isPlaying']}! " \
                    f"{sessionStorage[user_id]['data'][sessionStorage[user_id]['multID']]['question']}."
            else:
                if sessionStorage[user_id]['multID'] == 20: # 10 + 10 + 1
                    # ПРОВЕРКА
                    answer = sessionStorage[user_id]['data'][sessionStorage[user_id]['multID'] - 1]['answer']
                    if answer == req['request']['original_utterance'].lower():
                        toGiveCount = sessionStorage[user_id]['names'][0] \
                            if sessionStorage[user_id]['names'][1] == sessionStorage[user_id]['isPlaying'] else \
                        sessionStorage[user_id]['names'][1]
                        sessionStorage[user_id]['multCount'][toGiveCount] += 1
                        res['response']['text'] = 'Верно! '
                    else:
                        res['response']['text'] = f"Ошибка, правильный ответ: {answer}! "
                    # ПРОВЕРКА
                    name1 = sessionStorage[user_id]['names'][0]
                    name2 = sessionStorage[user_id]['names'][1]
                    if sessionStorage[user_id]['multCount'][name1] == sessionStorage[user_id]['multCount'][name2]:
                        res['response']['text'] += f"В этой битве победила ничья! " \
                            f"Оба игрока набрали по {sessionStorage[user_id]['multCount'][name1]} баллов." # pymorphy2!
                    elif sessionStorage[user_id]['multCount'][name1] > sessionStorage[user_id]['multCount'][name2]:
                        res['response']['text'] += f"Победил игрок {name1} со счетом " \
                            f"{sessionStorage[user_id]['multCount'][name1]}:{sessionStorage[user_id]['multCount'][name2]}"
                    else:
                        res['response']['text'] += f"Победил игрок {name2} со счетом " \
                            f"{sessionStorage[user_id]['multCount'][name2]}:{sessionStorage[user_id]['multCount'][name2]}"
                    return
                else:
                    answer = sessionStorage[user_id]['data'][sessionStorage[user_id]['multID'] - 1]['answer']
                    if answer == req['request']['original_utterance'].lower():
                        toGiveCount = sessionStorage[user_id]['names'][0] \
                    if sessionStorage[user_id]['names'][1] == sessionStorage[user_id]['isPlaying'] else sessionStorage[user_id]['names'][1]
                        sessionStorage[user_id]['multCount'][toGiveCount] += 1
                        res['response']['text'] = 'Верно! '
                    else:
                        res['response']['text'] = f"Ошибка, правильный ответ: {answer}! "
                    res['response']['text'] += f"Играет {sessionStorage[user_id]['isPlaying']}! " \
                        f"{sessionStorage[user_id]['data'][sessionStorage[user_id]['multID']]['question']}."
            sessionStorage[user_id]['isPlaying'] = sessionStorage[user_id]['names'][0] \
                    if sessionStorage[user_id]['names'][1] == sessionStorage[user_id]['isPlaying'] else sessionStorage[user_id]['names'][1]
            sessionStorage[user_id]['multID'] += 1
    else:
        res["response"]["card"] = modes_list("Меню")
        res["response"]["text"] = "Извини, я тебя не понимаю. Выбери режим из предложенных!"
    return


def station_dialog(req, res):
    user_id = req['session']['user_id']
    if res['response']['end_session'] is True:
        write_in_base(user_id)
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

            res['response']['text'] = f'Давно не виделись, {sessionStorage[user_id]["nick"]}! ' \
                f'Твои очки: антонимы: {sessionStorage[user_id]["ant"]}, синонимы: {sessionStorage[user_id]["sin"]} ' \
                f'паронимы: {sessionStorage[user_id]["par"]}'
        except Exception:
            res['response']['text'] = 'Добро пожаловать в словесную игру ПАС. Давай знакомиться! Назови свое имя.'
        return
            
    if sessionStorage[user_id]['nick'] is None:
        tag = str(random.randint(0, 10001))
        sessionStorage[user_id]['nick'] = req['request']['original_utterance'] + "#" + tag
        res['response']['text'] = f'Приятно познакомиться! Твой ник с тэгом: {sessionStorage[user_id]["nick"]}\n' \
                                  'У меня есть 4 режима: паронимы, синонимы, антонимы и мультиплеер на двоих, ' \
                                  'в котором ты сможешь сыграть со своим другом!'
        res['user_state_update'] = {
            'nick': sessionStorage[user_id]['nick']
        }
        return
    if 'паронимы' in req['request']['original_utterance'].lower():
        sessionStorage[user_id]['mode'] = 'пароним'
        paron = copy.deepcopy(par)
        random.shuffle(paron)
        sessionStorage[user_id]['data'] = paron
        sessionStorage[user_id]['id'] = 0
        sessionStorage[user_id]['last'] = False
    if 'антонимы' in req['request']['original_utterance'].lower():
        sessionStorage[user_id]['mode'] = 'антоним'
        antonym = copy.deepcopy(ant)
        random.shuffle(antonym)
        sessionStorage[user_id]['data'] = antonym
        sessionStorage[user_id]['id'] = 0
        sessionStorage[user_id]['last'] = False
    if 'синонимы' in req['request']['original_utterance'].lower():
        sessionStorage[user_id]['mode'] = 'синоним'
        sinonym = copy.deepcopy(sin)
        random.shuffle(sinonym)
        sessionStorage[user_id]['data'] = sinonym
        sessionStorage[user_id]['id'] = 0
        sessionStorage[user_id]['last'] = False

    if sessionStorage[user_id]['mode'] in ['антоним', 'пароним', 'синоним']:
        word = sessionStorage[user_id]['data'][sessionStorage[user_id]['id']]['question']
        if not sessionStorage[user_id]['last']:
            res['response']['text'] = f'{word}!'
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
                res['user_state_update'] = write_in_state(user_id)
            else:
                res['response']['text'] = f"Ты ошибся, правильный ответ: {answer}"

            res['response']['text'] += f' Следующий вопрос: {word}!'
            if sessionStorage[user_id]['id'] == len(sessionStorage[user_id]['data']):
                random.shuffle(sessionStorage[user_id]['data'])
                sessionStorage[user_id]['id'] = 0
        sessionStorage[user_id]['id'] += 1
    elif sessionStorage[user_id]['mode'] == 'мультиплеер':
        if not sessionStorage[user_id]['names']:
            entity_length = get_first_name(req)
            if entity_length <= 1:
                res['response']['text'] = 'Маловато игроков. Вас должно быть двое! Назови два имени, пожалуйста!'
                return
            elif entity_length >= 3:
                res['response']['text'] = 'Многовато игроков. Вас должно быть двое! Назови два имени, пожалуйста!'
                return
            else:
                sessionStorage[user_id]['names'] = req['request']['original_utterance'].split() # нужна def с поиском интентов
                print(sessionStorage[user_id]['names'])
                res['response']['text'] = 'Я задам каждому по десять вопросов! Играть будем по очереди!\n' \
                                          'Немного терминологии для повторения.\n' \
                                          'Паронимы — это слова, сходные по звучанию, но различающиеся лексическим значением, например, адресат — адресант.\n' \
                                          'Антонимы — это слова, имеющие прямо противоположные лексические значения, например, огонь — вода.\n' \
                                          'Синонимы — это слова, разные по написанию, но имеющие схожее значение, например, ветер — бриз.\n' \
                                          'Скажи "Поехали!" — и мы начинаем!\n'
                sessionStorage[user_id]['isPlaying'] = sessionStorage[user_id]['names'][0]
                sessionStorage[user_id]['multCount'] = {
                    sessionStorage[user_id]['names'][0]: 0,
                    sessionStorage[user_id]['names'][1]: 0
                }
                sessionStorage[user_id]['multID'] = 0
        else:
            if sessionStorage[user_id]['multID'] == 0:
                res['response']['text'] = f"Играет {sessionStorage[user_id]['isPlaying']}! " \
                    f"{sessionStorage[user_id]['data'][sessionStorage[user_id]['multID']]['question']}."
            else:
                if sessionStorage[user_id]['multID'] == 20: # 10 + 10 + 1
                    # ПРОВЕРКА
                    answer = sessionStorage[user_id]['data'][sessionStorage[user_id]['multID'] - 1]['answer']
                    if answer == req['request']['original_utterance'].lower():
                        toGiveCount = sessionStorage[user_id]['names'][0] \
                            if sessionStorage[user_id]['names'][1] == sessionStorage[user_id]['isPlaying'] else \
                        sessionStorage[user_id]['names'][1]
                        sessionStorage[user_id]['multCount'][toGiveCount] += 1
                        res['response']['text'] = 'Верно! '
                    else:
                        res['response']['text'] = f"Ошибка, правильный ответ: {answer}! "
                    # ПРОВЕРКА
                    name1 = sessionStorage[user_id]['names'][0]
                    name2 = sessionStorage[user_id]['names'][1]
                    if sessionStorage[user_id]['multCount'][name1] == sessionStorage[user_id]['multCount'][name2]:
                        res['response']['text'] += f"В этой битве победила ничья! " \
                            f"Оба игрока набрали по {sessionStorage[user_id]['multCount'][name1]} баллов." # pymorphy2!
                    elif sessionStorage[user_id]['multCount'][name1] > sessionStorage[user_id]['multCount'][name2]:
                        res['response']['text'] += f"Победил игрок {name1} со счетом " \
                            f"{sessionStorage[user_id]['multCount'][name1]}:{sessionStorage[user_id]['multCount'][name2]}"
                    else:
                        res['response']['text'] += f"Победил игрок {name2} со счетом " \
                            f"{sessionStorage[user_id]['multCount'][name2]}:{sessionStorage[user_id]['multCount'][name2]}"
                    return
                else:
                    answer = sessionStorage[user_id]['data'][sessionStorage[user_id]['multID'] - 1]['answer']
                    if answer == req['request']['original_utterance'].lower():
                        toGiveCount = sessionStorage[user_id]['names'][0] \
                    if sessionStorage[user_id]['names'][1] == sessionStorage[user_id]['isPlaying'] else sessionStorage[user_id]['names'][1]
                        sessionStorage[user_id]['multCount'][toGiveCount] += 1
                        res['response']['text'] = 'Верно! '
                    else:
                        res['response']['text'] = f"Ошибка, правильный ответ: {answer}! "
                    res['response']['text'] += f"Играет {sessionStorage[user_id]['isPlaying']}! " \
                        f"{sessionStorage[user_id]['data'][sessionStorage[user_id]['multID']]['question']}."
            sessionStorage[user_id]['isPlaying'] = sessionStorage[user_id]['names'][0] \
                    if sessionStorage[user_id]['names'][1] == sessionStorage[user_id]['isPlaying'] else sessionStorage[user_id]['names'][1]
            sessionStorage[user_id]['multID'] += 1
    else:
        res['response']['text'] = 'Прости, не понимаю тебя. Выбери режим: паронимы, антонимы, синонимы или мультиплеер.'
    return
    

def get_first_name(req) -> int:
    names = []
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            names.append(entity['value'].get('first_name', None))
    return len(names)


def run():
    app.run(host="0.0.0.0", port=8080)


def keep_alive():
    server = Thread(target=run)
    server.start()


if __name__ == '__main__':
    from flask_ngrok import run_with_ngrok
    run_with_ngrok(app)
    app.run()
    #keep_alive()
    # app.run()