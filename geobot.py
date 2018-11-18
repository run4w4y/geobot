import logging
import ast
import telegram
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from geobot_config import geobot_token, adminlist

teams = {}

bot = telegram.Bot(token=geobot_token)
updater = Updater(token=geobot_token)
dispatcher = updater.dispatcher


def save_teams():
    global teams
    with open('teams.txt', 'w') as f:
        f.write(str(teams))


def read_teams():
    global teams
    with open('teams.txt', 'r') as f:
        teams_string = f.read()
        teams = ast.literal_eval(teams_string)


def start(bot, update):
    chat = update.message.chat_id
    user = update.message.from_user
    print(user['username'] + ' (' + str(chat) + ') -- ', '/start')
    bot.send_message(chat_id=update.message.chat_id, text="Здравствуйте! Начните работу с ознакомления "
                                                          "с возможностями бота при помощи команды /help")


def add_team(bot, update):
    chat = update.message.chat_id
    bot.send_message(chat_id=chat, text='Как вы хотите назвать команду?')
    user = update.message.from_user
    print(user['username'] + ' (' + str(chat) + ') -- ', '/add_team')
    return 0


def ask_team(bot, update):
    chat = update.message.chat_id
    team_name = update.message.text
    if team_name not in teams.keys():
        teams[team_name] = []
        bot.send_message(chat_id=chat, text='Команда успешно создана!')
        print(teams)
    else:
        bot.send_message(chat_id=chat, text='Такая команда уже есть! Попробуйте еще раз')
    save_teams()
    return ConversationHandler.END


def join_team(bot, update):
    chat = update.message.chat_id
    user = update.message.from_user
    print(user['username'] + ' (' + str(chat) + ') -- ', '/join_team')

    if not list(teams.keys()):
        bot.send_message(chat_id=chat, text='Пока что нет ни одной команды, в которую вы могли бы вступить')
        return ConversationHandler.END

    reply_markup = [[i for i in list(teams.keys())]]
    bot.send_message(chat_id=chat, text='Выберите команду, в которую хотите вступить',
                     reply_markup=ReplyKeyboardMarkup(reply_markup, one_time_keyboard=True))
    return 1


def add_user(bot, update):
    chat = update.message.chat_id
    user = update.message.from_user
    j_team = update.message.text
    if teams.get(j_team) is not None:
        if user['username'] not in teams[j_team]:
            bl = list(map(lambda x: 1 if user['username'] in teams[x] else 0, teams.keys()))
            if sum(bl) == 0:
                bot.send_message(chat_id=chat, text='Вы успешно вступили в команду ' + j_team + '!',
                                 reply_markup=ReplyKeyboardRemove())
                teams[j_team].append(user['username'])
                print(teams)
            else:
                prev_team = list(teams.keys())[bl.index(1)]
                bot.send_message(chat_id=chat, text='Вы успешно перешли в команду ' + j_team + ' из команды '
                                                    + str(prev_team) + '!', reply_markup=ReplyKeyboardRemove())
                teams[prev_team].pop(teams[prev_team].index(user['username']))
                teams[j_team].append(user['username'])
                print(teams)
        else:
            bot.send_message(chat_id=chat, text='Вы уже вступили в эту команду!',
                             reply_markup=ReplyKeyboardRemove())
    else:
        bot.send_message(chat_id=chat, text='Команда не найдена!', reply_markup=ReplyKeyboardRemove())
    save_teams()
    return ConversationHandler.END


def show_teams(bot, update):
    chat = update.message.chat_id
    user = update.message.from_user
    print(user['username'] + ' (' + str(chat) + ') -- ', '/show_teams')
    reply_msg = '<b>Список команд:</b> \n\n'
    c = 0
    for i in teams.items():
        c += 1
        if user['username'] in i[1]:
            reply_msg += str(c) + '. <b>' + i[0] + '</b>: '
        else:
            reply_msg += str(c) + '. ' + i[0] + ': '
        reply_msg += str(len(i[1]))
        if 1 < len(i[1]) < 5:
            reply_msg += ' человека'
        else:
            reply_msg += ' человек'
        if not i[1]:
            reply_msg += ';\n'
        else:
            reply_msg += ' (' + ', '.join(map(lambda x: '@' + x, i[1])) + ');\n'
    if not list(teams.keys()):
        bot.send_message(chat_id=chat, text=reply_msg + 'Нет команд', parse_mode=telegram.ParseMode.HTML)
    else:
        bot.send_message(chat_id=chat, text=reply_msg, parse_mode=telegram.ParseMode.HTML)


