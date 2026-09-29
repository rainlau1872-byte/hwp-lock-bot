import os
import time
import threading
from flask import Flask
import telebot
from telebot import types

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set in Environment!")

PRIVATE_GROUP_ID = os.getenv("PRIVATE_GROUP_ID", "5249925931")
try:
    PRIVATE_GROUP_ID = int(PRIVATE_GROUP_ID)
except:
    pass

PRIVATE_INVITE_LINK = os.getenv("PRIVATE_INVITE_LINK", "https://t.me/+UA_XO0ZK-YA0M2Y9")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "HWP Bot is Live!"

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
            btn2 = types.InlineKeyboardButton("📸 IG @hwp.study", url="https://instagram.com/hwp_academy")
            markup.add(btn1, btn2)
            bot.send_message(message.chat.id, "✅ 檢查到你已經入咗私人群！\n\nUCLC1005 3篇A+說明範文 + 紅筆批改版 喺下面：", reply_markup=markup)
            try:
                with open('UCLC1005_說明範例3篇.pdf', 'rb') as f:
                    bot.send_document(message.chat.id, f, caption="HWP.STUDY 獨家 - 完整版範文\nIG: @hwp.study")
            except:
                bot.send_message(message.chat.id, "PDF未放上Server，請聯絡管理員 @hwp.study")
        else:
            markup = types.InlineKeyboardMarkup()
            btn_join = types.InlineKeyboardButton("🔓 立即入群解鎖", url=PRIVATE_INVITE_LINK)
            btn_check = types.InlineKeyboardButton("✅ 我已加入，重新檢查", callback_data="check_again")
            markup.add(btn_join)
            markup.add(btn_check)
            bot.send_message(message.chat.id, f"🔒 完整版要入私人資源庫先睇到\n\n你而家未入群 {PRIVATE_INVITE_LINK}\n\n入咗之後再按「我已加入」", reply_markup=markup)
    except Exception as e:
        markup = types.InlineKeyboardMarkup()
        btn_join = types.InlineKeyboardButton("🔓 立即入群解鎖", url=PRIVATE_INVITE_LINK)
        btn_check = types.InlineKeyboardButton("✅ 我已加入，重新檢查", callback_data="check_again")
        markup.add(btn_join)
        markup.add(btn_check)
        bot.send_message(message.chat.id, f"🔒 完整版要入私人資源庫先睇到\n\n請先加入：\n{PRIVATE_INVITE_LINK}\n\n入咗之後按下面個掣", reply_markup=markup)
        print(f"Error check: {e}", flush=True)

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
    print("HWP Bot 已經啟動...", flush=True)
    time.sleep(3)  # 等舊 instance 死咗先開始 polling，避免 Render 0-downtime 409
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            print(f"Bot polling error: {e}, 5秒後重試...", flush=True)
            time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
