import json
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

user_data = {}

ADMIN_ID =6238734044
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Sizning ID: {update.effective_user.id}")


def get_handlers():
    return [
        CommandHandler("start", start),
        MessageHandler(filters.CONTACT, save_contact),
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text),
        CallbackQueryHandler(select_direction),
        CommandHandler("cancel", cancel_data),
        CommandHandler("reyting", show_rating),
        CommandHandler("id", get_id),
        CommandHandler("admin", show_all_data),
        CommandHandler("count_users", count_users),
        CommandHandler("delete", delete_user),
        CommandHandler("update", update_score)
    ]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = f"""👋 Assalomu alaykum, {user.first_name}!

📌 Ushbu bot orqali siz quyidagi bosqichlar orqali ro'yxatdan o'tasiz:

Telefon raqamingizni yuborasiz  
Ism va familiyangizni kiritasiz  
Yo'nalish tanlaysiz: 
    - Iqtisodiyot
    - Soliq
    - Moliya
    - Menejment
    - Bank ishi
    - Jahon iqtisodiyoti  
0 < x ≤ 100 oraliqda ball kiritasiz  
Kiritgan ma'lumotingiz reytingga qo'shiladi  
Istalgan vaqtda:
    /cancel — ma'lumotlaringizni o'chirish  
    /reyting — yo'nalishiz bo'yicha reytingni ko'rish  
 Ma'lumot o'chirilgandan so'ng /start orqali qayta kiritishingiz mumkin

📞 Davom etish uchun telefon raqamingizni yuboring.
"""

    button = [[KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)]]
    await update.message.reply_text(welcome_text, 
        reply_markup=ReplyKeyboardMarkup(button, one_time_keyboard=True, resize_keyboard=True))


async def save_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    user_id = update.effective_user.id
    user_data[user_id] = {"phone": contact.phone_number}
    await update.message.reply_text("Raqam qabul qilindi. Ismingizni kiriting:\nBekor qilish uchun /cancel", reply_markup=ReplyKeyboardRemove())

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id not in user_data:
        await update.message.reply_text("Iltimos, avval /start ni bosing.")
        return

    data = user_data[user_id]

    if "first_name" not in data:
        data["first_name"] = text
        await update.message.reply_text("Familiyangizni kiriting:\nBekor qilish uchun /cancel")
    elif "last_name" not in data:
        data["last_name"] = text
        await send_direction_buttons(update)
    elif "direction" in data and "score" not in data:
        try:
            score = float(text)
            if 56 <= score <= 100:
                data["score"] = score
                save_user_data(user_id, data)
                await update.message.reply_text("""Ma'lumotlar saqlandi. Rahmat!\nReytingni ko'rish uchun bosing /reyting\nAgar noto'gri ma'lumot kiritgan bo'lsangiz /cancel""", reply_markup=ReplyKeyboardRemove())
            else:
                await update.message.reply_text("Iltimos, ballni 0 dan katta va 100 dan kichik qilib kiriting.\nBekor qilish uchun /cancel")
        except ValueError:
            await update.message.reply_text("Faqat son kiriting (56 <= x ≤ 100).\nBekor qilish uchun /cancel")
    else:
        await update.message.reply_text("Siz allaqachon ma'lumot kiritgansiz\n/cancel orqali o'chiring.")

async def send_direction_buttons(update: Update):
    buttons = [
        [InlineKeyboardButton("Iqtisodiyot", callback_data="Iqtisodiyot")],
        [InlineKeyboardButton("Soliq", callback_data="Soliq")],
        [InlineKeyboardButton("Moliya", callback_data="Moliya")],
        [InlineKeyboardButton("Menejment", callback_data="Menejment")],
        [InlineKeyboardButton("Bank ishi", callback_data="Bank ishi")],
        [InlineKeyboardButton("Jahon iqtisodiyoti", callback_data="Jahon iqtisodiyoti")],
    ]
    markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("Yo'nalishni tanlang:", reply_markup=markup)

