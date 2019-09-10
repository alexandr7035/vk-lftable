import time
import src.static
import src.gettime

# Each function in this module returns message text according to its name

# Will be romoved later.
missing_keyboard_warning = '⚠ Если Вы не видите клавиатуру, попробуйте использовать версию бота для Telegram — https://t.me/lftable_bot (или браузерную версию ВК).'

def main_text():
    text = '🗓 Выберите нужное действие.\n'

    text += missing_keyboard_warning

    return(text)


def download_text():
    text = ''

    for ttb in src.static.all_timetables:

        text += '⬇️ "' + ttb.name + '" - ' + ttb.url + ' - ' + src.gettime.ttb_gettime(ttb).strftime('%d.%m.%Y %H:%M') + '\n'
        time.sleep(src.static.download_interval)

    text += '\n' + missing_keyboard_warning

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
