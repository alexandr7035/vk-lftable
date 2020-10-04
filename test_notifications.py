import os
import sqlite3
import src.static
import src.db_classes

# Writes old times to the db for all timetables
#
# WARNING!!!
# Notifications are sent to all active users
# Do not use in prodution enviroment
#

WARNING_TEXT = "Warning!!! Notifications will be sent to all active users!\n"
WARNING_TEXT += "Do NOT use the script in production enviroment.\n"
WARNING_TEXT += "Would you like to continue? (y/N): "

TEST_DATE = '01.01.2000 12:00:00'

if __name__ == "__main__":
    
    if input(WARNING_TEXT).lower() != "y":
        print("\nExit.")

    db = src.db_classes.TimesDB()
    db.connect()
    
    try:
        for ttb in src.static.all_timetables:
            db.write_time(ttb.shortname, TEST_DATE)
    except sqlite3.OperationalError:
        print("\n[!] Can't update time in the db. Exit.")
        print("(Check if you have write permissions first)")

    print("\nDone. Exit.")
    

