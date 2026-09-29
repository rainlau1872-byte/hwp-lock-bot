import os
import time
import threading
from flask import Flask
import telebot
from telebot import types

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set!")

PRIVATE_GROUP_ID = int(os.getenv("PRIVATE_GROUP_ID", "-1003647321921"))
PRIVATE_INVITE_LINK = os.getenv("PRIVATE_INVITE_LINK", "https://t.me/+UA_XO0ZK-YA0M2Y9")

# --- 你的3個聯絡方法 ---
WHATSAPP_NUMBER = "59475041"
WHATSAPP_LINK = f"https://wa.me/852{WHATSAPP_NUMBER}?text=你好，想問功課服務"
TG_SERVICE = "@homework_professor"
WEBSITE = "https://www.homework-professor.com/"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "HWP Bot Live - Contact Updated"

SUBJECTS = {
    "nursing": {"name": "🩺 Nursing 護理", "tag": "#NURSING", "desc": "Care Plan / Case Study / Drug Calc / Reflective\n熱門：NURS1003, NURS2007, Patho", },
    "business": {"name": "📊 Business 商科", "tag": "#BUSINESS", "desc": "Report / SWOT / Finance / Business Plan\n熱門：MGMT, DSME, ECON", },
    "research": {"name": "📈 Research/SPSS", "tag": "#RESEARCH", "desc": "SPSS / STATA / R / 問卷分析 / p-value\n代跑數據+出圖", },
    "marketing": {"name": "📣 Marketing", "tag": "#MARKETING", "desc": "4P / Marketing Plan / Consumer Behavior", },
    "engineering": {"name": "⚙️ Engineering", "tag": "#ENGINEERING", "desc": "Lab Report / MATLAB / CAD", },
    "english": {"name": "✍️ English/UCLC", "tag": "#ENGLISH", "desc": "UCLC1005/1003 / Essay / APA MLA\n紅筆批改版", },
    "psyc": {"name": "🧠 PSYC 心理學", "tag": "#PSYC", "desc": "Research Proposal / Experiment Report / Literature Review / APA 7th\n熱門：PSYC1001, Developmental, Cognitive", },
    "law": {"name": "⚖️ LAW 法律", "tag": "#LAW", "desc": "Case Brief / Legal Memo / IRAC / Essay\n熱門：LLAW1001, Contract, Tort", },
    "ps": {"name": "📝 Personal Statement", "tag": "#PS", "desc": "Master / PhD / Scholarship / Exchange\n全英撰寫 + 2次修改", },
    "cv": {"name": "📄 CV / Cover Letter", "tag": "#CV", "desc": "CV / Resume / Cover Letter / LinkedIn\n投行 / Big4 / 實習 ATS優化", },
    "other": {"name": "📦 其他科目", "tag": "#OTHER", "desc": "SOCI / EDUC / GE / 任何冷門科都接", },
}

MAIN_KEYS = ["nursing","business","research","psyc","law","ps","cv","english"]

def contact_buttons():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton(f"💚 WhatsApp 客服 (主) {WHATSAPP_NUMBER}", url=WHATSAPP_LINK))
    markup.add(types.InlineKeyboardButton(f"✈️ TG 客服 {TG_SERVICE}", url=f"https://t.me/{TG_SERVICE.replace('@','')}"))
    markup.add(types.InlineKeyboardButton(f"🌐 官網 {WEBSITE}", url=WEBSITE))
    return markup

def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    for k in MAIN_KEYS:
        if k in SUBJECTS:
            markup.add(types.InlineKeyboardButton(SUBJECTS[k]["name"], callback_data=f"subj_{k}"))
    markup.add(
        types.InlineKeyboardButton("📚 更多科目 >", callback_data="more_subjects"),
        types.InlineKeyboardButton("🛠 急單/改格式/減AI", callback_data="subj_urgent")
    )
    return markup

def more_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    for k in ["marketing","engineering","other"]:
        markup.add(types.InlineKeyboardButton(SUBJECTS[k]["name"], callback_data=f"subj_{k}"))
    markup.add(types.InlineKeyboardButton("⬅️ 返主目錄", callback_data="back_menu"))
    return markup

