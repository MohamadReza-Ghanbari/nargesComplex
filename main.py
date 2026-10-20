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

        # خواندن ماه‌ها از سطر اول ستون‌های مربوطه
        month_current = "—"
        month_civil = "—"
        if "monthCurrent" in df.columns and pd.notna(
            df["monthCurrent"].iloc[0]
        ):
            month_current = str(df["monthCurrent"].iloc[0]).strip()
        if "monthCivil" in df.columns and pd.notna(df["monthCivil"].iloc[0]):
            month_civil = str(df["monthCivil"].iloc[0]).strip()

        unit_data = df[df["Unit"] == int(unit_number)]

        if not unit_data.empty:
            return {
                "status": "ok",
                "current": int(unit_data.iloc[0]["CurrentCharge"]),
                "civil": int(unit_data.iloc[0]["CivilCharge"]),
                "month_current": month_current,
                "month_civil": month_civil,
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
            current_val = data["current"]
            civil_val = data["civil"]
            m_current = data["month_current"]
            m_civil = data["month_civil"]

            # تعیین وضعیت متنی شارژ جاری
            if current_val > 0:
                current_text = f"🔹 **شارژ جاری:** {current_val:,} ریال\n💳 کارت جاری: `{current_card_display}`\n👤 به نام: {owner_current_card}"
            elif current_val == 0:
                current_text = "🔹 **شارژ جاری:** ۰ ریال (تسویه کامل ✅)"
            else:
                current_text = f"🔹 **شارژ جاری:** {abs(current_val):,} ریال (بستانکار 🟢)"

            # تعیین وضعیت متنی شارژ عمرانی
            if civil_val > 0:
                civil_text = f"🔸 **شارژ عمرانی:** {civil_val:,} ریال\n💳 کارت عمرانی: `{civil_card_display}`\n👤 به نام: {owner_civil_card}"
            elif civil_val == 0:
                civil_text = "🔸 **شارژ عمرانی:** ۰ ریال (تسویه کامل ✅)"
            else:
                civil_text = f"🔸 **شارژ عمرانی:** {abs(civil_val):,} ریال (بستانکار 🟢)"

            # متن اصلی پیام صورت‌حساب
            main_text = (
                f"🏢 **صورت‌حساب واحد {user_input}**\n\n"
                f"🗓 وضعیت شارژ جاری تا پایان **{m_current} ماه**\n"
                f"{current_text}\n\n"
                f"🗓 وضعیت شارژ عمرانی تا پایان **{m_civil} ماه**\n"
                f"{civil_text}\n"
            )

            # اگر حداقل یکی از شارژها بدهکاری داشته باشد، بخش راهنمای کپی ارسال می‌شود
            if current_val > 0 or civil_val > 0:
                main_text += (
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"جهت کپی راحت مبالغ و شماره کارت‌ها در پیام‌های مجزای زیر ارسال می‌شوند.\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"📌 **راهنمای پرداخت سریع در بله:**\n"
                    f"ابتدا مبلغ را کپی نمایید، سپس با لمس شماره کارت مستقیماً وارد صفحه انتقال وجه شده و مبلغ را درج فرمایید."
                )

            bot.reply_to(message, main_text, parse_mode="Markdown")

            # ارسال پیام‌های کپی آسان برای شارژ جاری (صرفاً در صورت بدهکاری)
            if current_val > 0:
                bot.send_message(
                    message.chat.id,
                    f"🔹 **مبلغ شارژ جاری واحد {user_input} (ریال):**",
                    parse_mode="Markdown",
                )
                bot.send_message(message.chat.id, str(current_val))

                bot.send_message(
                    message.chat.id,
                    f"💳 **شماره کارت شارژ جاری**\n👤 {owner_current_card}:",
                    parse_mode="Markdown",
                )
                bot.send_message(message.chat.id, str(current_card))

            # ارسال پیام‌های کپی آسان برای شارژ عمرانی (صرفاً در صورت بدهکاری)
            if civil_val > 0:
                bot.send_message(
                    message.chat.id,
                    f"🔸 **مبلغ شارژ عمرانی واحد {user_input} (ریال):**",
                    parse_mode="Markdown",
                )
                bot.send_message(message.chat.id, str(civil_val))

                bot.send_message(
                    message.chat.id,
                    f"💳 **شماره کارت شارژ عمرانی**\n👤 {owner_civil_card}:",
                    parse_mode="Markdown",
                )
                bot.send_message(message.chat.id, str(civil_card))

            # پیام پایانی راهنما
            bot.send_message(
                message.chat.id,
                f"━━━━━━━━━━━━━━━━━━\nجهت استعلام مجدد، لطفاً شماره واحد خود را ارسال فرمایید.",
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
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

    print("Bot is running...")
    bot.infinity_polling()
