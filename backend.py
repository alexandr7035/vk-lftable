# Backend file
# Work with databases and etc

import os
import sqlite3
from static import *
import ssl
import urllib.request
from datetime import datetime
import pytz

def first_run_check():
    
    try:
        os.mkdir(db_dir)
    except Exception:
        pass
    
    
    
    # Create database for users notified about timetables' updates.
    # 4 tables for each timetable, each with 'users' column
    if not os.path.exists(notifications_db):
        print(notifications_db)
        conn = sqlite3.connect(notifications_db)
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
        
        
        
    # Database for all clients.
    if not os.path.exists(clients_db):
        conn = sqlite3.connect(clients_db)

        cursor = conn.cursor()
        
        cursor.execute('CREATE TABLE clients (user_id)')
        
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
    conn = sqlite3.connect(notifications_db)
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
           
           
# Checks if user is client
def check_user_is_client(user_id):
    
    # Connect to users db.
    conn = sqlite3.connect(clients_db)
    cursor = conn.cursor()
        
    cursor.execute('SELECT user_id FROM clients')
    result = cursor.fetchall()
        
    conn.close()
    
    # List for users notifed about current ttb updates.
    
    
    
    clients_list = []
    for i in result:
       clients_list.append(i[0])
    
   
    
    if str(user_id) in clients_list:
           return True
    else:
           return False

