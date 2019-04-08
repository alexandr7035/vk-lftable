#!./venv/bin/python3 -B
import flask

from flask import Flask, request, json
import vk

import sys
from datetime import datetime


vk_api_version = 5.90

# Tokens
try:
    from tokens import vk_token
except Exception:
    print("Can't load vk_token from file. Exit.")

try:
    from tokens import confirmation_token
except Exception:
    print("Can't load confirmation_token from file. Exit.")

from static import *

# A global variable. Button pressed.
current_callback = ''

# Function to create button
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



################################### Keyboards ##########################

def menu_keyboard():
    
    btn_status = '🔔'
    btn_status = '🔕'
    
    pravo_c1.btn = create_button('Правоведение - 1⃣ ' + btn_status, pravo_c1.shortname)
    pravo_c2.btn = create_button('Правоведение - 2⃣ ' + btn_status, pravo_c1.shortname)
    pravo_c3.btn = create_button('Правоведение - 3⃣ ' + btn_status, pravo_c1.shortname)
    pravo_c4.btn = create_button('Правоведение - 4⃣ ' + btn_status, pravo_c1.shortname)
    
    mag_c1.btn = create_button('Магистратура - 1⃣ ' + btn_status , mag_c1.shortname)
    mag_c2.btn = create_button('Магистратура - 2⃣ ' + btn_status, mag_c2.shortname)
    
    
    keyboard = {
    "one_time": True,
    "buttons": [[pravo_c1.btn, pravo_c2.btn],
                [pravo_c3.btn, pravo_c4.btn],
                [mag_c1.btn, mag_c2.btn]] 
    } 
     
    return(json.dumps(keyboard, ensure_ascii=False).encode("utf-8"))




######################### Mesages ######################################

def menu_message():
    menu_text = 'VK-LFTable v1.0: работа с расписанием занятий юридического факультета БГУ.\n\n'
    
    menu_text += 'Источник: https://law.bsu.by\n'
    menu_text += 'Информация об авторских правах юрфака: https://law.bsu.by/avtorskie-prava.html\n\n'
    
    menu_text += 'Выберите нужное расписание:'
    
    return(menu_text)

########################################################################


# The main part. Event handler based on flask

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
    
    # If got message from user
    elif data['type'] == 'message_new':
        session = vk.Session()
        api = vk.API(session, v=vk_api_version)

        # User who calls bot
        user_id = data['object']['from_id']
        
        global current_callback
        
        
        def callback_do_action(current_callback, mid):
            print("User " + str(user_id) + " pressed '" + current_callback + "' button")
            if current_callback in  ['pravo_c1', 'pravo_c2', 'pravo_c3', 'pravo_c4', 
                                    'mag_c1', 'mag_c2',
                                    'refresh', 'notify']:
                pass
            
            

            
            if current_callback == "menu":
                api.messages.send(access_token=vk_token, peer_id=str(user_id), message_id=mid, message=menu_message(), keyboard=menu_keyboard(), dont_parse_links=1, photo='inx960x640.jpg')
            
        
        # If users sends text instead of pressing button
        # Send to main menu
        try:
            current_callback = json.loads(data['object']['payload'])['button']
            print(data['object']['conversation_message_id'])
            
            mid = int(data['object']['conversation_message_id'])
            
            callback_do_action(current_callback, mid)
        except Exception as e:
            print('exception', e)
            api.messages.send(access_token=vk_token, user_id=str(user_id), message=menu_message(), keyboard=menu_keyboard())
            pass
        """

        
        mid = int(data['object']['conversation_message_id'])
        current_callback = json.loads(data['object']['payload'])['button']
        callback_do_action(current_callback, mid)
        """
          
        # Necessary reply
        return 'ok'



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
