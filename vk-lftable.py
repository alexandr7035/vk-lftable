#!/usr/bin/env python3

import os
import sys
import time
import sqlite3
import atexit
from datetime import datetime

import vk
import flask
from flask import Flask, request, json
from apscheduler.schedulers.background import BackgroundScheduler

# See 'src/' directory
import src.static
import src.messages
import src.keyboards
import src.db_classes
from src.lftable_logger import *


# Tokens
try:
    from src.tokens import vk_token
except Exception:
    print("Can't load vk_token from file. Exit.")
    sys.exit()

try:
    from src.tokens import confirmation_token
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
        self.api = vk.API(session, v=src.static.vk_api_version)
        
        # Objects to access the databases
        self.timesdb = src.db_classes.TimesDB()
        self.notificationsdb = src.db_classes.NotificationsDB()
        self.statisticsdb = src.db_classes.StatisticsDB()
        self.clientsdb = src.db_classes.ClientsDB()
        
        # Create necessary directories and files
        self.prepare_workspace()
        
        # Sets times to the 'times.db' immediately after the run WITHOUT notifiying users
        # This is to prevent late notifications if the bot was down for a long time
        self.timesdb.connect()
        for timetable in src.static.all_timetables:
            update_time = src.gettime.ttb_gettime(timetable).strftime('%d.%m.%Y %H:%M:%S')
            self.timesdb.write_time(timetable.shortname, update_time)
        self.timesdb.close()
        
        
    def prepare_workspace(self):
        
        # Create directory for sqlite3 databases
        if not os.path.exists(src.static.db_dir):
            os.mkdir(src.static.db_dir)
            
            logger.info("'" + src.static.db_dir + "' directory was created")
            
        # Create databases. See db_classes.py
        if not os.path.isfile(src.static.clientsdb_path):
            self.clientsdb.connect()
            self.clientsdb.construct()
            self.clientsdb.close()

            logger.info("'" + src.static.clientsdb_path + "' database was created")

        if not os.path.isfile(src.static.timesdb_path):
            self.timesdb.connect()
            self.timesdb.construct()
            self.timesdb.close()

            logger.info("'" + src.static.timesdb_path + "' database was created")

        if not os.path.isfile(src.static.notificationsdb_path):
            self.notificationsdb.connect()
            self.notificationsdb.construct()
            self.notificationsdb.close()

            logger.info("'" + src.static.notificationsdb_path + "' database was created")

        if not os.path.isfile(src.static.statisticsdb_path):
            self.statisticsdb.connect()
            self.statisticsdb.construct()
            self.statisticsdb.close()

            logger.info("'" + src.static.statisticsdb_path + "' database was created")
        
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
                    self.send_message(user_id, 
                                     src.messages.main_menu_text(), 
                                     src.keyboards.main_keyboard())
                    
            else:
                if data['object'].get('payload'):
                    callback = json.loads(data['object']['payload'])['button']
                    if callback == 'start':
                        # Add user to clients db
                        self.clientsdb.add_client(user_id)
                        self.send_message(user_id, 
                                          src.messages.main_menu_text(), 
                                          src.keyboards.main_keyboard())                      
                else:
                    self.send_message(user_id, 
                                      src.messages.start_text(), 
                                      src.keyboards.start_keyboard())
            
            self.clientsdb.close()
                
             
        return 'ok'
    
    def handle_button_callback(self, user_id, callback):
        print('CALLBACK')
        
        if callback == 'main_menu':
            self.send_message(user_id, src.messages.main_menu_text(), src.keyboards.main_keyboard())
        
        if callback == 'download':
            self.send_message(user_id, src.messages.download_text(), src.keyboards.download_keyboard())
            
        if callback in ['pravo_menu', 'ek_polit_menu', 'mag_menu']:
            if callback == 'pravo_menu':
                self.send_message(user_id, 
                                  src.messages.main_menu_text(), 
                                  src.keyboards.pravo_keyboard(user_id))
            elif callback == 'ek_polit_menu':
                self.send_message(user_id, 
                                  src.messages.main_menu_text(), 
                                  src.keyboards.ek_polit_keyboard(user_id))
            elif callback == 'mag_menu':
                self.send_message(user_id, 
                                  src.messages.main_menu_text(), 
                                  src.keyboards.mag_keyboard(user_id))
        
        if  callback in ['pravo_c1', 'pravo_c2', 'pravo_c3', 'pravo_c4',
                          'ek_polit_c1', 'ek_polit_c2', 'ek_polit_c3', 'ek_polit_c4',
                        'mag_c1', 'mag_c2']:
            
            timetable = getattr(src.static, callback)                
            
            self.notificationsdb.connect()
            if self.notificationsdb.check_if_user_notified(user_id, timetable.shortname) is True:
                self.notificationsdb.disable_notifications(user_id, timetable.shortname)
                self.send_message(user_id, src.messages.notification_disabled_text(timetable))
            else:
                self.notificationsdb.enable_notifications(user_id, timetable.shortname)
                self.send_message(user_id, src.messages.notification_enabled_text(timetable))
            self.notificationsdb.close()
                
            if callback in ['pravo_c1', 'pravo_c2', 'pravo_c3', 'pravo_c4']:
                self.send_message(user_id, 
                                  src.messages.main_menu_text(), 
                                  src.keyboards.pravo_keyboard(user_id))
            elif callback in ['ek_polit_c1', 'ek_polit_c2', 'ek_polit_c3', 'ek_polit_c4']:
                self.send_message(user_id, 
                                  src.messages.main_menu_text(), 
                                  src.keyboards.ek_polit_keyboard(user_id))
            elif callback in ['mag_c1', 'mag_c2']:
                self.send_message(user_id, 
                                  src.messages.main_menu_text(), 
                                  src.keyboards.mag_keyboard(user_id))
                
                
        if callback == 'stop':
            self.clientsdb.connect()
            self.clientsdb.remove_client(user_id)
            self.send_message(user_id, src.messages.stop_text())
            
    
    def send_message(self, user_id, text, keyboard=None):
        self.api.messages.send(access_token=vk_token, 
                              user_id=user_id, 
                              message=text, 
                              keyboard=keyboard)

        




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

bot = LFTableBot()

app = flask.Flask(__name__)

@app.route('/', methods=['POST'])
def main_handler():
    return(bot.handle_request(request))


if __name__ == '__main__':
    
    # Log message
    logger.info("the program was STARTED now")
    
    app.run(host='127.0.0.1', port=5080, use_reloader=False)
    
