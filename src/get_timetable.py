import urllib.request
from datetime import datetime
from flask import json
import src.static

def get_timetable(timetable_shortname):

    print(src.static.lftable_server_address + 
                             '/timetable?timetable_name=' + timetable_shortname)

    r = urllib.request.urlopen(src.static.lftable_server_address + 
                             '/timetable?timetable_name=' + timetable_shortname)
                            
    data = json.loads(r.read())

    return data

