import time
import src.static
import src.gettime
import datetime

# Each function in this module returns message text according to its name

# Will be romoved later.
missing_keyboard_warning = '⚠ Если Вы не видите клавиатуру, попробуйте использовать версию бота для Telegram — https://t.me/lftable_bot (или браузерную версию ВК).'

def main_text():
    text = '🗓 Выберите нужное действие.\n'

    text += missing_keyboard_warning

    return(text)

def start_text():
    text = '🗓 VK-LFTable v' + src.static.lftable_version + ': быстрый доступ к расписанию занятий юридического факультета БГУ.\n\n'

    text += '⚠ Управление ботом происходит посредством клавиатуры, однако на данный момент некоторые приложения ее не поддерживают.\n'
    text += 'Если вы не видите клавиатуру, вы можете настроить уведомления об обновлении расписания в браузерной версии ВК и получать их в любом ВК-клиенте (Или воспользоваться версией бота для Telegram — https://t.me/lftable_bot).'
    return(text)


def stop_text():
    text = '❗️ Отключены все уведомления, клавиатура скрыта. \n'
    text += '️⌨️ ️Чтобы снова начать работу с LFTable, напишите любое сообщение.'

    return(text)

def pravo_menu_text():
    text = '✏️ Правоведение ✏️\n\n'

    for ttb, course in zip([src.static.pravo_c1, src.static.pravo_c2,
                src.static.pravo_c3, src.static.pravo_c4], ['1️⃣', '2️⃣', '3️⃣', '4️⃣']):
                    text += str(course) + '-й курс: ' + ttb.url + ' - ' + src.gettime.ttb_gettime(ttb).strftime('%d.%m.%Y %H:%M') + '\n'
    text += '----------------\n'
    text += 'Информанция обновлена: ' + datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    return(text)

def ek_polit_menu_text():
    text = '✏️ Экономическое право и политология ✏️\n\n'

    for ttb, course in zip([src.static.ek_polit_c1, src.static.ek_polit_c2,
                src.static.ek_polit_c3, src.static.ek_polit_c4], ['1️⃣', '2️⃣', '3️⃣', '4️⃣']):
                    text += str(course) + '-й курс: ' + ttb.url + ' - ' + src.gettime.ttb_gettime(ttb).strftime('%d.%m.%Y %H:%M') + '\n'
    text += '----------------\n'
    text += 'Информанция обновлена: ' + datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    return(text)

def mag_menu_text():
    text = '✏️ Магистратура ✏️\n\n'

    for ttb, course in zip([src.static.mag_c1, src.static.mag_c2], ['1️⃣', '2️⃣']):
                    text += str(course) + '-й курс: ' + ttb.url + ' - ' + src.gettime.ttb_gettime(ttb).strftime('%d.%m.%Y %H:%M') + '\n'
    text += '----------------\n'
    text += 'Информанция обновлена: ' + datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    return(text)


def notification_enabled_text(ttb):
    text = '🔔 Включены уведомления для расписания "' + ttb.name + '".'

    return(text)


def notification_disabled_text(ttb):
    text = '🔕 Отключены уведомления для расписания "' + ttb.name + '".'

    return(text)


def notification_text(timetable, update_time):
    text = '🔔 Обновлено расписание "' + timetable.name + '" 🔔' + '\n\n'

    text += 'Дата обновления: ' + update_time.strftime('%d.%m.%Y') + '\n'
    text += 'Время обновления: ' + update_time.strftime('%H:%M') + '\n\n'

    text += '⬇️ Скачать: ' + timetable.url + '\n\n'

    return(text)
