################################### Keyboards ##########################
from flask import json

import sqlite3
from backend import *
from static import *

# Function to create a button
def create_button(button_text, button_callback, color):
    button = {
        "action": {
        "type": "text",
        "payload": '{\"button\": \"' + button_callback + '\"}',
        "label": button_text
        },
        "color": color
        }

    return(button)


def main_keyboard(user_id):

    # notifications db
    conn = sqlite3.connect(notifications_db)
    cursor = conn.cursor()


    # Button color and text
    for ttb in all_timetables:


        if check_user_notified(ttb, user_id):
            ttb.btn_icon = '🔕'
            ttb.btn_color = 'negative'
        else:
            ttb.btn_icon = '🔔'
            ttb.btn_color = 'positive'



    # Close db
    conn.close()

    pravo_c1.btn = create_button('Прав. - 1⃣ ' + pravo_c1.btn_icon, pravo_c1.shortname, pravo_c1.btn_color)
    pravo_c2.btn = create_button('Прав. - 2⃣ ' + pravo_c2.btn_icon, pravo_c2.shortname, pravo_c2.btn_color)
    pravo_c3.btn = create_button('Прав. - 3⃣ ' + pravo_c3.btn_icon, pravo_c3.shortname, pravo_c3.btn_color)
    pravo_c4.btn = create_button('Прав. - 4⃣ ' + pravo_c4.btn_icon, pravo_c4.shortname, pravo_c4.btn_color)

    mag_c1.btn = create_button('Маг. - 1⃣ ' + mag_c1.btn_icon, mag_c1.shortname, mag_c1.btn_color)
    mag_c2.btn = create_button('Маг. - 2⃣ ' + mag_c2.btn_icon, mag_c2.shortname, mag_c2.btn_color)

    download_btn = create_button('Скачать ⬇️', 'download', 'positive')
    stop_btn = create_button('Отключить ❌', 'stop', 'positive')
    
    keyboard = {
    "one_time": True,
    "buttons": [[pravo_c1.btn, pravo_c2.btn, pravo_c3.btn], 
                [pravo_c4.btn, mag_c1.btn, mag_c2.btn],
                [download_btn, stop_btn]]

    }

    return(json.dumps(keyboard, ensure_ascii=False).encode("utf-8"))


def ok_keyboard():

    ok_button = create_button('✔ ОК', 'ok', 'positive')

    keyboard = {
    "one_time": True,
    "buttons": [[ok_button]]

    }

    return(json.dumps(keyboard, ensure_ascii=False).encode("utf-8"))
