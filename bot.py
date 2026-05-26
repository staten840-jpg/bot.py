import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from groq import Groq

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

SYSTEM_PROMPT = """Sen professional futbol tahlilchisisisan. Ismingiz SofaScore AI.

Har bir tahlilda ko'rsat:
⚽ SO'NGGI 5 NATIJA
🏥 TRAVMALAR va DISKVALIFIKATSIYALAR
🔄 TRANSFERLAR TA'SIRI
📊 STATISTIKA xG possession shots
🏆 LIGA XUSUSIYATLARI
🎯 PROGNOZ ishonch foizi bilan

Har doim ozbekcha yoz."""

def analyze(query):
    client = Groq(api_key=GROQ_API_KEY)
    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Tahlil qil: {query}"}
        ],
        max_tokens=3000
    )
    return r.choices[0].message.content

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("⚽ Oyun", callback_data="m"), InlineKeyboardButton("🏟 Jamoa", callback_data="t")],
          [InlineKeyboardButton("🏆 Liga", callback_data="l"), InlineKeyboardButton("📊 Prognoz", callback_data="p")]]
    await update.message.reply_text("🤖 SofaScore AI\n\nQaysi oyun yoki jamoani tahlil qilaman?", reply_markup=InlineKeyboardMarkup(kb))

async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    m = await update.message.reply_text("⏳ Tahlil qilinmoqda...")
    result = analyze(update.message.text)
    await m.delete()
    await update.message.reply_text(result[:4000])

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    hints = {"m": "Misol: Real Madrid vs Barcelona", "t": "Misol: Liverpool holati", "l": "Misol: Premier League", "p": "Misol: PSG vs Bayern prognoz"}
    await q.edit_message_text(hints.get(q.data, "Yozing!"))

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message))
    app.run_polling()

if __name__ == "__main__":
    main()
