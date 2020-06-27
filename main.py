import json, psycorg2

def write_in_base(user_id):
    con = psycopg2.connect(user="indmfojfvoiiem",
                           password="facdfb9fe6e90a07401ae02ef4e2297fa93c2bf6d205648e5d7e062c0c8da8bb",
                           host="ec2-54-247-78-30.eu-west-1.compute.amazonaws.com",
                           port="5432",
                           database="dd2pdbo5s56kui")
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
    