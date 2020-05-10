#!/usr/bin/env python3

import os
import sys
import time
import atexit
from datetime import datetime

import vk
from flask import json
from apscheduler.schedulers.background import BackgroundScheduler

# See 'src/' directory
import src.static
import src.messages
import src.keyboards
import src.db_classes
from src.logger import *


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


class LFTableBot():
    def __init__(self):

        logger.info("-")
        logger.info("vk-lftable was STARTED now")

        # VK
        session = vk.Session()
        self.api = vk.API(session, v=src.static.vk_api_version)

        # Objects to access the databases
        self.timesdb = src.db_classes.TimesDB()
        self.notificationsdb = src.db_classes.NotificationsDB()
        self.statisticsdb = src.db_classes.StatisticsDB()

        # Create necessary directories and files
        self.prepare_workspace()

        # Sets times to the TimesDB immediately after the run WITHOUT notifiying users
        # This is to prevent late notifications if the bot was down for a long time
        self.timesdb.connect()
        for timetable in src.static.all_timetables:

            # Get ttb update time from law.bsu.by
            # Use different gettime functions for ussual and credit/exam timetables. See src.gettime.py
            if timetable in src.static.credit_exam_timetables:
                data = src.gettime.credit_exam_gettime(timetable)
                update_time = data['time'].strftime('%d.%m.%Y %H:%M:%S')
            else:
                update_time = src.gettime.ttb_gettime(timetable).strftime('%d.%m.%Y %H:%M:%S')
            
            self.timesdb.write_time(timetable.shortname, update_time)
        self.timesdb.close()

        # Timejob for notifications
        # Use 'atexit' to shut down the scheduler when exiting the app
        scheduler = BackgroundScheduler()
        scheduler.add_job(func=self.notifications_timejob,
                          trigger="interval",
                          seconds=src.static.check_updates_interval)
        scheduler.start()
        atexit.register(lambda: scheduler.shutdown())

    # Create necessary directories and files
    def prepare_workspace(self):

        # Create directory for sqlite3 databases
        if not os.path.exists(src.static.db_dir):
            os.mkdir(src.static.db_dir)
            logger.info("'" + src.static.db_dir + "' directory was created")

        # Create databases. See db_classes.py (especially 'construct()' methods)
        #TimesDB
        if not os.path.isfile(src.static.timesdb_path):
            self.timesdb.connect()
            self.timesdb.construct()
            self.timesdb.close()

            logger.info("'" + src.static.timesdb_path + "' database was created")

        # NotificationsDB
        if not os.path.isfile(src.static.notificationsdb_path):
            self.notificationsdb.connect()
            self.notificationsdb.construct()
            self.notificationsdb.close()

            logger.info("'" + src.static.notificationsdb_path + "' database was created")

        # StatisticsDB
        if not os.path.isfile(src.static.statisticsdb_path):
            self.statisticsdb.connect()
            self.statisticsdb.construct()
            self.statisticsdb.close()

            logger.info("'" + src.static.statisticsdb_path + "' database was created")

    # Each request that flask (app.py) receives is passed as an argument to this function
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

            # Get user id
            user_id = str(data['object']['from_id'])

            # Prevent answers to old requests if bot was down
            # See src.static.max_request_delay
            request_time = data['object']['date']
            requeste = data['object']['date']
            if request_time <= round(time.time()) - src.static.max_request_delay:
                logger.info("skipped request: user_id=" + user_id + ", time=" + str(request_time))
                return('ok')

            self.statisticsdb.connect()

            # If user is active (pressed 'start' before)
            if self.statisticsdb.check_if_user_is_active(user_id) is True:

                # That means a button was pressed
                if data['object'].get('payload'):
                    callback = json.loads(data['object']['payload'])['button']
                    # Call method wich handles button click
                    self.handle_button_callback(user_id, callback)
                # Usual message was sent
                else:
                    self.send_message(user_id,
                                     src.messages.main_text(),
                                     src.keyboards.main_keyboard())

            # If user is not active
            else:
                # Make user active if he pressed 'start' button
                if data['object'].get('payload') and json.loads(data['object']['payload'])['button'] == 'start':

                    # Add user id to unique_users table (if there is no)
                    if user_id not in self.statisticsdb.get_unique_users():
                        logger.info("add unique user " + user_id)
                        self.statisticsdb.add_unique_user(user_id)

                    # Add user id to 'active_users' table
                    self.statisticsdb.add_active_user(user_id)
                    logger.info("user " + user_id + " is now active")
                    self.send_message(user_id,
                                      src.messages.main_text(),
                                      src.keyboards.main_keyboard())
                # Send invitation again and again until 'start' button is pressed
                else:
                    self.send_message(user_id,
                                      src.messages.start_text(),
                                      src.keyboards.start_keyboard())

            self.statisticsdb.close()

        # This reply is necessary for vk
        return 'ok'

    # Method wich handles button  (except 'start' button)
    def handle_button_callback(self, user_id, callback):

        # Show main menu
        if callback == 'main_menu':
            self.send_message(user_id, src.messages.main_text(), src.keyboards.main_keyboard())

        # Message with links to download timetable
        if callback == 'download':
            self.send_message(user_id, src.messages.download_text(), src.keyboards.download_keyboard())

        # Show menus for specialties (keyboard contains timetable buttons
        if callback in ['pravo_menu', 'ek_polit_menu', 'mag_menu', 'credits_menu', 'exams_menu', 
                        'refresh_pravo', 'refresh_ek_polit', 'refresh_mag', 'refresh_credits', 'refresh_exams']:

            if callback in ['pravo_menu', 'refresh_pravo']:
                self.send_message(user_id,
                                  src.messages.pravo_menu_text(),
                                  src.keyboards.pravo_keyboard(user_id))
            elif callback in ['ek_polit_menu', 'refresh_ek_polit']:
                self.send_message(user_id,
                                  src.messages.ek_polit_menu_text(),
                                  src.keyboards.ek_polit_keyboard(user_id))
            elif callback in ['mag_menu', 'refresh_mag']:
                self.send_message(user_id,
                                  src.messages.mag_menu_text(),
                                  src.keyboards.mag_keyboard(user_id))

            elif callback in ['credits_menu', 'refresh_credits']:
                self.send_message(user_id,
                                  src.messages.credits_menu_text(),
                                  src.keyboards.credits_keyboard(user_id))

            elif callback in ['exams_menu', 'refresh_exams']:
                self.send_message(user_id,
                                  src.messages.exams_menu_text(),
                                  src.keyboards.exams_keyboard(user_id))
            

        # If timetable button was pressed update keyboard with enable/disable notifications buttons
        if  callback in ['pravo_c1', 'pravo_c2', 'pravo_c3', 'pravo_c4',
                         'ek_polit_c1', 'ek_polit_c2', 'ek_polit_c3', 'ek_polit_c4',
                         'mag_c1', 'mag_c2',
                         'exam_c1', 'exam_c2', 'exam_c3', 'exam_c4',
                         'credit_c1', 'credit_c2', 'credit_c3', 'credit_c4']:

            # See TTB objects in src/static.py
            timetable = getattr(src.static, callback)

            # Enable/disable notifications
            self.notificationsdb.connect()
            if self.notificationsdb.check_if_user_notified(user_id, timetable.shortname) is True:
                self.notificationsdb.disable_notifications(user_id, timetable.shortname)
                logger.info('user ' + user_id + " disabled notifications for the '" + timetable.shortname + "' timetable")
                self.send_message(user_id, src.messages.notification_disabled_text(timetable))
            else:
                self.notificationsdb.enable_notifications(user_id, timetable.shortname)
                logger.info('user ' + user_id + " enabled notifications for the '" + timetable.shortname + "' timetable")
                self.send_message(user_id, src.messages.notification_enabled_text(timetable))
            self.notificationsdb.close()

            # Choose speciality message and show it again (with updated buttons)
            if callback in ['pravo_c1', 'pravo_c2', 'pravo_c3', 'pravo_c4']:
                self.send_message(user_id,
                                  src.messages.pravo_menu_text(),
                                  src.keyboards.pravo_keyboard(user_id))
            elif callback in ['ek_polit_c1', 'ek_polit_c2', 'ek_polit_c3', 'ek_polit_c4']:
                self.send_message(user_id,
                                  src.messages.ek_polit_menu_text(),
                                  src.keyboards.ek_polit_keyboard(user_id))
            elif callback in ['mag_c1', 'mag_c2']:
                self.send_message(user_id,
                                  src.messages.mag_menu_text(),
                                  src.keyboards.mag_keyboard(user_id))
            elif callback in ['credit_c1', 'credit_c2', 'credit_c3', 'credit_c4']:
                self.send_message(user_id,
                                src.messages.credits_menu_text(),
                                src.keyboards.credits_keyboard(user_id))

            elif callback in ['exam_c1', 'exam_c2', 'exam_c3', 'exam_c4']:
                self.send_message(user_id,
                                src.messages.exams_menu_text(),
                                src.keyboards.exams_keyboard(user_id))

        # 'Stop' button. Make user non-active until 'start' button is pressed again
        if callback == 'stop':
            self.statisticsdb.remove_active_user(user_id)
            logger.info("user " + user_id + " is now non-active")
            self.send_message(user_id, src.messages.stop_text())

    def send_message(self, user_id, text, keyboard=None):
        self.api.messages.send(access_token=vk_token,
                              user_id=user_id,
                              message=text,
                              keyboard=keyboard,
                              dont_parse_links=1)

    def notifications_timejob(self):
        print('Checking for ttb updates was started: ', datetime.now().strftime("%d.%m.%Y %Y %H:%M:%S"))

        # Connect to the times.db
        self.timesdb.connect()

        # See 'all_timetables' list in 'src/static.py'
        for checking_ttb in src.static.all_timetables:

            # Get timetable update time from law.bsu.by
            # Use different gettime functions for ussual and credit/exam timetables. See src.gettime.py
            if checking_ttb in src.static.credit_exam_timetables:
                data = src.gettime.credit_exam_gettime(checking_ttb)
                update_time = data['time'].strftime('%d.%m.%Y %H:%M:%S')
                timetable_url = data['url']
            else:
                update_time = src.gettime.ttb_gettime(checking_ttb).strftime('%d.%m.%Y %H:%M:%S')
                timetable_url = checking_ttb.url


            # Get old update time from the TimesDB.
            old_update_time = self.timesdb.get_time(checking_ttb.shortname)

            # Convert date strings to datetime objects
            dt_update_time = datetime.strptime(update_time, '%d.%m.%Y %H:%M:%S')
            dt_old_update_time = datetime.strptime(old_update_time, '%d.%m.%Y %H:%M:%S')

            # Compare the two dates
            # If timetable was updated send a notification to users who enabled notifications for this timetable
            if dt_update_time > dt_old_update_time:

                logger.info("'" + checking_ttb.shortname + "' timetable was updated at " + update_time)

                # Get list of users who enabled notifications for this timetable
                self.notificationsdb.connect()
                users_to_notify = self.notificationsdb.get_notified_users(checking_ttb.shortname)
                self.notificationsdb.close()

                # Send a notification to each user.
                for user_id in users_to_notify:

                    self.statisticsdb.connect()
                    # Send only if user is active
                    if self.statisticsdb.check_if_user_is_active(user_id) is True:

                        try:
                            self.send_message(user_id,
                                            src.messages.notification_text(checking_ttb, dt_update_time, timetable_url),
                                            src.keyboards.notification_keyboard())
                            logger.info("'" + checking_ttb.shortname + "' notification was sent to user " + user_id)
                        # If user blocked this bot & etc...
                        except Exception as e:
                            logger.info("can't send '" + checking_ttb.shortname + "' notification to user " + user_id + ", skip. EXCEPTION: " + str(e))
                            continue

                    # Write to log if user is not active
                    else:
                        logger.info("user " + user_id + " is not active now, skip '" + checking_ttb.shortname + "' notification")

                    self.statisticsdb.close()


                    # A delay to prevent any spam control exceptions
                    time.sleep(src.static.send_message_interval)

                # Write new update time to the database.
                self.timesdb.write_time(checking_ttb.shortname, update_time)

            # A delay to prevent any spam control exceptions
            time.sleep(src.static.send_message_interval)

        # Close 'times.db' until next check.
        self.timesdb.close()
