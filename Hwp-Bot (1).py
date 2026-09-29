import os
import telebot
from telebot import types

# ===== Render 建議用 Env Var，安全啲 =====
# 你喺 Render -> Environment 入面加呢3個就得，如果唔加，佢會用下面寫死嘅值
BOT_TOKEN = os.getenv("BOT_TOKEN", "8640840037:AAE-E5yL248tLJitlslWBOf-MYLYW0WB4f4")  # 舊Token已洩漏，記得去 BotFather /revoke 攞新嘅
PRIVATE_GROUP_ID = int(os.getenv("PRIVATE_GROUP_ID", "-1001234567890"))  # 暫時用假嘅，等Log印真ID再改
PRIVATE_INVITE_LINK = os.getenv("PRIVATE_INVITE_LINK", "https://t.me/+UA_XO0ZK-YA0M2Y9")

bot = telebot.TeleBot(BOT_TOKEN)

# ===== 自動偵測 Group ID 用 =====
@bot.message_handler(content_types=['new_chat_members', 'text', 'photo', 'sticker'])
def log_group_id(message):
    # 只要有人喺任何Group講嘢，就會喺Render Logs印出Group ID
    if message.chat.type in ['group', 'supergroup']:
        print(f"===== GROUP ID DETECTED =====")
        print(f"Group Name: {message.chat.title}")
        print(f"GROUP ID: {message.chat.id}")
        print(f"============================")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    # 如果係群入面打 /start，就淨係印ID，唔跑漏斗
    if message.chat.type in ['group', 'supergroup']:
        bot.reply_to(message, f"呢個群嘅ID係: {message.chat.id}\nCopy去用啦！")
        return

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
        print(f"Error check: {e}")

@bot.callback_query_handler(func=lambda call: call.data == "check_again")
def callback_check(call):
    send_welcome(call.message)
    bot.answer_callback_query(call.id, "檢查緊...")

print("HWP Bot 已經啟動...等緊Group ID")
bot.infinity_polling()
