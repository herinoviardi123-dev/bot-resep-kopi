"""
☕ Bot Telegram Resep Kopi - PRODUCTION READY

Fitur:
- Daftar resep kopi
- Favorit (persist ke file JSON)
- AI Barista (Claude)
- WebApp integration
- Logging & error handling

Cara jalan:
1. pip install python-telegram-bot anthropic python-dotenv
2. Buat file .env
3. python bot_resep_kopi.py
"""

import os
import json
import logging
from dotenv import load_dotenv
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import anthropic

# ===================== LOAD ENV =====================
load_dotenv()

BOT_TOKEN = "8666305875:AAFyZojgPibD_kOK1nA1wBsxNGcKOB75-3E"
ANTHROPIC_API_KEY = "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"
WEBAPP_URL = "https://iridescent-otter-0b20a1.netlify.app/"  # contoh: https://amazing-coffee-123.netlify.app


# ===================== VALIDASI =====================
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN tidak ditemukan di .env")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY tidak ditemukan di .env")

# ===================== LOGGING =====================
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===================== DATABASE FILE =====================
DB_FILE = "favorit.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

favorit_pengguna = load_db()

# ===================== DATA RESEP =====================
RESEP_KOPI = {
    "espresso": {
        "nama": "☕ Espresso",
        "deskripsi": "Kopi pekat khas Italia",
        "bahan": ["18g kopi", "30ml air"],
        "langkah": ["Tamp kopi", "Ekstrak 25 detik"],
        "waktu": "5 menit",
        "porsi": "1 shot",
        "tingkat_kesulitan": "⭐⭐⭐",
    },
    "latte": {
        "nama": "🥛 Latte",
        "deskripsi": "Espresso + susu creamy",
        "bahan": ["Espresso", "200ml susu"],
        "langkah": ["Buat espresso", "Steam susu", "Tuang"],
        "waktu": "7 menit",
        "porsi": "1 gelas",
        "tingkat_kesulitan": "⭐⭐",
    },
}

# ===================== FAVORIT =====================
def simpan_favorit(user_id, key):
    user_id = str(user_id)
    favorit_pengguna.setdefault(user_id, [])
    if key not in favorit_pengguna[user_id]:
        favorit_pengguna[user_id].append(key)
        save_db(favorit_pengguna)
        return True
    return False

def hapus_favorit(user_id, key):
    user_id = str(user_id)
    if key in favorit_pengguna.get(user_id, []):
        favorit_pengguna[user_id].remove(key)
        save_db(favorit_pengguna)
        return True
    return False

def cek_favorit(user_id, key):
    return key in favorit_pengguna.get(str(user_id), [])

# ===================== UI =====================
def menu_utama():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("☕ Buka WebApp", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton("📋 Resep", callback_data="list")],
        [InlineKeyboardButton("❤️ Favorit", callback_data="fav")],
        [InlineKeyboardButton("🤖 AI Barista", callback_data="ai")],
    ])

def format_resep(r):
    return (
        f"*{r['nama']}*\n_{r['deskripsi']}_\n\n"
        f"⏱ {r['waktu']} | 🍽 {r['porsi']}\n\n"
        f"*Bahan:*\n- " + "\n- ".join(r["bahan"]) +
        f"\n\n*Langkah:*\n- " + "\n- ".join(r["langkah"])
    )

# ===================== HANDLER =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "☕ *Bot Resep Kopi*\nPilih menu:",
        parse_mode="Markdown",
        reply_markup=menu_utama()
    )

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    data = q.data

    if data == "list":
        kb = [[InlineKeyboardButton(v["nama"], callback_data=f"d_{k}")]
              for k, v in RESEP_KOPI.items()]
        kb.append([InlineKeyboardButton("🏠 Menu", callback_data="home")])
        await q.edit_message_text("Pilih resep:", reply_markup=InlineKeyboardMarkup(kb))

    elif data.startswith("d_"):
        key = data[2:]
        r = RESEP_KOPI[key]
        fav = cek_favorit(uid, key)
        btn = "💔 Hapus" if fav else "❤️ Simpan"
        action = "h_" if fav else "s_"

        kb = [
            [InlineKeyboardButton(btn, callback_data=action + key)],
            [InlineKeyboardButton("⬅️", callback_data="list")]
        ]

        await q.edit_message_text(
            format_resep(r),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(kb)
        )

    elif data.startswith("s_"):
        simpan_favorit(uid, data[2:])
        await q.answer("Tersimpan ❤️")

    elif data.startswith("h_"):
        hapus_favorit(uid, data[2:])
        await q.answer("Dihapus 💔")

    elif data == "fav":
        fav = favorit_pengguna.get(str(uid), [])
        if not fav:
            await q.edit_message_text("Belum ada favorit")
            return

        kb = [[InlineKeyboardButton(RESEP_KOPI[k]["nama"], callback_data=f"d_{k}")]
              for k in fav]
        await q.edit_message_text("Favorit kamu:", reply_markup=InlineKeyboardMarkup(kb))

    elif data == "ai":
        context.user_data["ai"] = True
        await q.edit_message_text("Tanya soal kopi ☕")

    elif data == "home":
        await q.edit_message_text("Menu:", reply_markup=menu_utama())

async def ai_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("ai"):
        return

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    try:
        res = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=300,
            messages=[{"role": "user", "content": update.message.text}]
        )

        await update.message.reply_text(res.content[0].text)

    except Exception as e:
        logger.error(e)
        await update.message.reply_text("AI error")

    context.user_data["ai"] = False

# ===================== MAIN =====================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_handler))

    print("Bot jalan...")
    app.run_polling()

if __name__ == "__main__":
    main()
