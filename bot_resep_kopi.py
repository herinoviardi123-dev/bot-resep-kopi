"""
Bot Telegram Resep Kopi ☕
Fitur:
- Lihat daftar resep kopi
- Simpan & lihat resep favorit
- Rekomendasi AI menggunakan Claude
- Detail lengkap setiap resep

Cara menjalankan:
1. pip install python-telegram-bot anthropic
2. Ganti BOT_TOKEN dengan token dari BotFather
3. Ganti ANTHROPIC_API_KEY dengan API key dari console.anthropic.com
4. python bot_resep_kopi.py
"""

import os
import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import anthropic

# ===================== KONFIGURASI =====================
# Dibaca otomatis dari Railway Environment Variables
BOT_TOKEN = "8666305875:AAFyZojgPibD_kOK1nA1wBsxNGcKOB75-3E"
ANTHROPIC_API_KEY = "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"
WEBAPP_URL = "https://iridescent-otter-0b20a1.netlify.app/"  # contoh: https://amazing-coffee-123.netlify.app


# ===================== SETUP LOGGING =====================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===================== DATA RESEP KOPI =====================
RESEP_KOPI = {
    "espresso": {
        "nama": "☕ Espresso Klasik",
        "deskripsi": "Kopi pekat Italia yang kuat dan beraroma",
        "bahan": [
            "18g kopi bubuk (sangrai gelap)",
            "30ml air panas (90-95°C)",
        ],
        "langkah": [
            "Timbang 18g kopi bubuk halus",
            "Masukkan ke portafilter dan padatkan (tamp) dengan tekanan 30kg",
            "Pasang portafilter ke mesin espresso",
            "Ekstrak selama 25-30 detik hingga keluar 30ml",
            "Sajikan segera di cangkir yang sudah dipanaskan",
        ],
        "waktu": "5 menit",
        "porsi": "1 shot",
        "tingkat_kesulitan": "⭐⭐⭐",
    },
    "latte": {
        "nama": "🥛 Caffe Latte",
        "deskripsi": "Perpaduan espresso lembut dengan susu steamed yang creamy",
        "bahan": [
            "1 shot espresso (30ml)",
            "200ml susu segar",
            "Gula sesuai selera",
        ],
        "langkah": [
            "Buat 1 shot espresso dan tuang ke gelas",
            "Panaskan susu hingga 60-65°C sambil di-steam",
            "Kocok susu hingga berbusa lembut (microfoam)",
            "Tuang susu perlahan ke espresso dengan gerakan melingkar",
            "Buat latte art jika diinginkan",
        ],
        "waktu": "7 menit",
        "porsi": "1 gelas (230ml)",
        "tingkat_kesulitan": "⭐⭐",
    },
    "cappuccino": {
        "nama": "☁️ Cappuccino",
        "deskripsi": "Espresso dengan lapisan susu dan busa yang seimbang",
        "bahan": [
            "1 shot espresso (30ml)",
            "60ml susu segar",
            "60ml busa susu",
            "Bubuk cokelat untuk taburan",
        ],
        "langkah": [
            "Buat 1 shot espresso di cangkir 150ml",
            "Steam susu hingga berbusa tebal",
            "Tuang susu cair ke espresso (1/3 bagian)",
            "Tambahkan busa susu di atasnya (1/3 bagian)",
            "Taburi bubuk cokelat di atas busa",
        ],
        "waktu": "7 menit",
        "porsi": "1 cangkir (150ml)",
        "tingkat_kesulitan": "⭐⭐",
    },
    "v60": {
        "nama": "🔺 Pour Over V60",
        "deskripsi": "Metode manual yang menghasilkan kopi bersih dan jernih",
        "bahan": [
            "15g kopi bubuk (giling medium-coarse)",
            "250ml air panas (93°C)",
            "Filter kertas V60",
        ],
        "langkah": [
            "Letakkan filter di V60, bilas dengan air panas lalu buang airnya",
            "Masukkan 15g kopi ke filter",
            "Bloom: tuang 30ml air, tunggu 30 detik",
            "Tuang sisa air secara perlahan melingkar dari tengah ke pinggir",
            "Seluruh proses sekitar 3-4 menit",
            "Sajikan segera setelah tetesan terakhir",
        ],
        "waktu": "10 menit",
        "porsi": "1 gelas (200ml)",
        "tingkat_kesulitan": "⭐⭐⭐",
    },
    "cold_brew": {
        "nama": "🧊 Cold Brew",
        "deskripsi": "Kopi dingin yang dibuat dengan ekstraksi lambat selama 12-24 jam",
        "bahan": [
            "100g kopi bubuk (giling kasar)",
            "1 liter air dingin/suhu ruang",
            "Es batu untuk penyajian",
        ],
        "langkah": [
            "Campurkan kopi bubuk dengan air dingin dalam toples",
            "Aduk rata dan tutup rapat",
            "Simpan di kulkas selama 12-24 jam",
            "Saring menggunakan filter/kain saring",
            "Sajikan dengan es batu",
            "Bisa ditambah susu atau simple syrup",
        ],
        "waktu": "12-24 jam",
        "porsi": "4-6 gelas",
        "tingkat_kesulitan": "⭐",
    },
    "dalgona": {
        "nama": "🍮 Dalgona Coffee",
        "deskripsi": "Kopi kocok viral dengan tekstur creamy di atas susu",
        "bahan": [
            "2 sdm kopi instan",
            "2 sdm gula pasir",
            "2 sdm air panas",
            "200ml susu dingin",
            "Es batu",
        ],
        "langkah": [
            "Campurkan kopi instan, gula, dan air panas dalam mangkuk",
            "Kocok dengan mixer/whisk hingga mengembang dan berwarna cokelat muda",
            "Proses mengocok sekitar 5-10 menit dengan tangan",
            "Siapkan gelas dengan es batu dan susu dingin",
            "Sendokkan kopi kocok di atas susu",
            "Aduk sebelum diminum",
        ],
        "waktu": "15 menit",
        "porsi": "1 gelas",
        "tingkat_kesulitan": "⭐",
    },
}

