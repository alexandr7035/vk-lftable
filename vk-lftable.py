#!./venv/bin/python3 -B
import flask

from flask import Flask, request, json
import vk

import sys
import vk
print(sys.argv)

vk_api_version = 5.90

# Токены
try:
    from tokens import vk_token
except Exception:
    print("Can't load vk_token from file. Exit.")

try:
    from tokens import confirmation_token
except Exception:
    print("Can't load confirmation_token from file. Exit.")

from static import *


def create_button(button_text, button_callback):
    button = {
        "action": {
        "type": "text",
        "payload": '{\"button\": \"' + button_callback + '\"}',
        "label": button_text
        },
        "color": "positive"
        }
        
    return(button)


def menu_keyboard():
    
    pravo_c1.btn = create_button('Правоведение - 1⃣', pravo_c1.shortname)
    pravo_c2.btn = create_button('Правоведение - 2⃣', pravo_c1.shortname)
    pravo_c3.btn = create_button('Правоведение - 3⃣', pravo_c1.shortname)
    pravo_c4.btn = create_button('Правоведение - 4⃣', pravo_c1.shortname)
    
    mag_c1.btn = create_button('Магистратура - 1⃣', mag_c1.shortname)
    mag_c2.btn = create_button('Магистратура - 2⃣', mag_c2.shortname)
    
    
    keyboard = {
    "one_time": False,
    "buttons": [[pravo_c1.btn, pravo_c2.btn],
				[pravo_c3.btn, pravo_c4.btn],
				[mag_c1.btn, mag_c2.btn]] 
    } 
     
    return(json.dumps(keyboard, ensure_ascii=False).encode("utf-8"))






app = flask.Flask(__name__)


@app.route('/', methods=['POST'])
def main_handler():

    data = json.loads(request.data)
    print(70*'=')
    print(data)
    print(70*'=')

    if 'type' not in data.keys():
        return 'not vk'

    if data['type'] == 'confirmation':
        return confirmation_token

    elif data['type'] == 'message_new':
        session = vk.Session()
        api = vk.API(session, v=vk_api_version)

        # User who calls bot
        user_id = data['object']['from_id']
		
		
		
        api.messages.send(access_token=vk_token, user_id=str(user_id), message='Hello world!', keyboard=menu_keyboard())

        return 'ok'






if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
