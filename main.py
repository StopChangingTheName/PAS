import json

def main(event, context):
    res = {
        'session': event['session'],
        'version': event['version'],
        'response': {
            'end_session': False
        },
    }
    dialog(event,res)
    return json.dumps(res)

def dialog(event, res):
    return