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
    
    try:
        os.mkdir(db_dir)
    except Exception:
        pass
    
    
    
    # Create database for users notified about timetables' updates.
    # 4 tables for each timetable, each with 'users' column
    if not os.path.exists(users_db):
        print(users_db)
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
    
# Checks if user is notified when timetable is updated.
# Used to set text on the "notify" button.
def check_user_notified(ttb, user_id):
    
    # Connect to users db.
    conn = sqlite3.connect(users_db)
    cursor = conn.cursor()
        
    cursor.execute('SELECT users FROM ' + ttb.shortname)
    result = cursor.fetchall()
        
    conn.close()
    
    # List for users notifed about current ttb updates.
    users_to_notify = []
    for i in result:
       users_to_notify.append(i[0])

    
    if user_id in users_to_notify:
           return True
    else:
           return False


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

def keyboard(user_id):
    
    # notifications db
    conn = sqlite3.connect(users_db)
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
    
    pravo_c1.btn = create_button('Правоведение - 1⃣ ' + pravo_c1.btn_icon, pravo_c1.shortname, pravo_c1.btn_color)
    pravo_c2.btn = create_button('Правоведение - 2⃣ ' + pravo_c2.btn_icon, pravo_c2.shortname, pravo_c2.btn_color)
    pravo_c3.btn = create_button('Правоведение - 3⃣ ' + pravo_c3.btn_icon, pravo_c3.shortname, pravo_c3.btn_color)
    pravo_c4.btn = create_button('Правоведение - 4⃣ ' + pravo_c4.btn_icon, pravo_c4.shortname, pravo_c4.btn_color)
    
    mag_c1.btn = create_button('Магистратура - 1⃣ ' + mag_c1.btn_icon, mag_c1.shortname, mag_c1.btn_color)
    mag_c2.btn = create_button('Магистратура - 2⃣ ' + mag_c2.btn_icon, mag_c2.shortname, mag_c2.btn_color)
    
 
    
    keyboard = {
    "one_time": True,
    "buttons": [[pravo_c1.btn, pravo_c2.btn],
                [pravo_c3.btn, pravo_c4.btn],
                [mag_c1.btn, mag_c2.btn]]
                 
    } 
     
    return(json.dumps(keyboard, ensure_ascii=False).encode("utf-8"))




######################### Mesages ######################################

def message_text():
    text = '🔔 Настройте нужные уведомления: 🔔\n'
    text += '---------\n'
    text += 'Если Вы не видите клавиатуру, попробуйте использовать браузерную версию VK (https://vk.com)\n'
    text += 'В настоящее время приложение Kate Mobile не поддерживает клавиатуры ботов.'
    
    return(text)

########################################################################


def callback_do(callback, user_id):
    if callback == 'pravo_c1':
        current_ttb = pravo_c1
    elif callback == 'pravo_c2':
        current_ttb = pravo_c2
    elif callback == 'pravo_c3':
        current_ttb = pravo_c3
    elif callback == 'pravo_c4':
        current_ttb = pravo_c4
    
    elif callback == 'mag_c1':
        current_ttb = mag_c1
    elif callback == 'mag_c2':
        current_ttb = mag_c2
    
    
    #print("user " + user_id + " pressed button '" + callback + "'")
    

    
    if check_user_notified(current_ttb, user_id):
        conn_check = sqlite3.connect(users_db)
        cursor_check = conn_check.cursor() 
    
        #print('DELETE FROM ' + current_ttb.shortname + ' WHERE (users = \'' + str(user_id) + '\')')
        cursor_check.execute('DELETE FROM ' + current_ttb.shortname + ' WHERE (users = ' + str(user_id) + ')')
        conn_check.commit()
        conn_check.close()
    else:
        conn_check = sqlite3.connect(users_db)
        cursor_check = conn_check.cursor() 
        #print('INSERT INTO ' + current_ttb.shortname + ' VALUES (\'' + user_id + '\')')
        cursor_check.execute('INSERT INTO ' + current_ttb.shortname + ' VALUES (' + str(user_id) + ')')   
        conn_check.commit()
        conn_check.close()
           
    

    
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
        
        #global callback
        
        try:
            callback = json.loads(data['object']['payload'])['button']
            
            if callback in ['pravo_c1', 'pravo_c2', 'pravo_c3', 'pravo_c4', 'mag_c1', 'mag_c2']:
                callback_do(callback, user_id)
        except Exception as e:
            api.messages.send(access_token=vk_token, user_id=str(user_id), message=message_text(), keyboard=keyboard(user_id))
            
          
        # Necessary reply
        return 'ok'



if __name__ == '__main__':
    first_run_check()
    db_set_times_after_run()
    app.run(debug=True, host='0.0.0.0', port=80)
