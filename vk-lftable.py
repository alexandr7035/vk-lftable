#!./venv/bin/python3 -B
import flask

from flask import Flask, request, json
import vk


import sys
import vk
print(sys.argv)

vk_api_version = 5.50

# Токены
try:
	from tokens import vk_token
except Exception:
	print("Can't load vk_token from file. Exit.")

try:
	from tokens import confirmation_token
except Exception:
	print("Can't load confirmation_token from file. Exit.")


app = flask.Flask(__name__)


@app.route('/', methods=['POST'])
def processing():
    
    data = json.loads(request.data)
    print(data)
    
    if 'type' not in data.keys():
        return 'not vk'
        
    if data['type'] == 'confirmation':
        return confirmation_token
        
    elif data['type'] == 'message_new':
        session = vk.Session()
        api = vk.API(session, v=vk_api_version)
        
        # User who calls bot
        user_id = data['object']['user_id']
        
        api.messages.send(access_token=vk_token, user_id=str(user_id), message='Hello world!')
        
        
        return 'ok'




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