async def select_direction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    direction = update.callback_query.data
    user_data[user_id]["direction"] = direction
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(f"Tanlangan yo'nalish: {direction}\nEndi ballni kiriting (56<= x ≤ 100):\nBekor qilish uchun /cancel")

def save_user_data(user_id, data):
    try:
        with open("data.json", "r") as f:
            all_data = json.load(f)
    except FileNotFoundError:
        all_data = {}

    all_data[str(user_id)] = data
    with open("data.json", "w") as f:
        json.dump(all_data, f, indent=4)

async def cancel_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    try:
        with open("data.json", "r") as f:
            all_data = json.load(f)
    except FileNotFoundError:
        all_data = {}

    if user_id in all_data:
        del all_data[user_id]
        with open("data.json", "w") as f:
            json.dump(all_data, f, indent=4)
        await update.message.reply_text("Ma'lumotlaringiz o'chirildi. Qayta boshlash uchun /start ni bosing.")
    else:
        await update.message.reply_text("Sizda saqlangan ma'lumot yo'q, boshlash uchun /start ni bosing.")

async def show_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open("data.json", "r") as f:
            all_data = json.load(f)
    except FileNotFoundError:
        await update.message.reply_text("Hozircha reyting mavjud emas, boshlash uchun /start ni bosing.")
        return

    direction_users = {}
    for user in all_data.values():
        dir = user["direction"]
        if dir not in direction_users:
            direction_users[dir] = []
        direction_users[dir].append((user["first_name"], user["last_name"], user["score"]))

    msg = ""
    for direction, users in direction_users.items():
        users.sort(key=lambda x: x[2], reverse=True)
        msg += f"\n🏅 {direction}:\n"
        for i, (ism, fam, ball) in enumerate(users, 1):
            msg += f"{i}. {ism} {fam} — {ball}\n"

    await update.message.reply_text(msg or "Reyting mavjud emas, boshlash uchun /start ni bosing.")

async def show_all_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Siz admin emassiz.")
        return

    try:
        with open("data.json", "r") as f:
            all_data = json.load(f)
        msg = ""
        for uid, data in all_data.items():
            msg += f"{data['first_name']} {data['last_name']} ({data['direction']}) — {data['score']}\n"
        await update.message.reply_text(msg or "Hech kim ro'yxatdan o'tmagan.")
    except:
        await update.message.reply_text("⚠️ Ma'lumotlarni o'qishda xatolik.")

async def count_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        with open("data.json", "r") as f:
            all_data = json.load(f)
        await update.message.reply_text(f"👥 Foydalanuvchilar soni: {len(all_data)}")
    except:
        await update.message.reply_text("Xatolik yuz berdi.")

async def delete_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    args = context.args
    if not args:
        await update.message.reply_text("Foydalanuvchi ID sini kiriting. Misol: /ochirish 123456789")
        return
    uid = args[0]
    try:
        with open("data.json", "r") as f:
            all_data = json.load(f)
        if uid in all_data:
            del all_data[uid]
            with open("data.json", "w") as f:
                json.dump(all_data, f, indent=4)
            await update.message.reply_text("✅ Foydalanuvchi o'chirildi.")
        else:
            await update.message.reply_text("🔍 Bu ID ro'yxatda topilmadi.")
    except:
        await update.message.reply_text("⚠️ Xatolik yuz berdi.")
async def update_score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    args = context.args
    if len(args) != 2:
        await update.message.reply_text("Misol: /yangila 123456789 88.5")
        return
    uid, score = args
    try:
        score = float(score)
        if not (56 <= score <= 100):
            raise ValueError
        with open("data.json", "r") as f:
            all_data = json.load(f)
        if uid in all_data:
            all_data[uid]["score"] = score
            with open("data.json", "w") as f:
                json.dump(all_data, f, indent=4)
            await update.message.reply_text("✅ Ball yangilandi.")
        else:
            await update.message.reply_text("ID topilmadi.")
    except:
        await update.message.reply_text("❌ Ballni noto'g'ri kiritdingiz.")


