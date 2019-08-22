# Version number
lftable_version = '3.0'

# API version
vk_api_version = 5.90

# Pathes
db_dir = 'db/'
notificationsdb_path = db_dir + 'notifications.db'
timesdb_path = db_dir + 'times.db'
clientsdb_path = db_dir + 'clients.db'
statisticsdb_path = db_dir + 'statistics.db'
log_dir = 'log/'
log_file = log_dir + 'lftable.log'

# Intervals (s)
check_updates_interval = 120
send_message_interval = 2
max_request_delay = 5

# For download buttom to prevent spam control
download_interval = 0.01

# Class to store timetable options
class TTB():
    pass

# All types of timetables for all courses
pravo_c1 = TTB()
pravo_c2 = TTB()
pravo_c3 = TTB()
pravo_c4 = TTB()
mag_c1 = TTB()
mag_c2 = TTB()
ek_polit_c1 = TTB()
ek_polit_c2 = TTB()
ek_polit_c3 = TTB()
ek_polit_c4 = TTB()

# List to simplify 'for' loops (in order not to write all timetables many times)
all_timetables = [pravo_c1, pravo_c2, pravo_c3, pravo_c4, 
                 ek_polit_c1, ek_polit_c2, ek_polit_c3, ek_polit_c4,
                 mag_c1, mag_c2]

# Timetable data
pravo_c1.url = 'https://law.bsu.by/pub/2/Raspisanie_1_pravo.xls'
pravo_c1.name = 'Правоведение, 1-й курс'
pravo_c1.shortname = 'pravo_c1'

pravo_c2.url = 'https://law.bsu.by/pub/2/Raspisanie_2_pravo.xls'
pravo_c2.name = 'Правоведение, 2-й курс'
pravo_c2.shortname = 'pravo_c2'

pravo_c3.url = 'https://law.bsu.by/pub/2/Raspisanie_3_pravo.xls'
pravo_c3.name = 'Правоведение, 3-й курс'
pravo_c3.shortname = 'pravo_c3'

pravo_c4.url = 'https://law.bsu.by/pub/2/Raspisanie_4_pravo.xls'
pravo_c4.name = 'Правоведение, 4-й курс'
pravo_c4.shortname = 'pravo_c4'

ek_polit_c1.url = 'https://law.bsu.by/pub/2/Raspisanie_1_ek_polit.xls'
ek_polit_c1.name = 'Экономическое право и политология, 1-й курс'
ek_polit_c1.shortname = 'ek_polit_c1'

ek_polit_c2.url = 'https://law.bsu.by/pub/2/Raspisanie_2_ek_polit.xls'
ek_polit_c2.name = 'Экономическое право и политология, 2-й курс'
ek_polit_c2.shortname = 'ek_polit_c2'

ek_polit_c3.url = 'https://law.bsu.by/pub/2/Raspisanie_3_ek_polit.xls'
ek_polit_c3.name = 'Экономическое право и политология, 3-й курс'
ek_polit_c3.shortname = 'ek_polit_c3'

ek_polit_c4.url = 'https://law.bsu.by/pub/2/Raspisanie_4_ek_polit.xls'
ek_polit_c4.name = 'Экономическое право и политология, 4-й курс'
ek_polit_c4.shortname = 'ek_polit_c4'

mag_c1.url = 'https://law.bsu.by/pub/2/Raspisanie_mag_1_kurs.xls'
mag_c1.name = 'Магистратура, 1-й курс'
mag_c1.shortname = 'mag_c1'

mag_c2.url = 'https://law.bsu.by/pub/2/Raspisanie_mag_2_kurs.xls'
mag_c2.name = 'Магистратура, 2-й курс'
mag_c2.shortname = 'mag_c2'

# Possible button colors for vk api
# Dictionary allows to use friendly color names 
button_colors_dict = {'red':'negative', 
                     'green':'positive',
                     'blue':'primary',
                     'white':'secondary',
}

# If no color specified, src.keyboards.create_button() function uses this value
default_button_color = 'green'
