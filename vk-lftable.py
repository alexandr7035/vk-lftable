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
import src.db_classes

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
        
        # Objects to access the databases
        self.timesdb = src.db_classes.TimesDB()
        self.notificationsdb = src.db_classes.NotificationsDB()
        self.statisticsdb = src.db_classes.StatisticsDB()
        self.clientsdb = src.db_classes.ClientsDB()
        
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
            if request_time <= round(time.time()) - 5:
                print('skip request')
                return('ok')

            # Get user id
            user_id = str(data['object']['from_id'])
            print(user_id)
            
            
            self.clientsdb.connect()
            
            if self.clientsdb.check_if_user_is_client(user_id) is True:
            
                # That means a button was pressed
                if data['object'].get('payload'):
                    callback = json.loads(data['object']['payload'])['button']
                    self.handle_button_callback(user_id, callback)
                # Usual message was sent
                else:
                    print('receive usual message')
                    self.send_message(user_id, main_menu_text(), main_keyboard())
                    
            else:
                if data['object'].get('payload'):
                    callback = json.loads(data['object']['payload'])['button']
                    if callback == 'start':
                        # Add user to clients db
                        self.clientsdb.add_client(user_id)
                        self.send_message(user_id, main_menu_text(), main_keyboard())                      
                else:
                    self.send_message(user_id, start_text(), start_keyboard())
            
            self.clientsdb.close()
                
             
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
        
        if  callback in ['pravo_c1', 'pravo_c2', 'pravo_c3', 'pravo_c4',
                          'ek_polit_c1', 'ek_polit_c2', 'ek_polit_c3', 'ek_polit_c4',
                        'mag_c1', 'mag_c2']:
            
            timetable = getattr(src.static, callback)                
            
            self.notificationsdb.connect()
            if self.notificationsdb.check_if_user_notified(user_id, timetable.shortname) is True:
                self.notificationsdb.disable_notifications(user_id, timetable.shortname)
                self.send_message(user_id, notification_disabled_text(timetable))
            else:
                self.notificationsdb.enable_notifications(user_id, timetable.shortname)
                self.send_message(user_id, notification_enabled_text(timetable))
            self.notificationsdb.close()
                
            if callback in ['pravo_c1', 'pravo_c2', 'pravo_c3', 'pravo_c4']:
                self.send_message(user_id, main_menu_text(), pravo_keyboard())
            elif callback in ['ek_polit_c1', 'ek_polit_c2', 'ek_polit_c3', 'ek_polit_c4']:
                self.send_message(user_id, main_menu_text(), ek_polit_keyboard())
            elif callback in ['mag_c1', 'mag_c2']:
                self.send_message(user_id, main_menu_text(), mag_keyboard())
                
                
        if callback == 'stop':
            self.clientsdb.connect()
            self.clientsdb.remove_client(user_id)
            self.send_message(user_id, stop_text())
            
    
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




# The main part. Event handler based on flask
app = flask.Flask(__name__)

@app.route('/', methods=['POST'])
def main_handler():
    
    return(bot.handle_request(request))

####################### Main ##################################

# Log message
logger.info("the program was STARTED now")

# Prepare project structure after the first run
#first_run_check()
# Write times in the db in order to prevent late notifications
#db_set_times_after_run()

# VK
session = vk.Session()
api = vk.API(session, v=vk_api_version)

"""
# Add a sheduler
scheduler = BackgroundScheduler()
# Time job for notifications Set_updates_interval from 'static.py'
scheduler.add_job(func=notifications_check, trigger="interval", seconds=check_updates_interval)
# Start the job
scheduler.start()
# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())
"""

# Necessary for wsgi
app.wsgi_app = ProxyFix(app.wsgi_app)



if __name__ == '__main__':
    bot = LFTableBot()
    app.run(host='127.0.0.1', port=5080, use_reloader=False)
    
