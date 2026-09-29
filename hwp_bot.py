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

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "HWP Bot Live - PSYC LAW PS CV"

SUBJECTS = {
    "nursing": {"name": "🩺 Nursing 護理", "tag": "#NURSING", "desc": "Care Plan / Case Study / Drug Calc / Reflective\n熱門：NURS1003, NURS2007, Patho", "price": "改格式$150起"},
    "business": {"name": "📊 Business 商科", "tag": "#BUSINESS", "desc": "Report / SWOT / Finance / Business Plan\n熱門：MGMT, DSME, ECON", "price": "Report $300起"},
    "research": {"name": "📈 Research/SPSS", "tag": "#RESEARCH", "desc": "SPSS / STATA / R / 問卷分析 / p-value\n代跑數據+出圖", "price": "SPSS代跑 $200起"},
    "marketing": {"name": "📣 Marketing", "tag": "#MARKETING", "desc": "4P / Marketing Plan / Consumer Behavior", "price": "Plan $350起"},
    "engineering": {"name": "⚙️ Engineering", "tag": "#ENGINEERING", "desc": "Lab Report / MATLAB / CAD", "price": "Lab $250起"},
    "english": {"name": "✍️ English/UCLC", "tag": "#ENGLISH", "desc": "UCLC1005/1003 / Essay / APA MLA\n紅筆批改版", "price": "Essay $200起"},
    # 高單價新加
    "psyc": {"name": "🧠 PSYC 心理學", "tag": "#PSYC", "desc": "Research Proposal / Experiment Report / Literature Review / APA 7th\n熱門：PSYC1001, Developmental, Cognitive\n重點：老師好睇Theory + Critique", "price": "Proposal $400起"},
    "law": {"name": "⚖️ LAW 法律", "tag": "#LAW", "desc": "Case Brief / Legal Memo / IRAC / Essay\n熱門：LLAW1001, Contract, Tort\n重點：IRAC格式 + Citation", "price": "Memo $350起"},
    "ps": {"name": "📝 Personal Statement", "tag": "#PS", "desc": "Master / PhD / Scholarship / Exchange\n全英撰寫 + 2次無限修改\n熱門：CUHK, HKU, UK Master PS", "price": "PS $500起"},
    "cv": {"name": "📄 CV / Cover Letter", "tag": "#CV", "desc": "CV / Resume / Cover Letter / LinkedIn\n投行 / Big4 / 實習專用格式\nATS過濾系統優化", "price": "CV $180起 / Set $350"},
    "other": {"name": "📦 其他科目", "tag": "#OTHER", "desc": "SOCI / EDUC / GE / 任何冷門科都接\n直接DM報價", "price": "一律報價"},
}

MAIN_KEYS = ["nursing","business","research","psyc","law","ps","cv","english"]  # 8大主按鈕

def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    for k in MAIN_KEYS:
        if k in SUBJECTS:
            markup.add(types.InlineKeyboardButton(SUBJECTS[k]["name"], callback_data=f"subj_{k}"))
    markup.add(
        types.InlineKeyboardButton("📚 更多科目 >", callback_data="more_subjects"),
        types.InlineKeyboardButton("🛠️ 急單/改格式", callback_data="subj_urgent")
    )
    return markup

def more_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    for k in ["marketing","engineering","other"]:
        markup.add(types.InlineKeyboardButton(SUBJECTS[k]["name"], callback_data=f"subj_{k}"))
    markup.add(types.InlineKeyboardButton("⬅️ 返主目錄", callback_data="back_menu"))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.type in ['group', 'supergroup']:
        print(f"GROUP ID: {message.chat.id}", flush=True)
        bot.reply_to(message, f"ID: {message.chat.id}")
        return
    user_id = message.from_user.id
    try:
        member = bot.get_chat_member(PRIVATE_GROUP_ID, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            bot.send_message(message.chat.id, "✅ 已驗證入咗私庫 HWP.STUDY！\n\n你係咩科？揀一個即刻彈範文庫 + 價錢：", reply_markup=main_menu())
            try:
                with open('UCLC1005_說明範例3篇.pdf','rb') as f:
                    bot.send_document(message.chat.id, f, caption="🎁 新人禮：UCLC1005 3篇A+範文\nIG: @hwp.study")
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
        m = types.InlineKeyboardMarkup()
        m.add(types.InlineKeyboardButton("📸 IG @hwp.study 報價", url="https://instagram.com/hwp_academy"))
        m.add(types.InlineKeyboardButton("📚 公海", url="https://t.me/HWP_STUDY"))
        bot.send_message(call.message.chat.id, "🛠️ 急單/改格式 15分鐘報價\n\nAPA/MLA/Chicago\nDM @hwp.study：\nDeadline + 字數 + 科目", reply_markup=m)
        bot.answer_callback_query(call.id)
        return
    data = SUBJECTS.get(key)
    if not data: return
    m = types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton(f"📂 睇 {data['tag']} 全部", url=f"https://t.me/c/{str(PRIVATE_GROUP_ID).replace('-100','')}/1"))
    m.add(types.InlineKeyboardButton("🔙 主目錄", callback_data="back_menu"), types.InlineKeyboardButton("💬 搵顧問報價", url="https://instagram.com/hwp_academy"))
    
    text = f"{data['name']} 資源庫 {data['tag']}\n\n{data['desc']}\n\n💰 {data['price']}\n\n🔍 私人群搜：{data['tag']}\n📌 全部標籤：#NURSING #BUSINESS #RESEARCH #PSYC #LAW #PS #CV #ENGLISH"
    if key in ["ps","cv"]:
        text += "\n\n⚠️ PS/CV 需提供：申請學校 + 科系 + 舊版CV/背景"
    bot.send_message(call.message.chat.id, text, reply_markup=m)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data in ["check_again","back_menu","more_subjects"])
def handle_nav(call):
    if call.data == "check_again":
        send_welcome(call.message)
    elif call.data == "more_subjects":
        bot.edit_message_text("📚 更多科目：", call.message.chat.id, call.message.message_id, reply_markup=more_menu())
    else:
        bot.edit_message_text("你咩科？揀一個：", call.message.chat.id, call.message.message_id, reply_markup=main_menu())
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: True, content_types=['text','new_chat_members','photo','sticker'])
def log_all(message):
    if message.chat.type in ['group','supergroup']:
        print(f"GROUP ID: {message.chat.id}", flush=True)

def run_bot():
    print("HWP Bot - PSYC LAW PS CV 版啟動...", flush=True)
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
