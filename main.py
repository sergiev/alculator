# -*- coding: utf-8 -*-
"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, ParseMode
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

TOKEN = "2016466228:AAG1IyASm8VghcKRhf0NF7NYEmw0ka5uAnU"
WTF = 0.7893

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

SEX, MASS, HUNGER, VERDICT = range(4)

SEXES = ['Для девочки', 'Для мальчика']
HUNGERS = ['Ща лопну от жрачки', 'Сытость присутствует',
           'Лёгкое чувство голода', 'Нелёгкое чувство голода', 'Пишу из голодного обморока']
H = len(HUNGERS)
BUTTONS_IN_ROW = 3
HUNGER_KEYBOARD = [HUNGERS[i:min(i + BUTTONS_IN_ROW, H)] for i in range(0, H, BUTTONS_IN_ROW)]
users = {}

LIMITS = {'support': 0.17, 'lite': 0.45, 'intermediate': 0.75, 'hard': 0.9}


class Person:
    def __init__(self, is_male):
        self.is_male = is_male
        self.mass = None
        self.hunger = None
        self.degree = 1

    def volume_for_ethanol(self, ethanol):
        sex = 0.68 if self.is_male else 0.55
        return ethanol * self.mass * sex / self.hunger / self.degree / WTF


def start(update: Update, _: CallbackContext) -> int:
    """Starts the conversation and asks the user about their gender."""
    reply_keyboard = [SEXES]

    update.message.reply_text(
        'Привет чепушила!\n'
        'Отправь /zaebal to stop talking to me.\n\n'
        'Для кого проводим замеры?',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Boy or Girl?'
        ),
    )

    return SEX


def update_sex(update: Update, _: CallbackContext) -> int:
    """Stores the selected gender and asks for a mass."""
    user = update.message.from_user
    logger.info(f"Gender of user#{user.id}: {update.message.text}")
    is_male = bool(SEXES.index(update.message.text))
    if user.id not in users:
        users[user.id] = Person(is_male)
    else:
        users[user.id].is_male = is_male
    update.message.reply_text(
        'Прекрасно, восхитительно! А какова масса нашего пациента?\n'
        'Ответь числом в килограммах.',
    )

    return MASS


def update_mass(update: Update, _: CallbackContext) -> int:
    """"""
    user_id = update.message.from_user.id
    user = users[user_id]
    answer = update.message.text
    logger.info(f"Mass of user#{user_id}: {answer}")
    try:
        user.mass = float(answer.strip())
    except:
        update.message.reply_text(
            'Это не число в килограммах.\nДавай попробуем ещё раз. Пример ввода: 69.42',
        )
        return MASS
    update.message.reply_text("А что по голоду?\n",
                              reply_markup=ReplyKeyboardMarkup(HUNGER_KEYBOARD,
                                                               one_time_keyboard=True))
    return HUNGER


def update_hunger(update: Update, _: CallbackContext) -> int:
    user_id = update.message.from_user.id
    user = users[user_id]
    hunger_idx = HUNGERS.index(update.message.text)
    logger.info(f"Hunger of user#{user_id}: {hunger_idx}")
    user.hunger = 0.9 - (hunger_idx / 20)
    volumes = {level: user.volume_for_ethanol(limit) for level, limit in LIMITS.items()}
    update.message.reply_text(f"Для лёгкого опъянения {user.mass:.0f}-килограммовому"
                              f" {'мужскому' if user.is_male else 'женскому'} "
                              f"телу с такой степенью сытости нужно *{volumes['lite']:.0f}* "
                              "миллилитров чистого этанола.\n Для intermediate intoxication нужно "
                              f"*{volumes['intermediate']:.0f}* мл.\nГраница самоконтроля: "
                              f"*{volumes['hard']:.0f}* мл, за неё заходить *не стоит*.\n"
                              "Чтобы поддерживать выбранную кондицию, каждый час нужно "
                              f"подкидывать по *{volumes['support']:.0f}* мл этанола.\n"
                              f"Чтобы начать заново, отправь /start",
                              parse_mode=ParseMode.MARKDOWN)

    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SEX: [MessageHandler(Filters.regex(f'^({"|".join(SEXES)})$'), update_sex)],
            MASS: [MessageHandler(Filters.text & ~Filters.command, update_mass)],
            HUNGER: [MessageHandler(Filters.text & ~Filters.command, update_hunger)],
        },
        fallbacks=[CommandHandler('zaebal', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
