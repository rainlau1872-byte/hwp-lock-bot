import os
import json
import telebot
from telebot import types

BOT_TOKEN = os.environ.get("BOT_TOKEN")
PRIVATE_GROUP_ID = int(os.environ.get("GROUP_ID", "0"))

# === 最終Link ===
WHATSAPP_LINK = "https://wa.me/85259375041"
TG_GROUP_LINK = "https://t.me/homework_professor"
IG_LINK = "https://www.instagram.com/hwp.study"
PRIVATE_INVITE_LINK_ENV = os.environ.get("PRIVATE_INVITE_LINK")

bot = telebot.TeleBot(BOT_TOKEN)
try:
    bot.remove_webhook()
except:
    pass

PRIVACY_TEXT = """🔒 私隱聲明：本Bot僅用於驗證入群資格及派發教學資源，不會收集、儲存或公開任何同學之姓名、學號、院校資料。所有查詢均以匿名形式處理"""

INVITE_FILE = "invites.json"

def load_data():
    if not os.path.exists(INVITE_FILE):
        return {"users": {}, "referrals": {}}
    try:
        with open(INVITE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"users": {}, "referrals": {}}

def save_data(data):
    with open(INVITE_FILE, 'w') as f:
        json.dump(data, f)

def get_private_invite_link():
    if PRIVATE_INVITE_LINK_ENV:
        return PRIVATE_INVITE_LINK_ENV
    try:
        if PRIVATE_GROUP_ID != 0:
            link = bot.create_chat_invite_link(PRIVATE_GROUP_ID)
            return link.invite_link
    except Exception as e:
        print(f"auto invite failed: {e}")
    return TG_GROUP_LINK

def is_in_group(user_id):
    if PRIVATE_GROUP_ID == 0:
        return False
    try:
        m = bot.get_chat_member(PRIVATE_GROUP_ID, user_id)
        return m.status in ['member','administrator','creator']
    except:
        return False

@bot.message_handler(commands=['start'])
def handle_start(message):
    data=load_data()
    user_id=message.from_user.id
    args=message.text.split()
    if len(args)>1 and args[1].startswith('ref_'):
        try:
            referrer_id=int(args[1].replace('ref_',''))
            if referrer_id!=user_id and str(user_id) not in data["referrals"]:
                data["referrals"][str(user_id)]=referrer_id
                save_data(data)
        except:
            pass
    private_link=get_private_invite_link()
    welcome=f"""{PRIVACY_TEXT}

👋 歡迎嚟到 HWP 私人資源庫

入咗私人庫先拎得完整版，公海只放框架。

請先加入私人群，再按下面按鈕驗證：
"""
    markup=types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📲 1. 加入TG私庫 (私人Link)", url=private_link))
    markup.add(types.InlineKeyboardButton("✅ 2. 我已入群，立即驗證", callback_data="verify"))
    markup.add(types.InlineKeyboardButton("📩 取得邀請獎勵Link", callback_data="invite"))
    markup.row(types.InlineKeyboardButton("💬 WhatsApp 59375041", url=WHATSAPP_LINK),
               types.InlineKeyboardButton("📲 主TG @homework_professor", url=TG_GROUP_LINK))
    bot.send_message(message.chat.id, welcome, reply_markup=markup)
    if str(user_id) in data["referrals"] and is_in_group(user_id):
        referrer_id=data["referrals"][str(user_id)]
        if str(referrer_id) not in data["users"]:
            data["users"][str(referrer_id)]={"count":0,"invited_users":[]}
        if user_id not in data["users"][str(referrer_id)]["invited_users"]:
            data["users"][str(referrer_id)]["count"]+=1
            data["users"][str(referrer_id)]["invited_users"].append(user_id)
            save_data(data)
            try:
                count=data["users"][str(referrer_id)]["count"]
                bot.send_message(referrer_id, f"🎉 有同學經你條Link入咗私庫！目前已邀請 {count} 人\n夠3人即刻解鎖隱藏A+範文！")
            except:
                pass

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    data=load_data()
    private_link=get_private_invite_link()
    if call.data=="verify":
        if PRIVATE_GROUP_ID==0:
            bot.answer_callback_query(call.id,"管理員未設定GROUP_ID",show_alert=True)
            return
        if is_in_group(call.from_user.id):
            bot.answer_callback_query(call.id,"驗證成功！")
            markup=types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("💬 WhatsApp 59375041", url=WHATSAPP_LINK))
            markup.add(types.InlineKeyboardButton("📲 TG @homework_professor", url=TG_GROUP_LINK))
            markup.add(types.InlineKeyboardButton("📸 IG主帳", url=IG_LINK))
            msg=f"""✅ 驗證成功！已確認你入咗私人庫

{PRIVACY_TEXT}

入咗私人庫先拎得完整版：
/uclc - UCLC1005
/lch1105 - LCH1105
/turnitin - Turnitin
/ask - 匿名提問
/invite - 邀請Link
"""
            bot.send_message(call.message.chat.id, msg, reply_markup=markup)
        else:
            bot.answer_callback_query(call.id,"未入群，入咗先再驗證",show_alert=True)
            markup=types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("📲 加入TG私庫", url=private_link))
            bot.send_message(call.message.chat.id, "❌ 仲未偵測到你入群，請先加入私人群再按驗證。\n入咗私人庫先拎得完整版\n\n如果已入群但驗證唔到，請確認Bot係Admin。", reply_markup=markup)
    elif call.data=="invite":
        ref_link=f"https://t.me/{bot.get_me().username}?start=ref_{call.from_user.id}"
        count=data["users"].get(str(call.from_user.id),{}).get("count",0)
        bot.send_message(call.message.chat.id, f"🔗 你嘅專屬邀請Link：\n{ref_link}\n\n已邀請：{count}/3 人\n{PRIVACY_TEXT}")

