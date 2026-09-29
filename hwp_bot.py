import os
import threading
from flask import Flask
import telebot
from telebot import types

BOT_TOKEN = os.getenv("BOT_TOKEN", "8640840037:AAE-E5yL248tLJitlslWBOf-MYLYW0WB4f4")
PRIVATE_GROUP_ID = int(os.getenv("PRIVATE_GROUP_ID", "-1001234567890"))
PRIVATE_INVITE_LINK = os.getenv("PRIVATE_INVITE_LINK", "https://t.me/+UA_XO0ZK-YA0M2Y9")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "HWP Bot is Live! Group ID detector running."

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.type in ['group', 'supergroup']:
        print(f"===== GROUP ID DETECTED =====", flush=True)
        print(f"Group Name: {message.chat.title}", flush=True)
        print(f"GROUP ID: {message.chat.id}", flush=True)
        print(f"============================", flush=True)
        bot.reply_to(message, f"呢個群嘅ID係:\n{message.chat.id}")
        return
    user_id = message.from_user.id
    try:
        member = bot.get_chat_member(PRIVATE_GROUP_ID, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton("📚 返去公海 @HWP_STUDY", url="https://t.me/HWP_STUDY")
            markup.add(btn1)
            bot.send_message(message.chat.id, "✅ 檢查到你已經入咗私人群！", reply_markup=markup)
        else:
            markup = types.InlineKeyboardMarkup()
            btn_join = types.InlineKeyboardButton("🔓 立即入群解鎖", url=PRIVATE_INVITE_LINK)
            btn_check = types.InlineKeyboardButton("✅ 我已加入，重新檢查", callback_data="check_again")
            markup.add(btn_join)
            markup.add(btn_check)
            bot.send_message(message.chat.id, f"🔒 完整版要入私人資源庫先睇到\n{PRIVATE_INVITE_LINK}", reply_markup=markup)
    except Exception as e:
        print(f"Error: {e}", flush=True)
        markup = types.InlineKeyboardMarkup()
        btn_join = types.InlineKeyboardButton("🔓 立即入群解鎖", url=PRIVATE_INVITE_LINK)
        btn_check = types.InlineKeyboardButton("✅ 我已加入，重新檢查", callback_data="check_again")
        markup.add(btn_join)
        markup.add(btn_check)
        bot.send_message(message.chat.id, f"🔒 請先加入：\n{PRIVATE_INVITE_LINK}", reply_markup=markup)

@bot.message_handler(func=lambda m: True, content_types=['text','new_chat_members','photo','sticker'])
def log_all(message):
    if message.chat.type in ['group','supergroup']:
        print(f"===== GROUP ID DETECTED =====", flush=True)
        print(f"Group Name: {message.chat.title}", flush=True)
        print(f"GROUP ID: {message.chat.id}", flush=True)
        print(f"============================", flush=True)

@bot.callback_query_handler(func=lambda call: call.data == "check_again")
def callback_check(call):
    send_welcome(call.message)
    bot.answer_callback_query(call.id, "檢查緊...")

def run_bot():
    print("HWP Bot Polling 開始...", flush=True)
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
