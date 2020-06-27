import json

def main(event, context):
    res = {
        'session': event['session'],
        'version': event['version'],
        'response': {
            'end_session': False
        },
    }
    if 'screen' in event['meta']['interfaces']:
        dialog(event,res)
    else:
        station_dialog(event, res)
    
    return json.dumps(res)

def dialog(req,res):
    return

def station_dialog(req, res):
    return
    