@bot.message_handler(commands=['invite'])
def invite_cmd(message):
    data=load_data()
    ref_link=f"https://t.me/{bot.get_me().username}?start=ref_{message.from_user.id}"
    count=data["users"].get(str(message.from_user.id),{}).get("count",0)
    bot.send_message(message.chat.id, f"🔗 你嘅專屬邀請Link：\n{ref_link}\n已邀請：{count}/3\n{PRIVACY_TEXT}")

@bot.message_handler(commands=['ask'])
def ask_cmd(message):
    question=message.text.replace('/ask','').strip()
    if not question:
        markup=types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💬 WhatsApp 59375041", url=WHATSAPP_LINK))
        markup.add(types.InlineKeyboardButton("📲 TG @homework_professor", url=TG_GROUP_LINK))
        bot.send_message(message.chat.id, f"用法：\n/ask 你嘅問題\n例如： /ask LCH1105點揀社評\n\n匿名轉去私人群\n\n{PRIVACY_TEXT}", reply_markup=markup)
        return
    if PRIVATE_GROUP_ID==0:
        bot.send_message(message.chat.id, "❌ 管理員未設定GROUP_ID")
        return
    anon_text=f"📩 匿名同學提問：\n\n{question}\n\n---\n(匿名轉發，已隱藏資料)"
    try:
        bot.send_message(PRIVATE_GROUP_ID, anon_text)
        markup=types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton("💬 WhatsApp 59375041", url=WHATSAPP_LINK),
                   types.InlineKeyboardButton("📲 @homework_professor", url=TG_GROUP_LINK),
                   types.InlineKeyboardButton("📸 IG @hwp.study", url=IG_LINK))
        bot.send_message(message.chat.id, f"✅ 已匿名發送去私人群\n\n{PRIVACY_TEXT}", reply_markup=markup)
    except Exception as e:
        bot.send_message(message.chat.id, f"發送失敗：{e}")

@bot.message_handler(commands=['uclc','lch1105','turnitin'])
def resource_cmd(message):
    if not is_in_group(message.from_user.id):
        markup=types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📲 加入TG私庫", url=get_private_invite_link()))
        bot.send_message(message.chat.id, f"🔒 只限私庫成員\n打 /start 開始\n\n{PRIVACY_TEXT}", reply_markup=markup)
        return
    cmd=message.text.split()[0]
    base=f"{PRIVACY_TEXT}\n\n📌 僅作教育用途及寫作結構參考，請勿抄襲\n\n"
    tail="\n\n入咗私人庫先拎得完整版，公海只放框架。"
    if 'uclc' in cmd:
        bot.send_message(message.chat.id, base+"🔒 UCLC1005 A+ 範文 (紅筆批改版) 已上載"+tail)
    elif 'lch1105' in cmd:
        bot.send_message(message.chat.id, base+"🔒 LCH1105 Checklist + 標題公式已上載"+tail)
    else:
        bot.send_message(message.chat.id, base+"📝 Turnitin流程：將Word檔Send嚟呢個Bot"+tail)

print("Bot starting...")
bot.infinity_polling(skip_pending=True, timeout=20, long_polling_timeout=20)
