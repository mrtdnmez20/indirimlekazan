# bot.py
import logging
import re
import asyncio
import httpx
import xml.etree.ElementTree as ET
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# -------------------------
# Ayarlar
# -------------------------
TOKEN = "8515438168:AAEEgYfGV_0yF4ayUDj8NNO_ZJ7_60PVXwQ"
ONAY_KANAL = 5250165372  # Senin Telegram ID'n
KAYNAK_KANAL = "@kazanindirimle"

# RSS/Feed kaynakları
FEEDLER = [
    "https://www.dhdeals.com/rss",
    "https://trendyoldeals.com/rss",
    "https://www.amazon.com.tr/buyuk-indirimler/rss",
    "https://www.hepsiburada.com/rss/firsatlar"
]

# -------------------------
# Logging
# -------------------------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# -------------------------
# Ürün temizleme fonksiyonu
# -------------------------
def temizle(mesaj):
    linkler = re.findall(r'http[s]?://\S+', mesaj)
    baslik = mesaj.split('\n')[0][:100]
    indirim = re.findall(r'\d{1,3}%', mesaj)
    indirim = indirim[0] if indirim else ""
    mesaj = re.sub(r'[^\w\s%.-]', '', mesaj)
    temiz_mesaj = f"{baslik} {indirim}\n{', '.join(linkler)}"
    return temiz_mesaj

# -------------------------
# Onay için inline buton
# -------------------------
async def gonder_onay(context, mesaj):
    keyboard = [
        [InlineKeyboardButton("Paylaş", callback_data=f"paylas|{mesaj}")],
        [InlineKeyboardButton("Reddet", callback_data="reddet")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=ONAY_KANAL, text=mesaj, reply_markup=reply_markup)

# -------------------------
# Callback handler
# -------------------------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("paylas|"):
        mesaj = data.split("|", 1)[1]
        await context.bot.send_message(chat_id=KAYNAK_KANAL, text=mesaj)
        await query.edit_message_text(text=f"Paylaşıldı ✅\n\n{mesaj}")
    elif data == "reddet":
        await query.edit_message_text(text="Reddedildi ❌")

# -------------------------
# Kanal mesajlarını yakalama
# -------------------------
async def kanal_mesaj(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.username == KAYNAK_KANAL.replace("@", ""):
        temiz = temizle(update.message.text)
        await gonder_onay(context, temiz)

# -------------------------
# RSS/Feed kontrol fonksiyonu
# -------------------------
async def feed_kontrol(context: ContextTypes.DEFAULT_TYPE):
    async with httpx.AsyncClient() as client:
        for feed_url in FEEDLER:
            try:
                r = await client.get(feed_url, timeout=10)
                root = ET.fromstring(r.text)
                for item in root.findall(".//item")[:5]:
                    title = item.find("title").text if item.find("title") is not None else ""
                    link = item.find("link").text if item.find("link") is not None else ""
                    mesaj = f"{title}\n{link}"
                    temiz = temizle(mesaj)
                    await gonder_onay(context, temiz)
            except Exception as e:
                logging.error(f"RSS hatası {feed_url}: {e}")

# -------------------------
# Bot başlat
# -------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot çalışıyor. Gelen ürünler onayına sunulacak.")

# -------------------------
# Main
# -------------------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & filters.Chat(username=KAYNAK_KANAL.replace("@", "")), callback=kanal_mesaj))
app.add_handler(CallbackQueryHandler(button))

job_queue = app.job_queue
job_queue.run_repeating(feed_kontrol, interval=600, first=10)

app.run_polling()
