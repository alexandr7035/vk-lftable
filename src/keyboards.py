import sqlite3
from flask import json
import src.static
import src.db_classes


# Function to create a button
def create_button(button_text, button_callback, color=src.static.default_button_color):
    
    colors_dict = {'red':'negative', 
                   'green':'positive'
    }
    
    button = {
        "action": {
        "type": "text",
        "payload": '{\"button\": \"' + button_callback + '\"}',
        "label": button_text
        },
        "color": colors_dict[color]
        }

    return(button)
    
def create_timetable_button(text, callback, user_id):
    notificationsdb = src.db_classes.NotificationsDB()
    notificationsdb.connect()
    
    timetable_shortname = callback
    
    if notificationsdb.check_if_user_notified(user_id, timetable_shortname) is not True:
        return(create_button(text + ' 🔔', callback))
    else:
        return(create_button(text + ' 🔕', callback, 'red'))
    


def main_keyboard():
    pravo_btn = create_button('📌 Правоведение', 'pravo_menu', 'green')
    ek_polit_btn = create_button('📌 Эк. и полит.', 'ek_polit_menu', 'green')
    mag_btn  = create_button('📌 Магистратура', 'mag_menu', 'green')
    
    download_btn = create_button('⬇️ Скачать', 'download', 'green')
    stop_btn = create_button('Отключить ❌', 'stop', 'green')
    
    keyboard = {
    "one_time": True,
    "buttons": [[pravo_btn, ek_polit_btn],
                [mag_btn, download_btn],
                [stop_btn]]

    }
    
    return(json.dumps(keyboard, ensure_ascii=False).encode("utf-8"))



def pravo_keyboard(user_id):
    pravo_c1_btn = create_timetable_button('Правоведение - 1⃣', src.static.pravo_c1.shortname, user_id)
    pravo_c2_btn = create_timetable_button('Правоведение - 2⃣', src.static.pravo_c2.shortname, user_id)
    pravo_c3_btn = create_timetable_button('Правоведение - 3⃣', src.static.pravo_c3.shortname, user_id)
    pravo_c4_btn = create_timetable_button('Правоведение - 4⃣', src.static.pravo_c4.shortname, user_id)
    back_button = create_button('⬅️ Назад', 'main_menu', 'green')
    
    
    
    keyboard = { 
    "one_time": True,
    "buttons": [[pravo_c1_btn, pravo_c2_btn],
                [pravo_c3_btn, pravo_c4_btn],
                [back_button]]
    }
    
    return(json.dumps(keyboard, ensure_ascii=False).encode("utf-8"))
    
def ek_polit_keyboard(user_id):
    ek_polit_c1_btn = create_timetable_button('Эк. и полит. - 1⃣', src.static.ek_polit_c1.shortname, user_id)
    ek_polit_c2_btn = create_timetable_button('Эк. и полит. - 2⃣', src.static.ek_polit_c2.shortname, user_id)
    ek_polit_c3_btn = create_timetable_button('Эк. и полит. - 3⃣', src.static.ek_polit_c3.shortname, user_id)
    ek_polit_c4_btn = create_timetable_button('Эк. и полит. - 4⃣', src.static.ek_polit_c4.shortname, user_id)
    back_button = create_button('⬅️ Назад', 'main_menu', 'green')

    keyboard = { 
    "one_time": True,
    "buttons": [[ek_polit_c1_btn, ek_polit_c2_btn],
                [ek_polit_c3_btn, ek_polit_c4_btn],
                [back_button]]
    }
    
    return(json.dumps(keyboard, ensure_ascii=False).encode("utf-8"))
    
def mag_keyboard(user_id):
    mag_c1_btn = create_timetable_button('Магистратура- 1⃣', src.static.mag_c1.shortname, user_id)
    mag_c2_btn = create_timetable_button('Магистратура - 2⃣', src.static.mag_c2.shortname, user_id)
    back_button = create_button('⬅️ Назад', 'main_menu', 'green')

    keyboard = { 
    "one_time": True,
    "buttons": [[mag_c1_btn, mag_c2_btn],
                [back_button]]
    }
    
    return(json.dumps(keyboard, ensure_ascii=False).encode("utf-8"))    


def download_keyboard():

    back_button = create_button('Назад', 'main_menu', 'green')

    keyboard = {
    "one_time": True,
    "buttons": [[back_button]]

    }

    return(json.dumps(keyboard, ensure_ascii=False).encode("utf-8"))

def notification_keyboard():
    back_button = create_button('⬅ В меню', 'main_menu', 'green')

    keyboard = {
    "one_time": True,
    "buttons": [[back_button]]

    }

    return(json.dumps(keyboard, ensure_ascii=False).encode("utf-8"))


def start_keyboard():

    start_button = create_button('🗓 Start', 'start', 'green')

    keyboard = {
    "one_time": True,
    "buttons": [[start_button]]

    }

    return(json.dumps(keyboard, ensure_ascii=False).encode("utf-8"))

