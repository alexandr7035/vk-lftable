#!./venv/bin/python3 -B
import flask

from flask import Flask, request, json
import vk

import sys
import vk
from datetime import datetime
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


current_callback = ''

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
    "one_time": True,
    "buttons": [[pravo_c1.btn, pravo_c2.btn],
                [pravo_c3.btn, pravo_c4.btn],
                [mag_c1.btn, mag_c2.btn]] 
    } 
     
    return(json.dumps(keyboard, ensure_ascii=False).encode("utf-8"))


def answer_keyboard():
    
    menu_button = create_button('Назад в меню', 'menu')
    
    keyboard = {
    "one_time": True,
    "buttons": [[menu_button]] 
    } 
    
    return(json.dumps(keyboard, ensure_ascii=False).encode("utf-8"))
    
def menu_message():
    menu_text = 'LFTable v?: работа с расписанием занятий юридического факультета БГУ.\n\n'
    
    menu_text += 'Источник: https://law.bsu.by\n'
    menu_text += 'Информация об авторских правах юрфака: https://law.bsu.by/avtorskie-prava.html\n'
    
    
    return(menu_text)
    
def answer_message():
    global current_callback
    if current_callback == 'pravo_c1':
        current_ttb = pravo_c1
    elif current_callback == 'pravo_c2':
        current_ttb = pravo_c2
    elif current_callback == 'pravo_c3':
        current_ttb = pravo_c3
    elif current_callback == 'pravo_c4':
        current_ttb = pravo_c4
    
    elif current_callback == 'mag_c1':
        current_ttb = mag_c1
    elif current_callback == 'mag_c2':
        current_ttb = mag_c2
    """  
    elif current_callback == 'refresh':
        current_ttb = old_ttb
    
    elif current_callback == 'notify':
        current_ttb = old_ttb
    """
    
    update_date = ''
    update_time = ''
    
    # Form the message's text
    answer_text = current_ttb.name
    
    answer_text += 'Дата обновления: ' + update_date + '\n'
    answer_text += 'Время обновления: '+ update_time + '\n\n'

    answer_text += 'Скачать: ' + current_ttb.url + "\n\n"
    
    # To fix badrequest error.
    answer_text += '-------------------\n'
    answer_text += 'Страница обновлена: ' + datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    
    return(answer_text)






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
        
        global current_callback
        
        def callback_do_action(current_callback):
        
            if current_callback in  ['pravo_c1', 'pravo_c2', 'pravo_c3', 'pravo_c4', 
                                    'mag_c1', 'mag_c2',
                                    'refresh', 'notify']:
                print(current_callback)
                api.messages.send(access_token=vk_token, user_id=str(user_id), message=answer_message(), keyboard=answer_keyboard())
        
            print("User " + str(user_id) + " pressed '" + current_callback + "' button")

            
            if current_callback == "menu":
                api.messages.send(access_token=vk_token, user_id=str(user_id), message=menu_message(), keyboard=menu_keyboard())
            
        
        try:
            current_callback = json.loads(data['object']['payload'])['button']
            print(current_callback)
            callback_do_action(current_callback)
        except Exception as e:
            print('exception', e)
            api.messages.send(access_token=vk_token, user_id=str(user_id), message=menu_message(), keyboard=menu_keyboard())
            pass
        
          

        
        

        return 'ok'






if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
