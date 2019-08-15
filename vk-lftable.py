#!/usr/bin/env python3

import os
import sys
# Add src/' directory with local modules to path
sys.path.append('src')


import flask
from flask import Flask, request, json
import vk

import time

import sqlite3
from datetime import datetime

# See this files to understand how everything works.
from static import *
from backend import *
from messages import *
from keyboards import *
from lftable_logger import *

# For time jobs (especially for sending notifications)
import atexit
from apscheduler.schedulers.background import BackgroundScheduler

# Necessary for gunicorn wsgi
from werkzeug.contrib.fixers import ProxyFix


# Tokens
try:
    from tokens import vk_token
except Exception:
    print("Can't load vk_token from file. Exit.")
    sys.exit()

try:
    from tokens import confirmation_token
except Exception:
    print("Can't load confirmation_token from file. Exit.")
    sys.exit()




# Function which sends message (used instead of using multiple 'api.messages.send()')
def bot_send_message(user_id, message_text, keyboard=None):

    if keyboard == None:
        api.messages.send(access_token=vk_token, user_id=user_id, message=message_text, keyboard=keyboard)
    else:
        api.messages.send(access_token=vk_token, user_id=user_id, message=message_text, keyboard=keyboard)


class LFTableBot():
    def __init__(self):
        # VK
        session = vk.Session()
        self.api = vk.API(session, v=vk_api_version)
        
    def handle_request(self, flask_request):
        data = json.loads(flask_request.data)
        print(data)
        
        if 'type' not in data.keys():
            return 'not vk'

        # Send confirmation token to vk if requested
        if data['type'] == 'confirmation':
            return confirmation_token
            
        # If got message from user
        elif data['type'] == 'message_new':
            
            # Prevent answers to old requests if bot was down
            request_time = data['object']['date']
            requeste = data['object']['date']
            #if request_time <= round(time.time()) - 20:
            #    return('ok')

            # Get user id
            user_id = str(data['object']['from_id'])
            
            # That means a button was pressed
            if data['object'].get('payload'):
                callback = json.loads(data['object']['payload'])['button']
                self.handle_button_callback(user_id, callback)
            # Usual message was sent
            else:
                print('receive usual message')
                self.send_message(user_id, main_menu_text(), main_keyboard())
                
             
        return 'ok'
    
    def handle_button_callback(self, user_id, callback):
        print('CALLBACK')
        
        if callback == 'main_menu':
            self.send_message(user_id, main_menu_text(), main_keyboard())
        
        if callback == 'download':
            self.send_message(user_id, download_text(), download_keyboard())
            
        if callback in ['pravo_menu', 'ek_polit_menu', 'mag_menu']:
            if callback == 'pravo_menu':
                self.send_message(user_id, main_menu_text(), pravo_keyboard())
            elif callback == 'ek_polit_menu':
                self.send_message(user_id, main_menu_text(), ek_polit_keyboard())
            elif callback == 'mag_menu':
                self.send_message(user_id, main_menu_text(), mag_keyboard())
    
    def send_message(self, user_id, text, keyboard=None):
        self.api.messages.send(access_token=vk_token, user_id=user_id, message=text, keyboard=keyboard)

        

bot = LFTableBot()


##################### Time job for notifications ######################

# Main function for notifications.
def notifications_check():

    print('Checking for ttb updates was started: ', datetime.now().strftime("%d.%m.%Y %Y %H:%M:%S"))

    # Connect to  the times db
    conn_times_db = sqlite3.connect(times_db)
    cursor_times_db = conn_times_db.cursor()

    # Check each ttb for updates (see this list in 'static.py')
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


        # If the timetable was updated, sends a notification to each user
        #+ from certain table in 'users.db'
        if dt_update_time > dt_old_update_time:

            # Log message
            logger.info("'" + checking_ttb.shortname + "' timetable was updated at " + update_time)

            # Connect to users db.
            conn_notifications_db = sqlite3.connect(notifications_db)
            cursor_notifications_db = conn_notifications_db.cursor()

            cursor_notifications_db.execute('SELECT user_id FROM ' + checking_ttb.shortname)
            result = cursor_notifications_db.fetchall()

            conn_notifications_db.close()

            # List for users notifed about current timetable updates.
            users_to_notify = []
            for i in result:
                users_to_notify.append(i[0])
            del(result)


            # Send a notification to each user.
            for user_id in users_to_notify:

                # Log message
                logger.info("'" + checking_ttb.shortname + "' notification was sent to user " + user_id)

                bot_send_message(user_id, notification_text(user_id, checking_ttb, dt_update_time), ok_keyboard())

                # A delay to prevent flood control exceptions
                time.sleep(send_message_interval)


            # Writing new update time to the database.
            cursor_times_db.execute("UPDATE times SET time = '" + update_time + "' WHERE (ttb = ?)", (checking_ttb.shortname,));
            conn_times_db.commit()

        # A delay to prevent flood control exceptions
        time.sleep(next_timetable_interval)

    # Close 'times.db' until next check.
    conn_times_db.close()


########################################################################

