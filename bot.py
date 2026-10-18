import os
import threading
import time
from flask import Flask
import telebot
from telebot import types

# ---------------- CONFIGURATION ----------------
BOT_TOKEN = "8717353251:AAE_FDKyqxSC3RzvJepJTih6H2K8Y3H9Q-Q"

# Admin Numeric Chat ID
ADMIN_CHAT_ID = 7218404735  
ADMIN_USERNAME = "Qayoom_pitafi05"

# Deposit Accounts (Owner: Munawar Ali)
JAZZCASH_NO = "03299202072"
JAZZCASH_NAME = "Munawar Ali"

SADAPAY_NO = "03252635541"
SADAPAY_NAME = "Munawar Ali"

BSC_BEP20_WALLET = "0x90a2efbc5799c9d41f134d0ea092be6001181382"
TRX_TRC20_WALLET = "TFprkhMJS2jtUGQ6kp6GHomUCwAzWjcPFd"

# Exchange Rates (PKR)
BUY_RATE = 290.22
SELL_RATE = 281.50

bot = telebot.TeleBot(BOT_TOKEN)
user_states = {}
all_users = set()  # Users memory for broadcast

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
    all_users.add(message.chat.id)
    welcome_text = (
        f"👋 Welcome to USDT BUY & SELL P2P Exchange!\n\n"
        f"⚡ Instant & Secure USDT Buy / Sell Service.\n"
        f"👤 Account Title: Munawar Ali\n\n"
        f"🟢 Buy USDT Rate: {BUY_RATE} PKR\n"
        f"🔴 Sell USDT Rate: {SELL_RATE} PKR\n\n"
        f"Neeche diye gaye buttons se apni requirement select karein:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard())

# --- ADMIN COMMAND: Send Direct Message (/send ChatID Message) ---
@bot.message_handler(commands=['send'])
def admin_send_message(message):
    if message.chat.id != ADMIN_CHAT_ID:
        return

    try:
        parts = message.text.split(" ", 2)
        target_chat_id = int(parts[1])
        msg_to_send = parts[2]

        bot.send_message(target_chat_id, f"💬 **Admin Msg:**\n{msg_to_send}", parse_mode="Markdown")
        bot.reply_to(message, f"✅ Message successfully sent to User: `{target_chat_id}`", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, "⚠️ Incorrect Format!\n\nUse: `/send CHAT_ID Your message`", parse_mode="Markdown")

# --- ADMIN COMMAND: Broadcast to All Users (/broadcast Message) ---
@bot.message_handler(commands=['broadcast'])
def admin_broadcast(message):
    if message.chat.id != ADMIN_CHAT_ID:
        return

    try:
        broadcast_msg = message.text.split(" ", 1)[1]
        count = 0
        for uid in list(all_users):
            try:
                bot.send_message(uid, f"📢 **ANNOUNCEMENT:**\n\n{broadcast_msg}", parse_mode="Markdown")
                count += 1
            except Exception:
                pass
        bot.reply_to(message, f"✅ Broadcast sent to {count} active users!")
    except Exception:
        bot.reply_to(message, "⚠️ Incorrect Format!\n\nUse: `/broadcast Your Announcement`", parse_mode="Markdown")

# --- Callback Query Handler ---
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    all_users.add(chat_id)

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
        user_states[chat_id] = {"step": "WAITING_BUY_AMOUNT"}
        msg = (
            f"💵 BUY USDT ORDER\n\n"
            f"📌 Current Rate: 1 USDT = {BUY_RATE} PKR\n\n"
            f"👇 Meharbani karke likhein ke aapko **kitni USDT buy karni hai?**\n"
            f"(Misal ke tor par: `10` ya `50` ya `100` likh kar send karein)"
        )
        bot.edit_message_text(msg, chat_id, call.message.message_id, reply_markup=get_cancel_keyboard(), parse_mode="Markdown")

    elif call.data == "sell_usdt":
        user_states[chat_id] = {"step": "WAITING_SELL_AMOUNT"}
        msg = (
            f"💰 SELL USDT ORDER\n\n"
            f"📌 Current Rate: 1 USDT = {SELL_RATE} PKR\n\n"
            f"👇 Meharbani karke likhein ke aapko **kitni USDT sell karni hai?**\n"
            f"(Misal ke tor par: `10` ya `50` ya `100` likh kar send karein)"
        )
        bot.edit_message_text(msg, chat_id, call.message.message_id, reply_markup=get_cancel_keyboard(), parse_mode="Markdown")

    elif call.data == "cancel_action":
        user_states.pop(chat_id, None)
        bot.send_message(chat_id, "❌ Transaction Cancelled.", reply_markup=get_main_keyboard())

    elif call.data.startswith("approve_"):
        try:
            target_user = int(call.data.split("_")[1])
            bot.answer_callback_query(call.id, "Order Approved Successfully!")
            bot.send_message(target_user, "🎉 Order Approved! Aapki transaction successfully verify ho gayi hai. Shukriya!")
            
            if call.message.photo:
                bot.edit_message_caption(call.message.caption + "\n\n✅ STATUS: APPROVED BY ADMIN", chat_id, call.message.message_id, reply_markup=None)
            else:
                bot.edit_message_text(call.message.text + "\n\n✅ STATUS: APPROVED BY ADMIN", chat_id, call.message.message_id, reply_markup=None)
        except Exception as e:
            print(f"Approve Error: {e}")

    elif call.data.startswith("reject_"):
        try:
            target_user = int(call.data.split("_")[1])
            bot.answer_callback_query(call.id, "Order Rejected.")
            bot.send_message(target_user, "❌ Order Rejected! Aapki payment / screenshot verify nahi ho saki. Direct Support se raabta karein.")
            
            if call.message.photo:
                bot.edit_message_caption(call.message.caption + "\n\n❌ STATUS: REJECTED BY ADMIN", chat_id, call.message.message_id, reply_markup=None)
            else:
                bot.edit_message_text(call.message.text + "\n\n❌ STATUS: REJECTED BY ADMIN", chat_id, call.message.message_id, reply_markup=None)
        except Exception as e:
            print(f"Reject Error: {e}")

# --- Handle User Input, Admin Replies & Mandatory Screenshots ---
@bot.message_handler(content_types=['photo', 'text'])
def handle_user_input(message):
    chat_id = message.chat.id
    all_users.add(chat_id)

    # 1. Admin Quick Reply Feature (Reply to order notification)
    if chat_id == ADMIN_CHAT_ID and message.reply_to_message:
        try:
            target_text = message.reply_to_message.caption or message.reply_to_message.text or ""
            if "ID Chat ID:" in target_text or "Chat ID: " in target_text:
                target_id = int(target_text.split("Chat ID: ")[1].split("\n")[0].strip())
                bot.send_message(target_id, f"💬 **Admin Msg:**\n{message.text}", parse_mode="Markdown")
                bot.reply_to(message, f"✅ Message sent to user `{target_id}`!", parse_mode="Markdown")
                return
        except Exception as e:
            bot.reply_to(message, f"⚠️ Reply failed: {e}")
            return

    state_data = user_states.get(chat_id)

    if not state_data:
        if message.text and not message.text.startswith('/'):
            bot.send_message(chat_id, "Main Menu se option select karein:", reply_markup=get_main_keyboard())
        return

    step = state_data.get("step")

    # 2. Handling Buy Amount Input
    if step == "WAITING_BUY_AMOUNT":
        try:
            usdt_amount = float(message.text.strip())
            if usdt_amount <= 0:
                raise ValueError()
            
            total_pkr = round(usdt_amount * BUY_RATE, 2)
            user_states[chat_id] = {
                "step": "WAITING_BUY_PROOF",
                "usdt": usdt_amount,
                "pkr": total_pkr
            }

            instruction_text = (
                f"🛒 BUY ORDER DETAILS:\n"
                f"🔹 USDT Quantity: {usdt_amount} USDT\n"
                f"💵 Total Payable: **{total_pkr} PKR**\n"
                f"👤 Account Title (All): Munawar Ali\n\n"
                f"💳 Deposit Accounts (PKR):\n"
                f"🔸 JazzCash: `{JAZZCASH_NO}` ({JAZZCASH_NAME})\n"
                f"🔸 SadaPay: `{SADAPAY_NO}` ({SADAPAY_NAME})\n\n"
                f"👇 **Instructions:**\n"
                f"1. Upar diye gaye account par **{total_pkr} PKR** send karein.\n"
                f"2. Payment ka **SCREENSHOT (PHOTO)** lazmi bhejein sath apna **USDT Wallet Address** likh kar."
            )
            bot.send_message(chat_id, instruction_text, reply_markup=get_cancel_keyboard(), parse_mode="Markdown")
        except ValueError:
            bot.send_message(chat_id, "⚠️ Barah-e-karam theek amount likhein (Misal ke tor par: `10` ya `25.5`)", reply_markup=get_cancel_keyboard())

    # 3. Handling Sell Amount Input
    elif step == "WAITING_SELL_AMOUNT":
        try:
            usdt_amount = float(message.text.strip())
            if usdt_amount <= 0:
                raise ValueError()
            
            total_pkr = round(usdt_amount * SELL_RATE, 2)
            user_states[chat_id] = {
                "step": "WAITING_SELL_DETAILS",
                "usdt": usdt_amount,
                "pkr": total_pkr
            }

            sell_text = (
                f"💰 SELL ORDER DETAILS:\n"
                f"🔹 USDT Quantity: {usdt_amount} USDT\n"
                f"💵 You Will Receive: **{total_pkr} PKR**\n\n"
                f"🌐 **Our Deposit Wallet Addresses:**\n"
                f"🔹 BEP20 (BSC):\n`{BSC_BEP20_WALLET}`\n\n"
                f"🔹 TRC20 (Tron):\n`{TRX_TRC20_WALLET}`\n\n"
                f"👇 **Instructions:**\n"
                f"1. Upar diye gaye address par **{usdt_amount} USDT** transfer karein.\n"
                f"2. Apna receiving account (JazzCash/EasyPaisa/Bank) likhein aur transfer ka **SCREENSHOT (PHOTO)** lazmi bhej dein."
            )
            bot.send_message(chat_id, sell_text, reply_markup=get_cancel_keyboard(), parse_mode="Markdown")
        except ValueError:
            bot.send_message(chat_id, "⚠️ Barah-e-karam theek amount likhein (Misal ke tor par: `10` ya `25.5`)", reply_markup=get_cancel_keyboard())

    # 4. Handling Final Proof with Mandatory Screenshot Check
    elif step in ["WAITING_BUY_PROOF", "WAITING_SELL_DETAILS"]:
        if not message.photo:
            bot.send_message(
                chat_id, 
                "⚠️ **Screenshot Missing!**\nBarah-e-karam bagair screenshot ke order submit nahi ho sakta. Apni payment/transfer ka **Screenshot (Photo)** lazmi send karein!", 
                reply_markup=get_cancel_keyboard(), 
                parse_mode="Markdown"
            )
            return

        usdt_amt = state_data.get("usdt", 0)
        pkr_amt = state_data.get("pkr", 0)
        order_type = "BUY USDT" if step == "WAITING_BUY_PROOF" else "SELL USDT"

        user_name = message.from_user.first_name
        username = f"@{message.from_user.username}" if message.from_user.username else "No Username"

        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        admin_markup.add(
            types.InlineKeyboardButton("✅ Approve Order", callback_data=f"approve_{chat_id}"),
            types.InlineKeyboardButton("❌ Reject Order", callback_data=f"reject_{chat_id}")
        )

        caption_text = (
            f"🔔 NEW P2P ORDER ({order_type})\n\n"
            f"👤 User: {user_name} ({username})\n"
            f"🆔 Chat ID: {chat_id}\n"
            f"📊 Amount: {usdt_amt} USDT\n"
            f"💵 Total PKR: {pkr_amt} PKR\n"
        )
        if message.caption:
            caption_text += f"\n📝 User Details / Wallet:\n{message.caption}\n"
        elif message.text:
            caption_text += f"\n📝 User Details / Wallet:\n{message.text}\n"

        photo_id = message.photo[-1].file_id

        success = notify_admin(chat_id, caption_text, photo_id=photo_id, markup=admin_markup)

        if success:
            bot.send_message(chat_id, "⏳ Request Submit Ho Gayi Hai! Aapka screenshot aur details Admin ko bhej di gayi hain. Jald hi verify ho jayega.", reply_markup=get_main_keyboard())
        else:
            bot.send_message(chat_id, "⚠️ Request submit karne mein masla aaya hai. Dobara koshish karein.", reply_markup=get_main_keyboard())

        user_states.pop(chat_id, None)

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
    