def help_com(bot, update):
    chat = update.message.chat_id
    user = update.message.from_user
    print(user['username'] + ' (' + str(chat) + ') -- ', '/help')
    if user['username'] not in adminlist:
        reply_msg = '<b>Список команд:</b> \n\n' \
                    '/help - список команд; \n' \
                    '/add_team - создать команду; \n' \
                    '/join_team - вступить в команду; \n' \
                    '/show_teams - показать все команды и их участников; \n' \
                    '/cancel - отменить действие.'
    else:
        reply_msg = '<b>Список команд:</b> \n\n' \
                    '/help - список команд; \n' \
                    '/add_team - создать команду; \n' \
                    '/join_team - вступить в команду; \n' \
                    '/show_teams - показать все команды и их участников; \n' \
                    '/delete_team - удалить выбранную команду; \n' \
                    '/clear_teams - очистить список команд; \n' \
                    '/shutdown - выключить бота; \n' \
                    '/cancel - отменить действие.'
    bot.send_message(chat_id=chat, text=reply_msg, parse_mode=telegram.ParseMode.HTML)


def cancel(bot, update):
    chat = update.message.chat_id
    print('/cancel', '--', chat)
    bot.send_message(chat_id=chat, text='Команда отменена', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def echo(bot, update):
    chat = update.message.chat_id
    user = update.message.from_user
    print(user['username']+' ('+str(chat)+'):', update.message.text)
    return ConversationHandler.END


def shutdown(bot, update):
    global updater

    chat = update.message.chat_id
    user = update.message.from_user
    print(user['username'] + ' (' + str(chat) + ') -- ', '/shutdown')
    if user['username'] not in adminlist:
        bot.send_message(chat_id=chat, text='Извините, по-видимому, у вас нет прав на исполнение данной команды')
    else:
        bot.send_message(chat_id=chat, text='Бот был успешно выключен')
        save_teams()
        updater.stop()
        dispatcher.stop()
        bot.stop()
        exit(0)


def delete_team(bot, update):
    chat = update.message.chat_id
    user = update.message.from_user
    print(user['username'] + ' (' + str(chat) + ') -- ', '/delete_team')
    if user['username'] not in adminlist:
        bot.send_message(chat_id=chat, text='Извините, по-видимому, у вас нет прав на исполнение данной команды')
        return ConversationHandler.END
    reply_markup = [[i for i in list(teams.keys())]]
    bot.send_message(chat_id=chat, text='Выберите команду, которую хотите удалить',
                     reply_markup=ReplyKeyboardMarkup(reply_markup, one_time_keyboard=True))
    return 2


def single_delete(bot, update):
    chat = update.message.chat_id
    user = update.message.from_user
    d_team = update.message.text
    if d_team not in teams.keys():
        bot.send_message(chat_id=chat, text='Команда не найдена!', reply_markup=ReplyKeyboardRemove())
    else:
        del teams[d_team]
        bot.send_message(chat_id=chat, text='Команда '+d_team+' была успешно удалена!',
                         reply_markup=ReplyKeyboardRemove())
    save_teams()
    return ConversationHandler.END


def clear_teams(bot, update):
    global teams
    chat = update.message.chat_id
    user = update.message.from_user
    print(user['username'] + ' (' + str(chat) + ') -- ', '/clear_teams')
    if user['username'] not in adminlist:
        bot.send_message(chat_id=chat, text='Извините, по-видимому, у вас нет прав на исполнение данной команды')
    else:
        bot.send_message(chat_id=chat, text='Список команд успешно очищен!')
    teams = {}
    save_teams()


def main():
    global bot, updater, dispatcher
    read_teams()

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    add_handler = CommandHandler('add_team', add_team)

    cancel_handler = CommandHandler('cancel', cancel)

    join_handler = CommandHandler('join_team', join_team)

    delete_handler = CommandHandler('delete_team', delete_team)

    clear_handler = CommandHandler('clear_teams', clear_teams)
    dispatcher.add_handler(clear_handler)

    show_handler = CommandHandler('show_teams', show_teams)
    dispatcher.add_handler(show_handler)

    help_handler = CommandHandler('help', help_com)
    dispatcher.add_handler(help_handler)

    shutdown_handler = CommandHandler('shutdown', shutdown)
    dispatcher.add_handler(shutdown_handler)

    dispatcher.add_handler(ConversationHandler(
        entry_points=[add_handler, join_handler, delete_handler, MessageHandler(Filters.text, echo)],
        states={
            0: [MessageHandler(Filters.text, ask_team)],
            1: [MessageHandler(Filters.text, add_user)],
            2: [MessageHandler(Filters.text, single_delete)]
        },
        fallbacks=[cancel_handler]
    ))

    updater.start_polling()

    while True:
        s = input().split('>>')
        if len(s) > 1:
            chat = int(s[0].split()[0])
            bot.send_message(chat_id=chat, text='>>'.join(s[1:]))
        else:
            print('wrong format of message')


if __name__ == '__main__':
    main()
