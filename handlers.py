"""
Telegram handlers for the OTP bot using pyTelegramBotAPI (telebot).
This file wires the bot, handlers, and database helpers together.
"""
import os
import logging
import random
from telebot import TeleBot, types
from db import init_db, get_user, save_user, is_banned, get_all_combos, assign_number_to_user, release_number, get_combo
from utils import safe_html, COUNTRY_CODES, force_sub_markup, force_sub_check
from ivasms import client as ivasms_client

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise SystemExit("BOT_TOKEN must be set in environment")

bot = TeleBot(BOT_TOKEN)

init_db()

ADMIN_IDS = [int(i) for i in os.getenv("ADMIN_IDS","8233900497").split(",") if i]

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if is_banned(user_id):
        bot.reply_to(message, "🚫 You are banned.")
        return

    # force subscribe check
    if not force_sub_check(user_id):
        markup = force_sub_markup()
        if markup:
            bot.send_message(chat_id, "🔒 Please subscribe to the required channels to use the bot.", reply_markup=markup)
        else:
            bot.send_message(chat_id, "🔒 Force-sub enabled but no channels configured.")
        return

    if not get_user(user_id):
        save_user(user_id, username=message.from_user.username or "", first_name=message.from_user.first_name or "", last_name=message.from_user.last_name or "")
        for admin in ADMIN_IDS:
            try:
                bot.send_message(admin, f"New user: {user_id} @{safe_html(message.from_user.username or 'None')}")
            except Exception:
                pass

    # build country buttons
    all_combos = get_all_combos()
    country_combos = {}
    for country_code, combo_index in all_combos:
        country_combos.setdefault(country_code, []).append(combo_index)

    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for country_code, indices in country_combos.items():
        if country_code in COUNTRY_CODES:
            name, flag, _ = COUNTRY_CODES[country_code]
            for idx in indices:
                text = f"{flag} {name}" if len(indices) == 1 else f"{flag} {name} ({idx})"
                buttons.append(types.InlineKeyboardButton(text, callback_data=f"country_{country_code}_{idx}"))
    for i in range(0, len(buttons), 2):
        markup.row(*buttons[i:i+2])

    bot.send_message(chat_id, "Welcome! Choose a country:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("country_"))
def handle_country_selection(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if is_banned(user_id):
        bot.answer_callback_query(call.id, "🚫 You are banned.", show_alert=True)
        return

    if not force_sub_check(user_id):
        bot.answer_callback_query(call.id, "🔒 Please subscribe to the required channels.", show_alert=True)
        return

    parts = call.data.split("_")
    country_code = parts[1]
    combo_index = int(parts[2]) if len(parts) > 2 else 1

    available_numbers = get_combo(country_code, combo_index, user_id)
    if not available_numbers:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="back_to_countries"))
        bot.edit_message_text("❌ No numbers available for this country.", chat_id, message_id, reply_markup=markup)
        return

    assigned = random.choice(available_numbers)
    old_user = get_user(user_id)
    if old_user and old_user[5]:
        release_number(old_user[5])
    assign_number_to_user(user_id, assigned)
    save_user(user_id, country_code=country_code, assigned_number=assigned)

    name, flag, _ = COUNTRY_CODES.get(country_code, ("Unknown", "🌍", ""))
    msg_text = f"◈ Number: <code>+{assigned}</code>\n◈ Country: {flag} {name}\n◈ Combo: #{combo_index}\n◈ Status: Waiting for SMS"

    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("🔄 Change Number", callback_data=f"change_num_{country_code}_{combo_index}"), types.InlineKeyboardButton("🔙 Back", callback_data="back_to_countries"))
    try:
        bot.edit_message_text(text=msg_text, chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="HTML")
        bot.answer_callback_query(call.id, "✅ Number assigned")
    except Exception as e:
        logging.exception(e)

@bot.callback_query_handler(func=lambda call: call.data == "back_to_countries")
def back_to_countries(call):
    send_welcome(call.message)


def start_bot():
    # try to load cookies for ivasms client (best-effort)
    try:
        ivasms_client.load_cookies()
    except Exception:
        pass
    bot.infinity_polling(timeout=30, long_polling_timeout=30)
