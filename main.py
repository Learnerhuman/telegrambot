from telegram.ext import ApplicationBuilder
from handlers import get_handlers

TOKEN = "8253106142:AAGfq_ez0hhVxnCNhhlGxmBaJpCzjJTvcXE"  # BotFather bergan tokenni shu yerga yozing

app = ApplicationBuilder().token(TOKEN).build()
for handler in get_handlers():
    app.add_handler(handler)

app.run_polling()
