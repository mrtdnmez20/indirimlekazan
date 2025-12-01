import re
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import hashlib

# ========================
# BOT AYARLARI
# ========================
BOT_TOKEN = "8515438168:AAEEgYfGV_0yF4ayUDj8NNO_ZJ7_60PVXwQ"
ADMIN_ID = 5250165372
TARGET_CHANNEL = "@indirimlekazan"
WATCH_CHANNELS = ["@kazanindirimle"]

logging.basicConfig(level=logging.INFO)

def google_link(text):
    from urllib.parse import quote
    return f"https://www.google.com/search?q={quote(text)}"

# ------------------------
# YENİ MESAJI ADMİN'E GÖNDER
# ------------------------
async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.channel_post
    if not message:
        return

    text = message.text or message.caption or ""
    url_match = re.search(r'(https?://\S+)', text)
    if not url_match:
        return

    product_url = url_match.group(1)
    title = text.split("\n")[0][:100]

    # callback_data için kısa hash
    callback_id = hashlib.md5(f"{title}{product_url}".encode()).hexdigest()

    g_link = google_link(title)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✔ ONAYLA", callback_data=f"ok|{callback_id}|{title}|{product_url}"),
            InlineKeyboardButton("✖ SİL", callback_data=f"del|{callback_id}")
        ]
    ])

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🔔 *Yeni Ürün!*\n\n*{title}*\n{product_url}\n\n🔎 [Google'da Ara]({g_link})",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# ------------------------
# BUTON İŞLEMLERİ
# ------------------------
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("del"):
        await query.edit_message_text("❌ Ürün reddedildi.")
        return

    _, callback_id, title, product_url = query.data.split("|")
    g_link = google_link(title)

    await context.bot.send_message(
        chat_id=TARGET_CHANNEL,
        text=f"🔔 *Yeni Ürün!*\n\n*{title}*\n{product_url}\n\n🔎 [Google'da Ara]({g_link})",
        parse_mode="Markdown"
    )

    await query.edit_message_text("✔ Ürün onaylandı ve kanala gönderildi!")

# ------------------------
# BOTU BAŞLAT
# ------------------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CallbackQueryHandler(callback_handler))

    for ch in WATCH_CHANNELS:
        app.add_handler(MessageHandler(filters.Chat(username=ch) & filters.ALL, forward_to_admin))

    app.run_polling()

if __name__ == "__main__":
    main()