# ===================== PENYIMPANAN FAVORIT =====================
# Format: {user_id: [list of resep keys]}
favorit_pengguna = {}

def simpan_favorit(user_id: int, resep_key: str) -> bool:
    """Simpan resep ke favorit pengguna"""
    if user_id not in favorit_pengguna:
        favorit_pengguna[user_id] = []
    if resep_key not in favorit_pengguna[user_id]:
        favorit_pengguna[user_id].append(resep_key)
        return True
    return False  # Sudah ada di favorit

def hapus_favorit(user_id: int, resep_key: str) -> bool:
    """Hapus resep dari favorit pengguna"""
    if user_id in favorit_pengguna and resep_key in favorit_pengguna[user_id]:
        favorit_pengguna[user_id].remove(resep_key)
        return True
    return False

def cek_favorit(user_id: int, resep_key: str) -> bool:
    """Cek apakah resep sudah di favorit"""
    return user_id in favorit_pengguna and resep_key in favorit_pengguna[user_id]

# ===================== HELPER UI =====================
def buat_keyboard_utama():
    """Buat keyboard menu utama"""
    keyboard = [
        [InlineKeyboardButton(
            "☕ Buka Kalkulator Resep",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )],
        [InlineKeyboardButton("📋 Daftar Resep", callback_data="daftar_resep")],
        [InlineKeyboardButton("❤️ Favorit Saya", callback_data="favorit_saya")],
        [InlineKeyboardButton("🤖 Tanya AI Barista", callback_data="tanya_ai")],
    ]
    return InlineKeyboardMarkup(keyboard)

def buat_keyboard_resep(resep_key: str, user_id: int):
    """Buat keyboard untuk halaman detail resep"""
    is_favorit = cek_favorit(user_id, resep_key)
    tombol_favorit = (
        InlineKeyboardButton("💔 Hapus dari Favorit", callback_data=f"hapus_{resep_key}")
        if is_favorit
        else InlineKeyboardButton("❤️ Simpan ke Favorit", callback_data=f"simpan_{resep_key}")
    )
    keyboard = [
        [tombol_favorit],
        [InlineKeyboardButton("⬅️ Kembali ke Daftar", callback_data="daftar_resep")],
        [InlineKeyboardButton("🏠 Menu Utama", callback_data="menu_utama")],
    ]
    return InlineKeyboardMarkup(keyboard)

