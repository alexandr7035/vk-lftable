#!./venv/bin/python3

import sqlite3
# Database with upate times of each timetable
from static import times_db
# List of all timetables
from static import all_timetables

conn = sqlite3.connect(times_db)
cursor = conn.cursor()

# Set wrong old times to the times db in order to check whether notifications work correctly
for ttb in all_timetables:
	cursor.execute("UPDATE times SET time = '01.01.2001 00:00:00' WHERE ttb = ?", (ttb.shortname,))

conn.commit()
conn.close()
