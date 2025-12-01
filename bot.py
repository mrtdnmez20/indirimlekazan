import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# ========================
# BOT AYARLARI
# ========================
BOT_TOKEN = "8184765049:AAGS-X9Qa829_kV7hiWFistjN3G3QdJs1SY"
ADMIN_ID = 5250165372  # Senin Telegram ID'n
TARGET_CHANNEL = "@indirimlekazan"  # Ana kanal

# Takip edilecek kanallar
WATCH_CHANNELS = [
    "@kazanindirimle",
    "@indirimalarmiAmazon",
    "@indirimalarmiTrendyol",
    "@indirimalarmiHepsiburada",
    "@indirimalarmiPazarama",
    "@indirimalarmiElektronik",
    "@indirimalarmiEvYasam",
    "@enesozen",
    "@indirimdeal"
]

# ========================
# LOGGING
# ========================
logging.basicConfig(level=logging.INFO)

# ========================
# GOOGLE ARAMA LINKİ
# ========================
def google_link(text):
    from urllib.parse import quote
    return f"https://www.google.com/search?q={quote(text)}"

# ========================
# YENİ MESAJI ADMİN'E GÖNDER
# ========================
async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.channel_post
    text = message.text or message.caption or "Ürün açıklaması bulunamadı"
    
    g_link = google_link(text)

    # ONAY / RED butonları
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✔ ONAYLA", callback_data=f"ok|{message.chat_id}|{message.message_id}"),
            InlineKeyboardButton("✖ SİL", callback_data="del")
        ]
    ])

    # Admin'e DM gönder
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🔔 *Yeni Ürün Yakalandı!*\n\n{text}\n\n🔎 [Google'da Ara]({g_link})",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# ========================
# BUTON İŞLEMLERİ
# ========================
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "del":
        await query.edit_message_text("❌ Ürün reddedildi.")
        return

    _, chat_id, msg_id = query.data.split("|")
    chat_id = int(chat_id)
    msg_id = int(msg_id)

    try:
        await context.bot.forward_message(
            chat_id=TARGET_CHANNEL,
            from_chat_id=chat_id,
            message_id=msg_id
        )
        await query.edit_message_text("✔ Ürün onaylandı ve kanala gönderildi!")
    except Exception as e:
        await query.edit_message_text(f"Hata: {e}")

# ========================
# BOTU BAŞLAT
# ========================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Buton handler
    app.add_handler(CallbackQueryHandler(callback_handler))

    # Kanal mesajlarını dinleme
    for ch in WATCH_CHANNELS:
        app.add_handler(MessageHandler(filters.Chat(username=ch) & filters.ALL, forward_to_admin))

    app.run_polling()

if __name__ == "__main__":
    main()