def format_resep(resep: dict) -> str:
    """Format detail resep menjadi teks"""
    bahan_list = "\n".join([f"  • {b}" for b in resep["bahan"]])
    langkah_list = "\n".join([f"  {i+1}. {l}" for i, l in enumerate(resep["langkah"])])
    return (
        f"*{resep['nama']}*\n"
        f"_{resep['deskripsi']}_\n\n"
        f"⏱ Waktu: {resep['waktu']}\n"
        f"🍽 Porsi: {resep['porsi']}\n"
        f"🎯 Kesulitan: {resep['tingkat_kesulitan']}\n\n"
        f"*📦 Bahan-bahan:*\n{bahan_list}\n\n"
        f"*📝 Langkah-langkah:*\n{langkah_list}"
    )

# ===================== HANDLER COMMAND =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /start"""
    nama = update.effective_user.first_name
    pesan = (
        f"Halo, *{nama}*! ☕\n\n"
        "Selamat datang di *Bot Resep Kopi*!\n\n"
        "Saya bisa membantu kamu:\n"
        "📋 Melihat berbagai resep kopi\n"
        "❤️ Menyimpan resep favorit\n"
        "🤖 Bertanya ke AI Barista\n\n"
        "Pilih menu di bawah untuk mulai:"
    )
    await update.message.reply_text(
        pesan, parse_mode="Markdown", reply_markup=buat_keyboard_utama()
    )

async def cmd_favorit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /favorit"""
    user_id = update.effective_user.id
    await tampilkan_favorit(update.message, user_id)

async def cmd_daftar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /daftar"""
    await tampilkan_daftar_resep(update.message)

