import os
import threading
import time
from flask import Flask
import telebot
from telebot import types

# ---------------- CONFIGURATION ----------------
BOT_TOKEN = "8717353251:AAE_FDKyqxSC3RzvJepJTih6H2K8Y3H9Q-Q"

# Aapki Numeric Admin Chat ID
ADMIN_CHAT_ID = 7218404735  

ADMIN_USERNAME = "Qayoom_pitafi05"  # Support link ke liye

# Deposit Accounts (Owner: Munawar Ali)
JAZZCASH_NO = "03299202072"
JAZZCASH_NAME = "Munawar Ali"

SADAPAY_NO = "03252635541"
SADAPAY_NAME = "Munawar Ali"

BSC_BEP20_WALLET = "0x90a2efbc5799c9d41f134d0ea092be6001181382"
TRX_TRC20_WALLET = "TFprkhMJS2jtUGQ6kp6GHomUCwAzWjcPFd"

# Exchange Rates (PKR)
BUY_RATE = 290.0
SELL_RATE = 281.0

bot = telebot.TeleBot(BOT_TOKEN)
user_states = {}

# --- Flask Server (Keep-Alive Guard on Port 10001) ---
app = Flask(__name__)

@app.route("/")
@app.route("/health")
def home():
    return "USDT P2P EXCHANGE BOT IS LIVE 24/7!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10001))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

# --- Direct Safe Notification to Admin ---
def notify_admin(chat_id, caption_text, photo_id=None, markup=None):
    for attempt in range(3):
        try:
            if photo_id:
                bot.send_photo(ADMIN_CHAT_ID, photo_id, caption=caption_text, reply_markup=markup, timeout=20)
            else:
                bot.send_message(ADMIN_CHAT_ID, caption_text, reply_markup=markup, timeout=20)
            return True
        except Exception as e:
            print(f"Admin Notification Attempt {attempt+1} Failed: {e}")
            time.sleep(2)
    return False

# --- Keyboards Setup ---
def get_main_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_buy = types.InlineKeyboardButton("💵 Buy USDT", callback_data="buy_usdt")
    btn_sell = types.InlineKeyboardButton("💰 Sell USDT", callback_data="sell_usdt")
    btn_rates = types.InlineKeyboardButton("📊 Live Rates", callback_data="live_rates")
    btn_support = types.InlineKeyboardButton("📞 Admin Support", url=f"https://t.me/{ADMIN_USERNAME}")
    markup.add(btn_buy, btn_sell)
    markup.add(btn_rates, btn_support)
    return markup

def get_cancel_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ Cancel Transaction", callback_data="cancel_action"))
    return markup

# --- Command /start ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        f"👋 Welcome to USDT BUY & SELL P2P Exchange!\n\n"
        f"⚡ Instant & Secure USDT Buy / Sell Service.\n"
        f"👤 Account Title: Munawar Ali\n\n"
        f"🟢 Buy USDT Rate: {BUY_RATE} PKR\n"
        f"🔴 Sell USDT Rate: {SELL_RATE} PKR\n\n"
        f"Neeche diye gaye buttons se apni requirement select karein:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard())

