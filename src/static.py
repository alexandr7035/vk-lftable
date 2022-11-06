# Version number
lftable_version = '4.3'

# API version
vk_api_version = '5.90'

# LFTable server address
lftable_server_address = 'http://api.lftable.site'

# Pathes
db_dir = 'db/'
notificationsdb_path = db_dir + 'notifications.db'
timesdb_path = db_dir + 'times.db'
clientsdb_path = db_dir + 'clients.db'
statisticsdb_path = db_dir + 'statistics.db'
log_dir = 'log/'
log_file = log_dir + 'lftable.log'

# Intervals (s)
check_updates_interval = 40
send_message_interval = 0.055
max_request_delay = 5

# Class to store timetable options
class Timetable():
    pass

# All types of timetables for all courses
pravo_c1 = Timetable()
pravo_c2 = Timetable()
pravo_c3 = Timetable()
pravo_c4 = Timetable()
mag_c1 = Timetable()
ek_polit_c1 = Timetable()
ek_polit_c2 = Timetable()
ek_polit_c3 = Timetable()
ek_polit_c4 = Timetable()
credit_c1 = Timetable()
exam_c1 = Timetable()
credit_c2 = Timetable()
exam_c2 = Timetable()
credit_c3 = Timetable()
exam_c3 = Timetable()
credit_c4 = Timetable()
exam_c4 = Timetable()

# Timetable data
pravo_c1.name = 'Правоведение, 1-й курс'
pravo_c1.shortname = 'pravo_c1'

pravo_c2.name = 'Правоведение, 2-й курс'
pravo_c2.shortname = 'pravo_c2'

pravo_c3.name = 'Правоведение, 3-й курс'
pravo_c3.shortname = 'pravo_c3'

pravo_c4.name = 'Правоведение, 4-й курс'
pravo_c4.shortname = 'pravo_c4'

ek_polit_c1.name = 'Экономическое право и политология, 1-й курс'
ek_polit_c1.shortname = 'ek_polit_c1'

ek_polit_c2.name = 'Экономическое право и политология, 2-й курс'
ek_polit_c2.shortname = 'ek_polit_c2'

ek_polit_c3.name = 'Экономическое право и политология, 3-й курс'
ek_polit_c3.shortname = 'ek_polit_c3'

ek_polit_c4.name = 'Экономическое право и политология, 4-й курс'
ek_polit_c4.shortname = 'ek_polit_c4'

mag_c1.name = 'Магистратура, 1-й курс'
mag_c1.shortname = 'mag_c1'

credit_c1.name = 'Зачеты, 1-й курс'
credit_c1.shortname = 'credit_c1'

credit_c2.name = 'Зачеты, 2-й курс'
credit_c2.shortname = 'credit_c2'

credit_c3.name = 'Зачеты, 3-й курс'
credit_c3.shortname = 'credit_c3'

credit_c4.name = 'Зачеты, 4-й курс'
credit_c4.shortname = 'credit_c4'

exam_c1.name = 'Экзамены, 1-й курс'
exam_c1.shortname = 'exam_c1'

exam_c2.name = 'Экзамены, 2-й курс'
exam_c2.shortname = 'exam_c2'

exam_c3.name = 'Экзамены, 3-й курс'
exam_c3.shortname = 'exam_c3'

exam_c4.name = 'Экзамены, 4-й курс'
exam_c4.shortname = 'exam_c4'


# List to simplify 'for' loops (in order not to write all timetables many times)
all_timetables = [pravo_c1, pravo_c2, pravo_c3, pravo_c4, 
                 ek_polit_c1, ek_polit_c2, ek_polit_c3, ek_polit_c4,
                 mag_c1,
                 credit_c1, credit_c2, credit_c3, credit_c4, 
                 exam_c1, exam_c2, exam_c3, exam_c4]


# Possible button colors for vk api
# Dictionary allows to use friendly color names 
button_colors_dict = {'red':'negative', 
                     'green':'positive',
                     'blue':'primary',
                     'white':'secondary',
}

# If no color specified, src.keyboards.create_button() function uses this value
default_button_color = 'green'