# ===================== HANDLER CALLBACK =====================
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler utama untuk semua callback query"""
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data == "menu_utama":
        nama = query.from_user.first_name
        pesan = (
            f"Halo, *{nama}*! ☕\n\n"
            "Pilih menu di bawah:"
        )
        await query.edit_message_text(
            pesan, parse_mode="Markdown", reply_markup=buat_keyboard_utama()
        )

    elif data == "daftar_resep":
        await tampilkan_daftar_resep(query)

    elif data == "favorit_saya":
        await tampilkan_favorit(query, user_id)

    elif data == "tanya_ai":
        await query.edit_message_text(
            "🤖 *Mode AI Barista Aktif!*\n\n"
            "Ketik pertanyaanmu tentang kopi, misalnya:\n"
            "• _\"Apa bedanya arabika dan robusta?\"_\n"
            "• _\"Rekomendasi kopi untuk pemula\"_\n"
            "• _\"Tips membuat espresso yang enak\"_\n\n"
            "Kirimkan pertanyaanmu sekarang! ☕",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Menu Utama", callback_data="menu_utama")]
            ])
        )
        context.user_data["mode_ai"] = True

    elif data.startswith("detail_"):
        resep_key = data.replace("detail_", "")
        if resep_key in RESEP_KOPI:
            resep = RESEP_KOPI[resep_key]
            teks = format_resep(resep)
            await query.edit_message_text(
                teks,
                parse_mode="Markdown",
                reply_markup=buat_keyboard_resep(resep_key, user_id)
            )

    elif data.startswith("simpan_"):
        resep_key = data.replace("simpan_", "")
        if simpan_favorit(user_id, resep_key):
            await query.answer("❤️ Resep disimpan ke favorit!", show_alert=False)
        else:
            await query.answer("Resep sudah ada di favorit!", show_alert=False)
        # Refresh tombol
        resep = RESEP_KOPI[resep_key]
        await query.edit_message_text(
            format_resep(resep),
            parse_mode="Markdown",
            reply_markup=buat_keyboard_resep(resep_key, user_id)
        )

    elif data.startswith("hapus_"):
        resep_key = data.replace("hapus_", "")
        if hapus_favorit(user_id, resep_key):
            await query.answer("💔 Resep dihapus dari favorit", show_alert=False)
        # Refresh tombol
        resep = RESEP_KOPI[resep_key]
        await query.edit_message_text(
            format_resep(resep),
            parse_mode="Markdown",
            reply_markup=buat_keyboard_resep(resep_key, user_id)
        )

# ===================== FUNGSI TAMPILAN =====================
async def tampilkan_daftar_resep(target):
    """Tampilkan daftar semua resep"""
    keyboard = []
    for key, resep in RESEP_KOPI.items():
        keyboard.append([InlineKeyboardButton(resep["nama"], callback_data=f"detail_{key}")])
    keyboard.append([InlineKeyboardButton("🏠 Menu Utama", callback_data="menu_utama")])

    pesan = "☕ *Daftar Resep Kopi*\n\nPilih resep yang ingin kamu lihat:"
    markup = InlineKeyboardMarkup(keyboard)

    if hasattr(target, "edit_message_text"):
        await target.edit_message_text(pesan, parse_mode="Markdown", reply_markup=markup)
    else:
        await target.reply_text(pesan, parse_mode="Markdown", reply_markup=markup)

async def tampilkan_favorit(target, user_id: int):
    """Tampilkan resep favorit pengguna"""
    favorit = favorit_pengguna.get(user_id, [])

    if not favorit:
        pesan = (
            "❤️ *Favorit Saya*\n\n"
            "Kamu belum menyimpan resep apapun.\n\n"
            "Buka resep dan tekan tombol *❤️ Simpan ke Favorit* untuk menyimpannya!"
        )
        keyboard = [[InlineKeyboardButton("📋 Lihat Daftar Resep", callback_data="daftar_resep")]]
    else:
        pesan = f"❤️ *Favorit Saya* ({len(favorit)} resep)\n\nResep yang sudah kamu simpan:"
        keyboard = []
        for key in favorit:
            if key in RESEP_KOPI:
                resep = RESEP_KOPI[key]
                keyboard.append([InlineKeyboardButton(resep["nama"], callback_data=f"detail_{key}")])
        keyboard.append([InlineKeyboardButton("📋 Semua Resep", callback_data="daftar_resep")])

    keyboard.append([InlineKeyboardButton("🏠 Menu Utama", callback_data="menu_utama")])
    markup = InlineKeyboardMarkup(keyboard)

    if hasattr(target, "edit_message_text"):
        await target.edit_message_text(pesan, parse_mode="Markdown", reply_markup=markup)
    else:
        await target.reply_text(pesan, parse_mode="Markdown", reply_markup=markup)

# ===================== HANDLER PESAN TEKS (AI) =====================
async def handle_pesan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk pesan teks - digunakan untuk mode AI Barista"""
    if not context.user_data.get("mode_ai"):
        await update.message.reply_text(
            "Ketik /start untuk membuka menu utama ☕",
            reply_markup=buat_keyboard_utama()
        )
        return

    pertanyaan = update.message.text
    await update.message.reply_text("🤔 Sedang mencari jawaban...")

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=500,
            system=(
                "Kamu adalah AI Barista profesional yang ahli tentang kopi. "
                "Jawab pertanyaan tentang kopi dalam bahasa Indonesia yang ramah dan informatif. "
                "Berikan tips praktis yang bisa langsung diterapkan. "
                "Gunakan emoji kopi agar lebih menarik. "
                "Jawab dengan singkat namun lengkap, maksimal 300 kata."
            ),
            messages=[{"role": "user", "content": pertanyaan}]
        )
        jawaban = response.content[0].text
        await update.message.reply_text(
            f"🤖 *AI Barista menjawab:*\n\n{jawaban}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❓ Tanya Lagi", callback_data="tanya_ai")],
                [InlineKeyboardButton("🏠 Menu Utama", callback_data="menu_utama")]
            ])
        )
    except Exception as e:
        logger.error(f"Error AI: {e}")
        await update.message.reply_text(
            "⚠️ Maaf, AI Barista sedang tidak tersedia. Coba lagi nanti.",
            reply_markup=buat_keyboard_utama()
        )

    context.user_data["mode_ai"] = False

# ===================== MAIN =====================
def main():
    """Jalankan bot"""
    app = Application.builder().token(BOT_TOKEN).build()

    # Daftarkan handler
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("favorit", cmd_favorit))
    app.add_handler(CommandHandler("daftar", cmd_daftar))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_pesan))

    print("☕ Bot Resep Kopi berjalan...")
    print("Tekan Ctrl+C untuk menghentikan")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