# --- Callback Query Handler ---
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id

    if call.data == "live_rates":
        rates_msg = (
            f"📊 CURRENT P2P RATES\n\n"
            f"🟢 Buy USDT: {BUY_RATE} PKR\n"
            f"🔴 Sell USDT: {SELL_RATE} PKR\n"
            f"👤 Account Title: Munawar Ali\n\n"
            f"✨ Fast & Instant Transactions!"
        )
        bot.answer_callback_query(call.id, "Rates Updated!")
        bot.send_message(chat_id, rates_msg, reply_markup=get_main_keyboard())

    elif call.data == "buy_usdt":
        user_states[chat_id] = "WAITING_BUY_PROOF"
        buy_text = (
            f"💵 BUY USDT ORDER\n\n"
            f"📌 Current Rate: 1 USDT = {BUY_RATE} PKR\n"
            f"👤 Account Title (All): Munawar Ali\n\n"
            f"💳 Deposit Accounts (PKR):\n"
            f"🔸 JazzCash: {JAZZCASH_NO} ({JAZZCASH_NAME})\n"
            f"🔸 SadaPay: {SADAPAY_NO} ({SADAPAY_NAME})\n\n"
            f"👇 Instructions:\n"
            f"1. Upar diye gaye kisi bhi account par payment send karein.\n"
            f"2. Niche '✅ Payment Done (Send Screenshot)' button par click karein."
        )
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("✅ Payment Done (Send Screenshot)", callback_data="upload_buy_ss"))
        markup.add(types.InlineKeyboardButton("❌ Cancel Order", callback_data="cancel_action"))
        bot.edit_message_text(buy_text, chat_id, call.message.message_id, reply_markup=markup)

    elif call.data == "upload_buy_ss":
        bot.send_message(chat_id, "📸 Meharbani karke apni Payment ka Screenshot aur apna USDT Wallet Address (BEP20 / TRC20) yahan send karein:", reply_markup=get_cancel_keyboard())

    elif call.data == "sell_usdt":
        user_states[chat_id] = "WAITING_SELL_DETAILS"
        sell_text = (
            f"💰 SELL USDT ORDER\n\n"
            f"📌 Current Rate: 1 USDT = {SELL_RATE} PKR\n\n"
            f"🌐 Our Deposit Wallet Addresses:\n"
            f"🔹 BEP20 (BSC):\n{BSC_BEP20_WALLET}\n\n"
            f"🔹 TRC20 (Tron):\n{TRX_TRC20_WALLET}\n\n"
            f"👇 Step 1: Upar diye gaye address par USDT send karein.\n"
            f"👇 Step 2: Apna receiving account dene ke liye niche '📝 Enter Receiving Details' par click karein."
        )
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("📝 Enter Receiving Details", callback_data="input_sell_info"))
        markup.add(types.InlineKeyboardButton("❌ Cancel Order", callback_data="cancel_action"))
        bot.edit_message_text(sell_text, chat_id, call.message.message_id, reply_markup=markup)

    elif call.data == "input_sell_info":
        info_prompt = (
            f"📝 Apni Payment Details Likhein:\n\n"
            f"Meharbani karke message mein apna receiving account batayein:\n"
            f"• JazzCash / EasyPaisa / SadaPay / NayaPay / UPaisa / Commercial Bank Name\n"
            f"• Account Number / IBAN\n"
            f"• Account Title\n\n"
            f"*(Saari details likh kar sath transfer ka Screenshot bhi bhej dein)*"
        )
        bot.send_message(chat_id, info_prompt, reply_markup=get_cancel_keyboard())

    elif call.data == "cancel_action":
        user_states.pop(chat_id, None)
        bot.send_message(chat_id, "❌ Transaction Cancelled.", reply_markup=get_main_keyboard())

    elif call.data.startswith("approve_"):
        target_user = call.data.split("_")[1]
        bot.send_message(target_user, "🎉 Order Approved! Aapki transaction successfully verify ho gayi hai. Shukriya!")
        try:
            bot.edit_message_caption(call.message.caption + "\n\n✅ STATUS: APPROVED BY ADMIN", chat_id, call.message.message_id)
        except Exception:
            pass

    elif call.data.startswith("reject_"):
        target_user = call.data.split("_")[1]
        bot.send_message(target_user, "❌ Order Rejected! Aapki payment / screenshot verify nahi ho saki. Direct Support se raabta karein.")
        try:
            bot.edit_message_caption(call.message.caption + "\n\n❌ STATUS: REJECTED BY ADMIN", chat_id, call.message.message_id)
        except Exception:
            pass

# --- Handle User Screenshots & Details ---
@bot.message_handler(content_types=['photo', 'text'])
def handle_user_proof(message):
    chat_id = message.chat.id
    state = user_states.get(chat_id)

    if state in ["WAITING_BUY_PROOF", "WAITING_SELL_DETAILS"]:
        user_name = message.from_user.first_name
        username = f"@{message.from_user.username}" if message.from_user.username else "No Username"
        order_type = "BUY USDT REQUEST" if state == "WAITING_BUY_PROOF" else "SELL USDT REQUEST"

        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        admin_markup.add(
            types.InlineKeyboardButton("✅ Approve Order", callback_data=f"approve_{chat_id}"),
            types.InlineKeyboardButton("❌ Reject Order", callback_data=f"reject_{chat_id}")
        )

        caption_text = (
            f"🔔 NEW P2P NOTIFICATION ({order_type})\n\n"
            f"👤 User: {user_name} ({username})\n"
            f"🆔 User Chat ID: {chat_id}\n"
        )
        if message.text:
            caption_text += f"\n📝 User Message / Details:\n{message.text}\n"

        photo_id = message.photo[-1].file_id if message.photo else None

        # Directly notify admin
        success = notify_admin(chat_id, caption_text, photo_id=photo_id, markup=admin_markup)

        if success:
            bot.send_message(chat_id, "⏳ Request Submitted Successfully! Aapka screenshot aur details Admin ko bhej di gayi hain. Jald hi verification mukammal ho jayegi.", reply_markup=get_main_keyboard())
        else:
            bot.send_message(chat_id, "⚠️ Request submit karne mein masla aaya hai. Barah-e-karam dobara koshish karein.", reply_markup=get_main_keyboard())

        user_states.pop(chat_id, None)

    else:
        bot.send_message(chat_id, "Main Menu se option select karein:", reply_markup=get_main_keyboard())

# --- Bot Runner ---
if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    while True:
        try:
            bot.polling(none_stop=True, interval=1, timeout=30)
        except Exception as e:
            print(f"P2P Bot Error: {e}")
            time.sleep(5)
  
