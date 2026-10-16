import os
from threading import Thread
from flask import Flask
import pandas as pd
import telebot

# --- راه‌اندازی سرور وب کوچک برای زنده نگه‌داشتن ربات در Render ---
app = Flask(__name__)


@app.route("/")
def home():
    return "Bale Bot is Alive!"


def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


# --- تنظیمات ربات بله ---
TOKEN = "1369540100:-7y88H-OWPGtk6aigvZR-A1j3p9uroZzd7k"
month = "مهر"

current_card = "5022291346694001"
current_card_display = "5022-2913-4669-4001"
civil_card = "6037998184734357"
civil_card_display = "6037-9981-8473-4357"

owner_current_card = "آقایان جواد رضائی و حمید نامدار مطلق"
owner_civil_card = "آقایان عباس محمدی و محمود سلطانشاهی سیرچی"

telebot.apihelper.API_URL = "https://tapi.bale.ai/bot{0}/{1}"
bot = telebot.TeleBot(TOKEN)


def get_unit_data(unit_number):
    try:
        df = pd.read_excel("data.xlsx")
        unit_data = df[df["Unit"] == int(unit_number)]

        if not unit_data.empty:
            return {
                "status": "ok",
                "current": int(unit_data.iloc[0]["CurrentCharge"]),
                "civil": int(unit_data.iloc[0]["CivilCharge"]),
            }
        else:
            return {"status": "not_found"}
    except Exception as e:
        print(f"Error reading excel: {e}")
        return {"status": "error"}


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(
        message,
        "👋 سلام و احترام؛\n"
        "لطفاً **شماره واحد** خود را به صورت عدد وارد نمایید:",
        parse_mode="Markdown",
    )


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_input = message.text.strip()

    if user_input.isdigit():
        data = get_unit_data(user_input)

        if data["status"] == "ok":
            main_text = (
                f"🏢 **صورت‌حساب واحد {user_input}**\n"
                f"🗓 وضعیت تا پایان **{month} ماه**\n\n"
                f"🔹 **شارژ جاری:** {data['current']:,} ریال\n"
                f"💳 کارت جاری: `{current_card_display}`\n"
                f"👤 به نام: {owner_current_card}\n\n"
                f"🔸 **شارژ عمرانی:** {data['civil']:,} ریال\n"
                f"💳 کارت عمرانی: `{civil_card_display}`\n"
                f"👤 به نام: {owner_civil_card}\n\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"جهت کپی راحت مبالغ و شماره کارت‌ها در پیام‌های مجزای زیر ارسال می‌شوند.\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"📌 **راهنمای پرداخت سریع در بله:**\n"
                f"ابتدا مبلغ را کپی نمایید، سپس با لمس شماره کارت مستقیماً وارد صفحه انتقال وجه شده و مبلغ را درج فرمایید."
            )
            bot.reply_to(message, main_text, parse_mode="Markdown")

            bot.send_message(
                message.chat.id,
                f"🔹 **مبلغ شارژ جاری واحد {user_input} (ریال):**",
                parse_mode="Markdown",
            )
            bot.send_message(message.chat.id, str(data["current"]))

            bot.send_message(
                message.chat.id,
                f"💳 **شماره کارت شارژ جاری**\n👤 {owner_current_card}:",
                parse_mode="Markdown",
            )
            bot.send_message(message.chat.id, str(current_card))

            bot.send_message(
                message.chat.id,
                f"🔸 **مبلغ شارژ عمرانی واحد {user_input} (ریال):**",
                parse_mode="Markdown",
            )
            bot.send_message(message.chat.id, str(data["civil"]))

            bot.send_message(
                message.chat.id,
                f"💳 **شماره کارت شارژ عمرانی**\n👤 {owner_civil_card}:",
                parse_mode="Markdown",
            )
            bot.send_message(message.chat.id, str(civil_card))

            bot.send_message(
                message.chat.id,
                f"━━━━━━━━━━━━━━━━━━\nلطفاً شماره واحد خود را ارسال نمایید.",
            )

        elif data["status"] == "not_found":
            bot.reply_to(
                message,
                f"❌ شماره واحد **{user_input}** در سامانه ثبت نشده است. لطفاً شماره واحد را بررسی کرده و مجدداً ارسال کنید.",
                parse_mode="Markdown",
            )
        else:
            bot.reply_to(
                message,
                "⚠️ متأسفانه در فراخوانی اطلاعات خطایی رخ داد. لطفاً دقایقی دیگر مجدداً تلاش نمایید.",
            )
    else:
        bot.reply_to(
            message,
            "⚠️ لطفاً شماره واحد را تنها به صورت **عدد** ارسال فرمایید.",
            parse_mode="Markdown",
        )


if __name__ == "__main__":
    # اجرای وب‌سرور در پس‌زمینه
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

    print("Bot is running...")
    bot.infinity_polling()
