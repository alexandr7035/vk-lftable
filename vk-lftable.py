#!./venv/bin/python3 -B
import flask

from flask import Flask, request, json
import vk

import sys
from datetime import datetime
import sqlite3

import os
import ssl

import pytz

import urllib.request

from static import *

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



def first_run_check():
    # Create database for users notified about timetables' updates.
    # 4 tables for each timetable, each with 'users' column
    if not os.path.exists(users_db):
        conn = sqlite3.connect(users_db)
        cursor = conn.cursor()   
        

        
        for timetable in all_timetables:
            cursor.execute('CREATE TABLE ' + timetable.shortname + ' (users)')
            
        conn.commit()
        conn.close()
        
        
    # Create database to store the last update time of each timetable
    # 1 table, 4 rows (1 for each timetable), 2 columns (ttb name and the time of last update)
    if not os.path.exists(times_db):
        
        conn = sqlite3.connect(times_db)
        cursor = conn.cursor()
        
        
        cursor.execute('CREATE TABLE times (ttb, time)')
        conn.commit()
        
        for timetable in all_timetables:
            cursor.execute('INSERT INTO times VALUES ("' + timetable.shortname + '", "")')
        
        conn.commit()
        conn.close()
        
        
# Sets times to the 'times.db' immediately after the run WITHOUT notifiying users 
# Prevents late notifications if the program was down for a long time.
def db_set_times_after_run():
    conn = sqlite3.connect(times_db)
    cursor = conn.cursor()
    
    for timetable in all_timetables:
        
        update_time = ttb_gettime(timetable).strftime('%d.%m.%Y %H:%M:%S')
        
        cursor.execute("UPDATE times SET time = '" + update_time + "' WHERE (ttb = ?)", (timetable.shortname,));
        
    conn.commit()
    conn.close()
       

# The most important function of the program.
# Get and return timetable's mtime using urllib module. 
def ttb_gettime(ttb):
    

    # THIS IS A HOTFIX TO PREVENT "CERTIFICATE_VERIFY_FAILED" ERROR!
    # DISABLE THIS LATER
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    response =  urllib.request.urlopen(ttb.url, timeout=25, context=ctx)
    
    # Get date from HTTP header.
    native_date = ' '.join(dict(response.headers)['Last-Modified'].rsplit()[1:-1])
    
    # Transfer date to normal format.
    gmt_date = datetime.strptime(native_date, '%d %b %Y %H:%M:%S')
    
    # Transfer date to our timezone (GMT+3).
    old_tz = pytz.timezone('Europe/London')
    new_tz = pytz.timezone('Europe/Minsk')
    
    date = old_tz.localize(gmt_date).astimezone(new_tz) 
    
    return(date)
    
    

# Function to create button
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



################################### Keyboards ##########################

def keyboard():
    
    btn_status = '🔔'
    btn_status = '🔕'
    
    pravo_c1.btn = create_button('Правоведение - 1⃣ ' + btn_status, pravo_c1.shortname, "positive")
    pravo_c2.btn = create_button('Правоведение - 2⃣ ' + btn_status, pravo_c1.shortname, "positive")
    pravo_c3.btn = create_button('Правоведение - 3⃣ ' + btn_status, pravo_c1.shortname, "positive")
    pravo_c4.btn = create_button('Правоведение - 4⃣ ' + btn_status, pravo_c1.shortname, "negative")
    
    mag_c1.btn = create_button('Магистратура - 1⃣ ' + btn_status , mag_c1.shortname, "positive")
    mag_c2.btn = create_button('Магистратура - 2⃣ ' + btn_status, mag_c2.shortname, "positive")
    
    
    keyboard = {
    "one_time": True,
    "buttons": [[pravo_c1.btn, pravo_c2.btn],
                [pravo_c3.btn, pravo_c4.btn],
                [mag_c1.btn, mag_c2.btn]] 
    } 
     
    return(json.dumps(keyboard, ensure_ascii=False).encode("utf-8"))




######################### Mesages ######################################

def message_text():
    text = 'Настройте нужные уведомления:'
    
    
    return(text)

########################################################################


def callback_do(callback):
    api.messages.send(access_token=vk_token, user_id=str(user_id), message=message_text(), keyboard=keyboard())



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
        
        #global current_callback
        
        try:
            current_callback = json.loads(data['object']['payload'])['button']
            
            if current_callback in ['pravo_c1', 'pravo_c2', 'pravo_c3', 'pravo_4', 'mag_c1', 'mag_c2']:
                callback_do(current_callback)
        except Exception as e:
            api.messages.send(access_token=vk_token, user_id=str(user_id), message=message_text(), keyboard=keyboard())
            
          
        # Necessary reply
        return 'ok'



if __name__ == '__main__':
    first_run_check()
    db_set_times_after_run()
    app.run(debug=True, host='0.0.0.0', port=80)
