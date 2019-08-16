################################### Keyboards ##########################
from flask import json

import sqlite3
from backend import *
from static import *

# Function to create a button
def create_button(button_text, button_callback, color='green'):
    
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



def pravo_keyboard():
    pravo_c1_btn = create_button('Правоведение - 1⃣', pravo_c1.shortname)
    pravo_c2_btn = create_button('Правоведение - 2⃣', pravo_c2.shortname)
    pravo_c3_btn = create_button('Правоведение - 3⃣', pravo_c3.shortname)
    pravo_c4_btn = create_button('Правоведение - 4⃣', pravo_c4.shortname)
    back_button = create_button('⬅️ Назад', 'main_menu', 'green')
    
    for btn, timetable in zip([pravo_c1_btn, pravo_c2_btn, pravo_c3_btn, pravo_c4_btn],
                              [pravo_c1, pravo_c2, pravo_c3, pravo_c4]):
        print(btn, timetable)
        

    keyboard = { 
    "one_time": True,
    "buttons": [[pravo_c1_btn, pravo_c2_btn],
                [pravo_c3_btn, pravo_c4_btn],
                [back_button]]
    }
    
    return(json.dumps(keyboard, ensure_ascii=False).encode("utf-8"))
    
def ek_polit_keyboard():
    ek_polit_c1_btn = create_button('Эк. и полит. - 1⃣', ek_polit_c1.shortname, 'green')
    ek_polit_c2_btn = create_button('Эк. и полит. - 2⃣', ek_polit_c2.shortname, 'green')
    ek_polit_c3_btn = create_button('Эк. и полит. - 3⃣', ek_polit_c3.shortname, 'green')
    ek_polit_c4_btn = create_button('Эк. и полит. - 4⃣', ek_polit_c4.shortname, 'green')
    back_button = create_button('⬅️ Назад', 'main_menu', 'green')

    keyboard = { 
    "one_time": True,
    "buttons": [[ek_polit_c1_btn, ek_polit_c2_btn],
                [ek_polit_c3_btn, ek_polit_c4_btn],
                [back_button]]
    }
    
    return(json.dumps(keyboard, ensure_ascii=False).encode("utf-8"))
    
def mag_keyboard():
    mag_c1_btn = create_button('Магистратура- 1⃣', mag_c1.shortname, 'green')
    mag_c2_btn = create_button('Магистратура - 2⃣', mag_c2.shortname, 'green')
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




def start_keyboard():

    start_button = create_button('🗓 Start', 'start', 'green')

    keyboard = {
    "one_time": True,
    "buttons": [[start_button]]

    }

    return(json.dumps(keyboard, ensure_ascii=False).encode("utf-8"))

