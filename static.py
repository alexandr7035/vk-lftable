# Class for storing timetable's options.
class TTBS():
    pass

# API version
vk_api_version = 5.90

# Databases.
db_dir = 'db/'
notifications_db = db_dir + 'notifications.db'
times_db = db_dir + 'times.db'
clients_db = db_dir + 'clients.db'

# Intervals for update checks and notifications(s).
check_updates_interval = 120
send_message_interval = 2
next_timetable_interval = 5

# All types of timetables
pravo_c1 = TTBS()
pravo_c2 = TTBS()
pravo_c3 = TTBS()
pravo_c4 = TTBS()
mag_c1 = TTBS()
mag_c2 = TTBS()

all_timetables = [pravo_c1, pravo_c2, pravo_c3, pravo_c4, mag_c1, mag_c2]

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

mag_c1.url = 'https://law.bsu.by/pub/2/Raspisanie_mag_1_kurs.xls'
mag_c1.name = 'Магистратура, 1-й курс'
mag_c1.shortname = 'mag_c1'

mag_c2.url = 'https://law.bsu.by/pub/2/Raspisanie_mag_2_kurs.xls'
mag_c2.name = 'Магистратура, 2-й курс'
mag_c2.shortname = 'mag_c2'
