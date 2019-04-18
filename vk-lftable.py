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

import time

# See this fiels understand how everything works.
from static import *
from backend import *


# For time jobs
import atexit
from apscheduler.schedulers.background import BackgroundScheduler




# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

# Tokens
try:
    from tokens import vk_token
except Exception:
    print("Can't load vk_token from file. Exit.")

try:
    from tokens import confirmation_token
except Exception:
    print("Can't load confirmation_token from file. Exit.")



################################### Keyboard ##########################

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

def notification_keyboard():
    
    ok_button = create_button('✔ ОК', 'notification_ok', 'positive')

    keyboard = {
    "one_time": True,
    "buttons": [[ok_button]]
                 
    } 
    
    return(json.dumps(keyboard, ensure_ascii=False).encode("utf-8"))
    
######################### Mesages ######################################

def message_text():
    text = '🛠 Настройте нужные уведомления: 🛠\n'
    text += "\n"
    text += 'Если Вы не видите клавиатуру, попробуйте использовать браузерную версию VK (https://vk.com)\n'
    text += 'На данный момент многие приложения, в т.ч. Kate Mobile и VK mp3, не поддерживают клавиатуры ботов.'
    
    return(text)



##################### Time job for notifications ######################
"""
def print_date_time():
    print(datetime.now().strftime("%A, %d. %B %Y %I:%M:%S %p"))
"""

def send_notification(user_id, ttb, update_time):
    notification_text = '🔔 Обновлено расписание "' + ttb.name + '" 🔔' + '\n'
    notification_text += 'Дата обновления: ' + update_time.strftime('%d.%m.%Y') + '\n'
    notification_text += 'Время обновления: ' + update_time.strftime('%H:%M') + '\n'
    notification_text += '⬇️ Скачать: ' + ttb.url + '\n\n'
    
    api.messages.send(access_token=vk_token, user_id=str(user_id), message=notification_text, keyboard=notification_keyboard())


# Notification message. 
def notifications_check():
    
    print('CHECK STARTED: ', datetime.now().strftime("%A, %d. %B %Y %I:%M:%S %p"))
    
    conn_times_db = sqlite3.connect(times_db)
    cursor_times_db = conn_times_db.cursor()
    
    for checking_ttb in all_timetables:
        
        # Get ttb update time from law.bsu.by
        update_time = ttb_gettime(checking_ttb).strftime('%d.%m.%Y %H:%M:%S')
        
        
        # Get old update time from db.
        cursor_times_db.execute("SELECT time  FROM times WHERE (ttb = ?)", (checking_ttb.shortname,));
        result = cursor_times_db.fetchall()
        old_update_time = result[0][0]
        del(result)
        
        
        
        # String dates to datetime objects
        dt_update_time = datetime.strptime(update_time, '%d.%m.%Y %H:%M:%S')
        dt_old_update_time = datetime.strptime(old_update_time, '%d.%m.%Y %H:%M:%S')
        
        
        # If the timetable was updated, sends it to all users 
        #+ from certain table in 'users.db'
        if dt_update_time > dt_old_update_time:
       
            # Connect to users db.
            conn_users_db = sqlite3.connect(users_db)
            cursor_users_db = conn_users_db.cursor()
        
            cursor_users_db.execute('SELECT users FROM ' + checking_ttb.shortname)
            result = cursor_users_db.fetchall()

            conn_users_db.close()
    
            # List for users notifed about current timetable updates.
            users_to_notify = []
            for i in result:
                users_to_notify.append(i[0])
            del(result)
            
            
            
            # Send notifications to users.
            for user_id in users_to_notify:
                
                send_notification(user_id, checking_ttb, dt_update_time)
                
                time.sleep(send_message_interval)
                
            
            # Writing new update time to the database.
            cursor_times_db.execute("UPDATE times SET time = '" + update_time + "' WHERE (ttb = ?)", (checking_ttb.shortname,));
            conn_times_db.commit()
            
        time.sleep(send_message_interval)
    
    # Close 'times.db' until next check.
    conn_times_db.close()

# Add and run time job
scheduler = BackgroundScheduler()
# Set_updates_interval from 'static.py'
scheduler.add_job(func=notifications_check, trigger="interval", seconds=check_updates_interval)
scheduler.start()




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
    
    
    print("user " + str(user_id) + " pressed button '" + callback + "'")
    
    
    if check_user_notified(current_ttb, user_id):
        conn_check = sqlite3.connect(users_db)
        cursor_check = conn_check.cursor() 
    
        #print('DELETE FROM ' + current_ttb.shortname + ' WHERE (users = \'' + str(user_id) + '\')')
        cursor_check.execute('DELETE FROM ' + current_ttb.shortname + ' WHERE (users = ' + str(user_id) + ')')
        conn_check.commit()
        conn_check.close()
        
        text = '✅ Отключены уведомления для расписания"' + current_ttb.name + '"'
     
        api.messages.send(access_token=vk_token, user_id=str(user_id), message=text)

        
    else:
        conn_check = sqlite3.connect(users_db)
        cursor_check = conn_check.cursor() 
        #print('INSERT INTO ' + current_ttb.shortname + ' VALUES (\'' + user_id + '\')')
        cursor_check.execute('INSERT INTO ' + current_ttb.shortname + ' VALUES (' + str(user_id) + ')')   
        conn_check.commit()
        conn_check.close()
        
        text = '✅ Включены уведомления для расписания"' + current_ttb.name + '"'
        
        api.messages.send(access_token=vk_token, user_id=str(user_id), message=text)
    
      
    # Send main message again.
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


        # User who calls bot
        user_id = data['object']['from_id']
        
        #global callback
        
        try:
            callback = json.loads(data['object']['payload'])['button']
            
            if callback in ['pravo_c1', 'pravo_c2', 'pravo_c3', 'pravo_c4', 'mag_c1', 'mag_c2']:
                callback_do(callback, user_id)
            elif callback == 'notification_ok':
                api.messages.send(access_token=vk_token, user_id=str(user_id), message=message_text(), keyboard=keyboard(user_id))
            
        except Exception as e:
        

            api.messages.send(access_token=vk_token, user_id=str(user_id), message=message_text(), keyboard=keyboard(user_id))
            
          
        # Necessary reply
        return 'ok'


##############################################################

if __name__ == '__main__':
    # Prepare project structure after the first run
    first_run_check()
    # Write times in the db in order to prevent late notifications
    db_set_times_after_run()
    
    
    session = vk.Session()
    api = vk.API(session, v=vk_api_version)
    
    
    
    app.run(debug=True, host='0.0.0.0', port=80, use_reloader=False)

    

