import re
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# ========================
# BOT AYARLARI
# ========================
BOT_TOKEN = "8515438168:AAEEgYfGV_0yF4ayUDj8NNO_ZJ7_60PVXwQ"
ADMIN_ID = 5250165372
TARGET_CHANNEL = "@indirimlekazan"
WATCH_CHANNELS = ["@kazanindirimle"]

logging.basicConfig(level=logging.INFO)

# ========================
# GOOGLE
# ========================
def google_link(text):
    from urllib.parse import quote
    return f"https://www.google.com/search?q={quote(text)}"

# ========================
# SAHTE PORT SERVER (Render için)
# ========================
def fake_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is running")

    server = HTTPServer(("0.0.0.0", 10000), Handler)
    server.serve_forever()

# Arka planda fake server başlat
threading.Thread(target=fake_server, daemon=True).start()

# ========================
# ADMINE GÖNDER
# ========================
async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.channel_post
    text = message.text or message.caption or ""

    url_match = re.search(r'(https?://\S+)', text)
    if not url_match:
        return

    product_url = url_match.group(1)
    title = text.split("\n")[0][:150]
    g_link = google_link(title)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✔ ONAYLA", callback_data=f"ok|{title}|{product_url}"),
            InlineKeyboardButton("✖ SİL", callback_data="del")
        ]
    ])

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🔔 *Yeni Ürün!*\n\n*{title}*\n{product_url}\n\n🔎 [Google'da Ara]({g_link})",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# ========================
# BUTON
# ========================
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "del":
        await query.edit_message_text("❌ Ürün reddedildi.")
        return

    _, title, product_url = query.data.split("|")
    g_link = google_link(title)

    await context.bot.send_message(
        chat_id=TARGET_CHANNEL,
        text=f"🔔 *Yeni Ürün!*\n\n*{title}*\n{product_url}\n\n🔎 [Google'da Ara]({g_link})",
        parse_mode="Markdown"
    )

    await query.edit_message_text("✔ Ürün onaylandı ve kanala gönderildi!")

# ========================
# BOT BAŞLAT
# ========================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CallbackQueryHandler(callback_handler))

    for ch in WATCH_CHANNELS:
        app.add_handler(MessageHandler(filters.Chat(username=ch) & filters.ALL, forward_to_admin))

    app.run_polling()

if __name__ == "__main__":
    main()
