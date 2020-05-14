from flask import json
import src.static
import src.db_classes


# Function to create a button
def create_button(button_text, button_callback, color=src.static.default_button_color):

    button = {
        "action": {
        "type": "text",
        "payload": '{\"button\": \"' + button_callback + '\"}',
        "label": button_text
        },
        "color": src.static.button_colors_dict[color]
        }

    return(button)

# Timetable button may have two colors, so use separate function but based on create_button()
def create_timetable_button(text, callback, user_id):
    notificationsdb = src.db_classes.NotificationsDB()
    notificationsdb.connect()

    timetable_shortname = callback

    if notificationsdb.check_if_user_notified(user_id, timetable_shortname) is not True:
        return(create_button(text + ' 🔔', callback))
    else:
        return(create_button(text + ' 🔕', callback, 'red'))

    notificationsdb.close()


# Keyboard for main menu
def main_keyboard():
    pravo_btn = create_button('📕 Правоведение', 'pravo_menu')
    ek_polit_btn = create_button('📗 Эк. и полит.', 'ek_polit_menu')
    mag_btn  = create_button('📒 Магистратура', 'mag_menu')
    stop_btn = create_button('Отключить 🚫', 'stop')

    credits_btn = create_button("💀 Зачеты", "credits_menu")
    exams_btn = create_button("☠️ Экзамены", "exams_menu")

    keyboard = {
    "one_time": True,
    "buttons": [[pravo_btn, ek_polit_btn],
                [mag_btn, credits_btn],
                [exams_btn, stop_btn]]
    }

    return(json.dumps(keyboard, ensure_ascii=False).encode("utf-8"))

# Keyboards for specialities
def pravo_keyboard(user_id):
    pravo_c1_btn = create_timetable_button('Прав. - 1⃣', src.static.pravo_c1.shortname, user_id)
    pravo_c2_btn = create_timetable_button('Прав. - 2⃣', src.static.pravo_c2.shortname, user_id)
    pravo_c3_btn = create_timetable_button('Прав. - 3⃣', src.static.pravo_c3.shortname, user_id)
    pravo_c4_btn = create_timetable_button('Прав. - 4⃣', src.static.pravo_c4.shortname, user_id)
    back_button = create_button('⬅️ Назад', 'main_menu')
    refresh_btn = create_button('Обновить 🔄', 'refresh_pravo')

    keyboard = {
    "one_time": True,
    "buttons": [[pravo_c1_btn, pravo_c2_btn],
                [pravo_c3_btn, pravo_c4_btn],
                [back_button, refresh_btn]]

    }

    return(json.dumps(keyboard, ensure_ascii=False).encode("utf-8"))


def ek_polit_keyboard(user_id):
    ek_polit_c1_btn = create_timetable_button('Эк-полит. - 1⃣', src.static.ek_polit_c1.shortname, user_id)
    ek_polit_c2_btn = create_timetable_button('Эк-полит. - 2⃣', src.static.ek_polit_c2.shortname, user_id)
    ek_polit_c3_btn = create_timetable_button('Эк-полит. - 3⃣', src.static.ek_polit_c3.shortname, user_id)
    ek_polit_c4_btn = create_timetable_button('Эк-полит. - 4⃣', src.static.ek_polit_c4.shortname, user_id)
    back_button = create_button('⬅️ Назад', 'main_menu')
    refresh_btn = create_button('Обновить 🔄', 'refresh_ek_polit')

    keyboard = {
    "one_time": True,
    "buttons": [[ek_polit_c1_btn, ek_polit_c2_btn],
                [ek_polit_c3_btn, ek_polit_c4_btn],
                [back_button, refresh_btn]]
    }

    return(json.dumps(keyboard, ensure_ascii=False).encode("utf-8"))


def mag_keyboard(user_id):
    mag_c1_btn = create_timetable_button('Маг. - 1⃣', src.static.mag_c1.shortname, user_id)
    mag_c2_btn = create_timetable_button('Маг. - 2⃣', src.static.mag_c2.shortname, user_id)
    refresh_btn = create_button('Обновить 🔄', 'refresh_mag')
    back_button = create_button('⬅️ Назад', 'main_menu')

    keyboard = {
    "one_time": True,
    "buttons": [[mag_c1_btn, mag_c2_btn],
                [back_button, refresh_btn]]
    }

    return(json.dumps(keyboard, ensure_ascii=False).encode("utf-8"))


def credits_keyboard(user_id):
    credit_c1_btn = create_timetable_button('Зачеты - 1⃣', src.static.credit_c1.shortname, user_id)
    credit_c2_btn = create_timetable_button('Зачеты - 2️⃣', src.static.credit_c2.shortname, user_id)
    credit_c3_btn = create_timetable_button('Зачеты - 3️⃣', src.static.credit_c3.shortname, user_id)
    credit_c4_btn = create_timetable_button('Зачеты - 4️⃣', src.static.credit_c4.shortname, user_id)

    back_button = create_button('⬅️ Назад', 'main_menu')
    refresh_btn = create_button('Обновить 🔄', 'refresh_credits')

    keyboard = {
    "one_time": True,
    "buttons": [[credit_c1_btn, credit_c2_btn],
                [credit_c3_btn, credit_c4_btn],
                [back_button, refresh_btn]]

    }

    return(json.dumps(keyboard, ensure_ascii=False).encode("utf-8"))


def exams_keyboard(user_id):
    exam_c1_btn = create_timetable_button('Экзамены - 1⃣', src.static.exam_c1.shortname, user_id)
    exam_c2_btn = create_timetable_button('Экзамены - 2️⃣', src.static.exam_c2.shortname, user_id)
    exam_c3_btn = create_timetable_button('Экзамены - 3️⃣', src.static.exam_c3.shortname, user_id)
    exam_c4_btn = create_timetable_button('Экзамены - 4️⃣', src.static.exam_c4.shortname, user_id)

    back_button = create_button('⬅️ Назад', 'main_menu')
    refresh_btn = create_button('Обновить 🔄', 'refresh_exams')

    keyboard = {
    "one_time": True,
    "buttons": [[exam_c1_btn, exam_c2_btn],
                [exam_c3_btn, exam_c4_btn],
                [back_button, refresh_btn]]

    }

    return(json.dumps(keyboard, ensure_ascii=False).encode("utf-8"))


# Keyboard for a notification (only 'back' button to show main menu)
def back_to_main_menu_keyboard():
    back_button = create_button('⬅ В меню', 'main_menu', 'green')

    keyboard = {
    "one_time": True,
    "buttons": [[back_button]]

    }

    return(json.dumps(keyboard, ensure_ascii=False).encode("utf-8"))


def start_keyboard():

    start_button = create_button('🗓 Start', 'start')

    keyboard = {
    "one_time": True,
    "buttons": [[start_button]]

    }

    return(json.dumps(keyboard, ensure_ascii=False).encode("utf-8"))

