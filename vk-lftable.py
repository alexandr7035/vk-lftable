#!./venv/bin/python3 -B
import flask

from flask import Flask, request, json
import vk

import sys
from datetime import datetime
import sqlite3

import os

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



################################### Keyboards ##########################

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
    stop_btn = create_button('Отключить 🛑', 'stop', 'positive')
    
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

######################### Mesages ######################################



def main_text():
    text = '🛠 Выберите нужное действие. 🛠\n'
    text += "\n"
    text += '⚠ Если Вы не видите клавиатуру, попробуйте использовать браузерную версию VK (https://vk.com).\n'
    text += 'На данный момент многие приложения, в т.ч. Kate Mobile и VK mp3, не поддерживают клавиатуры ботов.\n'

    return(text)

def download_text():
    text = 'Ссылки для загрузки файлов с расписаниями.\n\n'
    
    
    for ttb in all_timetables:

        text += '⬇️ "' + ttb.name + '" - ' + ttb.url + ' - ' + ttb_gettime(ttb).strftime('%d.%m.%Y %H:%M') + '\n'
        time.sleep(0.2)
        
    text += '\n⚠ Если Вы не видите клавиатуру, попробуйте использовать браузерную версию VK (https://vk.com).'
    
    return(text)


##################### Time job for notifications ######################

# Notification text.
def send_notification(user_id, ttb, update_time):
    notification_text = '🔔 Обновлено расписание "' + ttb.name + '" 🔔' + '\n'
    notification_text += 'Дата обновления: ' + update_time.strftime('%d.%m.%Y') + '\n'
    notification_text += 'Время обновления: ' + update_time.strftime('%H:%M') + '\n'
    notification_text += '⬇️ Скачать: ' + ttb.url + '\n\n'
    
    notification_text += '⚠ Если Вы не видите клавиатуру, попробуйте использовать браузерную версию VK (https://vk.com).'
    
    api.messages.send(access_token=vk_token, user_id=str(user_id), message=notification_text, keyboard=ok_keyboard())

# Main function for notifications.
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
            conn_notifications_db = sqlite3.connect(notifications_db)
            cursor_notifications_db = conn_notifications_db.cursor()

            cursor_notifications_db.execute('SELECT users FROM ' + checking_ttb.shortname)
            result = cursor_notifications_db.fetchall()

            conn_notifications_db.close()

            # List for users notifed about current timetable updates.
            users_to_notify = []
            for i in result:
                users_to_notify.append(i[0])
            del(result)
            


            # Send notification to each user.
            for user_id in users_to_notify:

                send_notification(user_id, checking_ttb, dt_update_time)

                time.sleep(send_message_interval)


            # Writing new update time to the database.
            cursor_times_db.execute("UPDATE times SET time = '" + update_time + "' WHERE (ttb = ?)", (checking_ttb.shortname,));
            conn_times_db.commit()

        time.sleep(next_timetable_interval)

    # Close 'times.db' until next check.
    conn_times_db.close()

# Add and run time job
scheduler = BackgroundScheduler()
# Set_updates_interval from 'static.py'
scheduler.add_job(func=notifications_check, trigger="interval", seconds=check_updates_interval)
scheduler.start()




########################################################################


def callback_do(callback, user_id):


    # Download button
    if callback == 'download':
        api.messages.send(access_token=vk_token,
                      user_id=str(user_id),
                      message=download_text(),
                      keyboard=ok_keyboard())
        return
    
    
    # Stop command    
    elif callback == 'stop':
        
        # Disable all notifications.
        conn_check = sqlite3.connect(notifications_db)
        cursor_check = conn_check.cursor()
        
        for ttb in all_timetables:
            if check_user_notified(ttb, user_id):
                
                cursor_check.execute('DELETE FROM ' + ttb.shortname + ' WHERE (users = ' + str(user_id) + ')')
                conn_check.commit()
                
        conn_check.close()
               
        
        # Remove user id from clients_db
        conn_clients_db = sqlite3.connect(clients_db)
        cursor_clients_db = conn_clients_db.cursor()
        
        cursor_clients_db.execute('DELETE FROM clients WHERE (user_id = "' + str(user_id) + '")')
        conn_clients_db.commit()
        conn_clients_db.close()
        
        
        stop_text = '🛑 Отключены все уведомления, клавиатура скрыта. \nЧтобы снова начать работу с ботом, напишите любое сообщение'
        api.messages.send(access_token=vk_token,
                      user_id=str(user_id),
                      message=stop_text)
        return 'ok'
    
    
    # TTB buttons
    elif callback == 'pravo_c1':
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
        conn_check = sqlite3.connect(notifications_db)
        cursor_check = conn_check.cursor()

        #print('DELETE FROM ' + current_ttb.shortname + ' WHERE (users = \'' + str(user_id) + '\')')
        cursor_check.execute('DELETE FROM ' + current_ttb.shortname + ' WHERE (users = ' + str(user_id) + ')')
        conn_check.commit()
        conn_check.close()

        # Info message.
        text = '❎ Отключены уведомления для расписания "' + current_ttb.name + '".'
        api.messages.send(access_token=vk_token,
                          user_id=str(user_id),
                          message=text)
    
    
    

    else:
        conn_check = sqlite3.connect(notifications_db)
        cursor_check = conn_check.cursor()
        #print('INSERT INTO ' + current_ttb.shortname + ' VALUES (\'' + user_id + '\')')
        cursor_check.execute('INSERT INTO ' + current_ttb.shortname + ' VALUES (' + str(user_id) + ')')
        conn_check.commit()
        conn_check.close()
        
        # Info message.
        text = '✅ Включены уведомления для расписания"' + current_ttb.name + '".'
        api.messages.send(access_token=vk_token,
                          user_id=str(user_id),
                          message=text)


    # Send main message again.
    api.messages.send(access_token=vk_token,
                      user_id=str(user_id),
                      message=main_text(),
                      keyboard=main_keyboard())
                      

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
       
        
        message_text = data['object']['text']

            
        # If user is not a client and wants to become one    
        if message_text in ['/start'] and not check_user_is_client(user_id):
       
                # Add user id from clients_db
                conn_clients_db = sqlite3.connect(clients_db)
                cursor_clients_db = conn_clients_db.cursor()
        
                cursor_clients_db.execute('INSERT INTO clients VALUES ("'  + str(user_id) + '")')
                conn_clients_db.commit()
               
                
                conn_clients_db.close()
                
                api.messages.send(access_token=vk_token,
                              user_id=str(user_id),
                              message=main_text(),
                              keyboard=main_keyboard(user_id))
                
            
                return 'ok'
        

        # If user is still not a client, send invitation
        if not check_user_is_client(user_id):
            
            # Send invitation
            text = '🗓 LFTable-bot: быстрый доступ к расписанию занятий юридического факультета БГУ.\n'
            text += "⌨️ Введите '/start', чтобы начать работу."
            api.messages.send(access_token=vk_token,
                              user_id=str(user_id),
                              message=text) 
            
            return "ok"
        

        
        # If any button is pressed.
        try:
            callback = json.loads(data['object']['payload'])['button']
            callback_do(callback, user_id)
            return 'ok'
        except Exception as e:
            print('callback exception')
            api.messages.send(access_token=vk_token,
                              user_id=str(user_id),
                              message=main_text(),
                              keyboard=main_keyboard(user_id))
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