@bot.message_handler(commands=['start'])
@bot.message_handler(func=lambda m: m.text and m.text.strip().lower() in ['/start', 'start', '/START'])
def send_welcome(message):
    if message.chat.type in ['group', 'supergroup']:
        print(f"GROUP ID: {message.chat.id}", flush=True)
        bot.reply_to(message, f"ID: {message.chat.id}")
        return
    user_id = message.from_user.id
    text_raw = (message.text or '').strip().lower()
    print(f"/start triggered from {user_id} text={message.text} chat_type={message.chat.type}", flush=True)
    try:
        member = bot.get_chat_member(PRIVATE_GROUP_ID, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            bot.send_message(message.chat.id, "✅ 已驗證入咗私庫 HWP.STUDY！\n\n你係咩科？揀一個即刻彈範文庫：", reply_markup=main_menu())
            try:
                with open('UCLC1005_說明範例3篇.pdf','rb') as f:
                    bot.send_document(message.chat.id, f, caption="🎁 新人禮：UCLC1005 3篇A+範文\n官網 homework-professor.com | TG @homework_professor | WhatsApp 59475041")
            except:
                pass
        else:
            m = types.InlineKeyboardMarkup()
            m.add(types.InlineKeyboardButton("🔓 入私人庫解鎖", url=PRIVATE_INVITE_LINK))
            m.add(types.InlineKeyboardButton("✅ 已入，重新檢查", callback_data="check_again"))
            bot.send_message(message.chat.id, f"🔒 HWP 10大科目+PS/CV範文庫要入私庫先睇到\n{PRIVATE_INVITE_LINK}", reply_markup=m)
    except Exception as e:
        print(e, flush=True)
        m = types.InlineKeyboardMarkup()
        m.add(types.InlineKeyboardButton("🔓 入群", url=PRIVATE_INVITE_LINK))
        m.add(types.InlineKeyboardButton("✅ 已入", callback_data="check_again"))
        bot.send_message(message.chat.id, f"請先入群：{PRIVATE_INVITE_LINK}", reply_markup=m)

@bot.callback_query_handler(func=lambda c: c.data.startswith("subj_"))
def handle_subject(call):
    key = call.data.replace("subj_","")
    if key == "urgent":
        bot.send_message(call.message.chat.id, "🛠 急單/改格式/減AI 15分鐘報價\n\nAPA/MLA/Chicago/減AI\n請用下面3個方法聯絡我地，記得講 Deadline + 字數 + 科目：", reply_markup=contact_buttons())
        bot.answer_callback_query(call.id)
        return
    data = SUBJECTS.get(key)
    if not data: return
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(types.InlineKeyboardButton(f"📂 睇 {data['tag']} 全部範文", url=f"https://t.me/c/{str(PRIVATE_GROUP_ID).replace('-100','')}/1"))
    m.add(types.InlineKeyboardButton(f"💚 WhatsApp 報價 (主) {WHATSAPP_NUMBER}", url=WHATSAPP_LINK))
    m.add(types.InlineKeyboardButton(f"✈️ TG 客服 {TG_SERVICE}", url=f"https://t.me/{TG_SERVICE.replace('@','')}"))
    m.add(types.InlineKeyboardButton(f"🌐 官網下單", url=WEBSITE))
    m.add(types.InlineKeyboardButton("🔙 返主目錄", callback_data="back_menu"))
    
    text = f"{data['name']} 資源庫 {data['tag']}\n\n{data['desc']}\n\n🔍 私人群搜：{data['tag']}\n\n👇 搵客服報價 (講Deadline+字數+科目)"
    bot.send_message(call.message.chat.id, text, reply_markup=m)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data in ["check_again","back_menu","more_subjects"])
def handle_nav(call):
    if call.data == "check_again":
        send_welcome(call.message)
    elif call.data == "more_subjects":
        bot.edit_message_text("📚 更多科目：", call.message.chat.id, call.message.message_id, reply_markup=more_menu())
    else:
        bot.edit_message_text("你係咩科？揀一個：", call.message.chat.id, call.message.message_id, reply_markup=main_menu())
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: m.text and m.text.strip().lower() not in ['/start','start','/START'] , content_types=['text'])
def log_all_text(message):
    # avoid catching start
    if message.chat.type in ['group','supergroup']:
        print(f"GROUP ID: {message.chat.id}", flush=True)
        return
    # 任何其他文字都當作 /start 處理，方便學生
    send_welcome(message)

@bot.message_handler(content_types=['new_chat_members','photo','sticker'])
def log_all(message):
    if message.chat.type in ['group','supergroup']:
        print(f"GROUP ID: {message.chat.id}", flush=True)

def run_bot():
    print("HWP Bot - 3聯絡方法版啟動...", flush=True)
    time.sleep(3)
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            print(f"Retry: {e}", flush=True)
            time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
