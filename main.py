import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)
import requests

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

ASK_PROMPT = 1

main_menu = [
    ["Студент"],
    ["IT-технології"],
    ["Контакти"],
    ["Prompt Gemini"]
]
reply_markup = ReplyKeyboardMarkup(main_menu, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! Обери пункт меню:",
        reply_markup=reply_markup
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Студент":
        await update.message.reply_text("Шульга Кирил Владиславович\nГрупа: ІО-24")
    elif text == "IT-технології":
        await update.message.reply_text(
            "Мови програмування: JavaScript, Python, Java, PHP\n"
            "Операційні системи: Windows, Linux\n"
            "Бази даних: MySQL, MongoDB\n"
            "ІDE: PhPStorm, PyCharm, Visual Studio Code, IntelliJ IDEA\n"
        )
    elif text == "Контакти":
        await update.message.reply_text(
            "Телефон: +380502320239\nEmail: shulga.kirill01@gmail.com"
        )
    elif text == "Prompt Gemini":
        await update.message.reply_text("Введи слово або фразу, для якої підібрати синоніми:")
        return ASK_PROMPT
    else:
        await update.message.reply_text("Я не розумію цю команду. Обери пункт меню.")


async def handle_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_prompt = update.message.text

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": f"Підбери ввічливі синоніми до слова або фрази: {user_prompt}"}
                ]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        try:
            answer = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            await update.message.reply_text(f"Синоніми до *{user_prompt}*:\n{answer}", parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text("Не вдалося розібрати відповідь від Gemini API.")
    else:
        await update.message.reply_text("Помилка при зверненні до Gemini API.")

    return ConversationHandler.END


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Prompt Gemini$"), handle_message)],
        states={ASK_PROMPT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_prompt)]},
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущений...")
    app.run_polling()


if __name__ == "__main__":
    main()
