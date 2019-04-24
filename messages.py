######################### Mesages ######################################

# Will be romoved later.
missing_keyboard_warning = '⚠ Если Вы не видите клавиатуру, попробуйте использовать браузерную версию VK (https://vk.com).'

def main_text():
    text = '🛠 Выберите нужное действие. 🛠\n'
    text += "\n"
    
    text += missing_keyboard_warning

    return(text)


def download_text():
    text = 'Ссылки для загрузки файлов с расписаниями.\n\n'

    for ttb in all_timetables:

        text += '⬇️ "' + ttb.name + '" - ' + ttb.url + ' - ' + ttb_gettime(ttb).strftime('%d.%m.%Y %H:%M') + '\n'
        time.sleep(0.2)
    
    text += '\n' + missing_keyboard_warning
    
    return(text)


def start_text():
    # Send invitation
    text = '🗓 LFTable-bot: быстрый доступ к расписанию занятий юридического факультета БГУ.\n'
    text += "⌨️ Введите '/start', чтобы начать работу.\n\n"
    
    text += '⚠ Управление ботом происходит посредством коавиатуры, однако на данный момент многие приложения, включая Kate Mobile и VK mp3, ее не поддерживают.\n'
    text += 'Если вы не видите клавиатуру, вы можете настроить уведомления об обновлении расписания в браузерной версии VK и получать их в любом VK-клиенте.'
    return(text)
    
    
def stopped_text():
    text = '❗️ Отключены все уведомления, клавиатура скрыта. \n'
    text += '️⌨️ ️Чтобы снова начать работу с LFTable, напишите любое сообщение'
    
    return(text)


def notification_enabled_text(ttb):
    text = '✅ Включены уведомления для расписания "' + ttb.name + '".'

    return(text)    


def notification_disabled_text(ttb):
    text = '❎ Отключены уведомления для расписания "' + ttb.name + '".'

    return(text)