# Function for buttons' callbacks
def callback_do(callback, user_id):

    # Debug message
    #print("user " + user_id + " pressed button '" + callback + "'")
    #logger.debug('user ' + user_id + " pressed button '" + callback + "'")

    # Start button
    if callback == 'start' and not check_user_is_client(user_id):
                print("got button start claabacl")
                # Add user id from clients_db
                conn_clients_db = sqlite3.connect(clients_db)
                cursor_clients_db = conn_clients_db.cursor()
                cursor_clients_db.execute('INSERT INTO clients VALUES ("'  + user_id + '")')
                conn_clients_db.commit()
                conn_clients_db.close()

                logger.info("user "  + user_id + " added to 'clients.db'")

                bot_send_message(user_id, main_text(), main_keyboard(user_id))

                return

    # If user is still not a client, send invitation
    if not check_user_is_client(user_id):
            bot_send_message(user_id, start_text(), start_keyboard())
            return


    # Download button
    if callback == 'download':
        bot_send_message(user_id, download_text(), ok_keyboard())

        # Skip the code below, exit
        return


    # Stop button
    elif callback == 'stop':


        # Disable all notifications.
        conn_check = sqlite3.connect(notifications_db)
        cursor_check = conn_check.cursor()

        for ttb in all_timetables:
            if check_user_notified(ttb, user_id):

                cursor_check.execute('DELETE FROM ' + ttb.shortname + ' WHERE (user_id = "' + user_id + '")')
                conn_check.commit()

        conn_check.close()


        # Remove user id from clients_db
        conn_clients_db = sqlite3.connect(clients_db)
        cursor_clients_db = conn_clients_db.cursor()
        cursor_clients_db.execute('DELETE FROM clients WHERE (user_id = "' + user_id + '")')
        conn_clients_db.commit()
        conn_clients_db.close()

        # Log message
        logger.info("user "  + user_id + " removed from 'clients.db'")

        # Send 'stop' message
        bot_send_message(user_id, stopped_text())

        # Skip the code below, exit
        return


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


    # TTB button handling
    # If user id already exists in 'notifications.db', disable notifications and remove it
    if check_user_notified(current_ttb, user_id):
        conn_check = sqlite3.connect(notifications_db)
        cursor_check = conn_check.cursor()

        cursor_check.execute('DELETE FROM ' + current_ttb.shortname + ' WHERE (user_id = "' + user_id + '")')
        conn_check.commit()
        conn_check.close()

        # Log message
        logger.info('user ' + user_id + " disabled notifications for the '" + current_ttb.shortname + "' timetable")

        # Info message.
        bot_send_message(user_id, notification_disabled_text(current_ttb))

    # Write user id to the 'notifications.db'
    else:
        conn_check = sqlite3.connect(notifications_db)
        cursor_check = conn_check.cursor()
        cursor_check.execute('INSERT INTO ' + current_ttb.shortname + ' VALUES ("' + user_id + '")')
        conn_check.commit()
        conn_check.close()

        # Log message
        logger.info('user ' + user_id + " enabled notifications for the '" + current_ttb.shortname + "' timetable")

        # Info message.
        bot_send_message(user_id, notification_enabled_text(current_ttb))


    # Send main message again.
    bot_send_message(user_id, main_text(), main_keyboard())



# The main part. Event handler based on flask
app = flask.Flask(__name__)

@app.route('/', methods=['POST'])
def main_handler():
    
    return(bot.handle_request(request))
    """
    return 'ok'
    
    data = json.loads(request.data)

    print(datetime.now().strftime('%d.%m.%Y %H:%M:%S') + ' ---', data, '--- END')
    
    return  
    
    if 'type' not in data.keys():
        return 'not vk'

    # Send confirmation token to vk if requested
    if data['type'] == 'confirmation':
        return confirmation_token


    # If got message from user
    elif data['type'] == 'message_new':

        # User who calls bot
        user_id = str(data['object']['from_id'])


        # Prevent answers to old requests if bot was down
        request_time = data['object']['date']
        if request_time <= round(time.time()) - 5:

            # Write to log
            print('late request (unix time - ' + str(request_time) + ') was skipped')
            logger.info("late request (unix time - " + str(request_time) + ") was skipped")

            # Skip this request
            return('ok')



        # If user is not a client and sends '/start' command
        message_text = data['object']['text']



        # If user is a client and any button is pressed.
        try:
            callback = json.loads(data['object']['payload'])['button']
            callback_do(callback, user_id)
            return 'ok'

        except Exception:

            # If user is still not a client, send invitation
            if not check_user_is_client(user_id):
                bot_send_message(user_id, start_text(), start_keyboard())
                return "ok"

            # Reply for any invalid text message - send menu again.
            bot_send_message(user_id, main_text(), main_keyboard(user_id))
            return 'ok'
    """

####################### Main ##################################

# Log message
logger.info("the program was STARTED now")

# Prepare project structure after the first run
first_run_check()
# Write times in the db in order to prevent late notifications
db_set_times_after_run()

# VK
session = vk.Session()
api = vk.API(session, v=vk_api_version)

# Add a sheduler
scheduler = BackgroundScheduler()
# Time job for notifications Set_updates_interval from 'static.py'
scheduler.add_job(func=notifications_check, trigger="interval", seconds=check_updates_interval)
# Start the job
scheduler.start()
# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

# Necessary for wsgi
app.wsgi_app = ProxyFix(app.wsgi_app)



if __name__ == '__main__':
    bot = LFTableBot()
    app.run(host='127.0.0.1', port=5080, use_reloader=False)
