import time
import src.static
import src.gettime


# Will be romoved later.
missing_keyboard_warning = '⚠ Если Вы не видите клавиатуру, попробуйте использовать браузерную версию VK (https://vk.com).'

def main_menu_text():
    text = '🗓🛠 Выберите нужное действие.\n'

    text += missing_keyboard_warning

    return(text)


def download_text():
    #text = 'Ссылки для загрузки файлов с расписаниями.\n\n'
    text = ''

    for ttb in src.static.all_timetables:

        text += '⬇️ "' + ttb.name + '" - ' + ttb.url + ' - ' + src.gettime.ttb_gettime(ttb).strftime('%d.%m.%Y %H:%M') + '\n'
        time.sleep(0.2)

    text += '\n' + missing_keyboard_warning

    return(text)


def start_text():
    # Send invitation
    text = '🗓 VK-LFTable v' + src.static.lftable_version + ': быстрый доступ к расписанию занятий юридического факультета БГУ.\n'
    text += "⌨️ Нажимте кнопку 'Start', чтобы начать работу.\n\n"

    text += '⚠ Управление ботом происходит посредством клавиатуры, однако на данный момент некоторые приложения ее не поддерживают.\n'
    text += 'Если вы не видите клавиатуру, вы можете настроить уведомления об обновлении расписания в браузерной версии VK и получать их в любом VK-клиенте.'
    return(text)


def stop_text():
    text = '❗️ Отключены все уведомления, клавиатура скрыта. \n'
    text += '️⌨️ ️Чтобы снова начать работу с LFTable, напишите любое сообщение.'

    return(text)


def notification_enabled_text(ttb):
    text = '🕑🔔 Включены уведомления для расписания "' + ttb.name + '".'

    return(text)


def notification_disabled_text(ttb):
    text = '🕑🔕 Отключены уведомления для расписания "' + ttb.name + '".'

    return(text)


def notification_text(user_id, ttb, update_time):
    text = '🔔 Обновлено расписание "' + ttb.name + '" 🔔' + '\n'
    text += 'Дата обновления: ' + update_time.strftime('%d.%m.%Y') + '\n'
    text += 'Время обновления: ' + update_time.strftime('%H:%M') + '\n'
    text += '⬇️ Скачать: ' + ttb.url + '\n\n'

    #text += missing_keyboard_warning

    return(text)
