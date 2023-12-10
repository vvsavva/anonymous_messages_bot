from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, Filters
import sqlite3
import random
import string
import config
otpravka = []
conn = sqlite3.connect(config.baza)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS user (
        user_id INTEGER,
        name TEXT,
        refid TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS mess (
        user_id INTEGER,
        message_id INTEGER,
        reply_message_id INTEGER
    )
''')
conn.commit()
def generate_random_kode(length):
    while True:
        letters = string.ascii_lowercase
        rand_string = ''.join(random.choice(letters) for i in range(length))
        with sqlite3.connect(config.baza) as conn:
            cursor = conn.cursor()

        cursor.execute('SELECT refid FROM user WHERE refid = ?', (rand_string,))
        refid = cursor.fetchone()
        conn.commit()
        if refid:
            pass
        else:
            break
    return rand_string
TOKEN = config.TOKEN
def start(update, context):
    chat_id = update.message.chat_id
    user = update.message.from_user
    with sqlite3.connect(config.baza) as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM user WHERE user_id = ?', (chat_id,))
        existing_user = cursor.fetchone()

        if existing_user is None:
            cursor.execute('INSERT INTO user (user_id, name, refid) VALUES (?, ?, ?)',
                    (chat_id, user.username, generate_random_kode(9)))
        conn.commit()
    referral_code = context.args[0] if context.args else None
    if referral_code:
        with sqlite3.connect(config.baza) as conn:
            cursor = conn.cursor()
        cursor.execute('SELECT refid FROM user WHERE user_id = ?', (chat_id,))
        refid = cursor.fetchone()
        refid = refid[0]
        cursor.execute('SELECT user_id FROM user WHERE refid = ?', (referral_code,))
        rsass = cursor.fetchone()
        rsass = rsass[0]
        otpravka.append([chat_id, rsass])
        update.message.reply_text(f"🚀 Напиши сообщение которое ты хочешь написать!\n\nКстати вот твоя личная ссылка если захочешь тоже получать сообщения!\nt.me/anonymous_sova_bot?start={refid}")
    else:
        cursor.execute('SELECT refid FROM user WHERE user_id = ?', (chat_id,))
        refid = cursor.fetchone()
        refid = refid[0]
        update.message.reply_text(f"🚀 Начни получать анонимные сообщения прямо сейчас!\n\nВот твоя личная ссылка!\nt.me/anonymous_sova_bot?start={refid}")
def forward_to_userrrrr(update, context):
    user_id = update.message.chat_id
    member = update.message.from_user.username
    sas = None
    for opr in otpravka:
        if opr[0] == user_id:
            sas = 1
            komy = opr[1]
    if sas:
        conn = sqlite3.connect(config.baza)
        cursor = conn.cursor()
        conn.close()
        sent_message = None
        if update.message.text:
            sent_message = context.bot.send_message(komy, f'Вам написали анонимное сооюбщение:\n{update.message.text}')
        elif update.message.photo:
            photo = update.message.photo[-1] 
            context.bot.send_photo(komy, photo.file_id, caption=f'Вам написали анонимное сооюбщение:\n{update.message.caption}')
        elif update.message.audio:
            audio = update.message.audio
            sent_message = context.bot.send_audio(komy, audio.file_id, caption=f'Вам написали анонимное сооюбщение:\n{update.message.caption}')
        elif update.message.document:
            file = update.message.document
            if file.mime_type == "audio/mpeg":
                sent_message = context.bot.send_audio(komy, file.file_id, caption=f'Вам написали анонимное сооюбщение:\n{update.message.caption}')
            else:
                sent_message = context.bot.send_document(komy, file.file_id, caption=f'Вам написали анонимное сооюбщение:\n{update.message.caption}')
        elif update.message.video:
            sent_message = context.bot.send_video(komy, update.message.video.file_id, caption=f'Вам написали анонимное сооюбщение:\n{update.message.caption}')
        elif update.message.voice:
            sent_message = context.bot.send_voice(komy, update.message.voice.file_id, caption=f'Вам написали анонимное сооюбщение:\n{update.message.caption}')

        if sent_message:
            otpravka.remove([user_id, komy])
            update.message.reply_text(f"🚀Сообщение отправлено!")
            conn = sqlite3.connect(config.baza)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO mess (user_id, message_id, reply_message_id) VALUES (?, ?, ?)", (user_id, update.message.message_id, sent_message.message_id))
            conn.commit()
            conn.close()

def reply_to(update, context):
    chat_id = update.message.chat_id
    reply_message = update.message.reply_to_message
    reply_message_id = reply_message.message_id
    message_id = update.message.message_id
    conn = sqlite3.connect(config.baza)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM mess WHERE reply_message_id=?", (reply_message_id,))
    user_id = cursor.fetchone()
    conn.close()

    if user_id:
        user_id = user_id[0]
        context.bot.copy_message(chat_id=user_id, from_chat_id=chat_id, message_id=message_id, disable_notification=True)
def main() -> None:
    updater = Updater(token=TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))

    dispatcher.add_handler(MessageHandler(Filters.private & Filters.reply, reply_to))
    dispatcher.add_handler(MessageHandler(Filters.private & Filters.all, forward_to_userrrrr))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()