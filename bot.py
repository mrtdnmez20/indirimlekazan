# bot.py
import logging
import re
import feedparser
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# -------------------------
# Ayarlar
# -------------------------
TOKEN = "8515438168:AAEEgYfGV_0yF4ayUDj8NNO_ZJ7_60PVXwQ"
ONAY_KANAL = 5250165372  # Onaya sunulacak kişi/chat ID
KAYNAK_KANAL = "@kazanindirimle"

# RSS/Feed kaynakları
FEEDLER = [
    "https://www.dhdeals.com/rss",  # Örnek
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
    # Linkleri ayıkla
    linkler = re.findall(r'http[s]?://\S+', mesaj)
    # Başlığı çıkar
    baslik = mesaj.split('\n')[0][:100]  # İlk satır başlık
    # Yüzde indirim algılama
    indirim = re.findall(r'\d{1,3}%', mesaj)
    indirim = indirim[0] if indirim else ""
    # Gereksiz emojileri temizle
    mesaj = re.sub(r'[^\w\s%.-]', '', mesaj)
    # Formatı hazırla
    temiz_mesaj = f"{baslik} {indirim}\n{', '.join(linkler)}"
    return temiz_mesaj

# -------------------------
# Onay için inline buton
# -------------------------
async def gonder_onay(update_or_bot, context, mesaj, chat_id=None):
    keyboard = [
        [InlineKeyboardButton("Paylaş", callback_data=f"paylas|{mesaj}")],
        [InlineKeyboardButton("Reddet", callback_data="reddet")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if chat_id:
        await context.bot.send_message(chat_id=chat_id, text=mesaj, reply_markup=reply_markup)
    else:
        await update_or_bot.message.reply_text(mesaj, reply_markup=reply_markup)

# -------------------------
# Callback handler
# -------------------------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("paylas|"):
        mesaj = data.split("|", 1)[1]
        await context.bot.send_message(chat_id=ONAY_KANAL, text=mesaj)
        await query.edit_message_text(text=f"Paylaşıldı ✅\n\n{mesaj}")
    elif data == "reddet":
        await query.edit_message_text(text="Reddedildi ❌")

# -------------------------
# Kanal mesajlarını yakalama
# -------------------------
async def kanal_mesaj(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.username == KAYNAK_KANAL.replace("@", ""):
        temiz = temizle(update.message.text)
        await gonder_onay(update, context, temiz)

# -------------------------
# RSS/Feed kontrol fonksiyonu
# -------------------------
async def feed_kontrol(context: ContextTypes.DEFAULT_TYPE):
    for feed_url in FEEDLER:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:5]:  # Son 5 ürünü al
            mesaj = f"{entry.title}\n{entry.link}"
            temiz = temizle(mesaj)
            await gonder_onay(context.bot, context, temiz, chat_id=ONAY_KANAL)

# -------------------------
# Bot başlat
# -------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot çalışıyor. Gelen ürünler onayına sunulacak.")

# -------------------------
# Main
# -------------------------
app = ApplicationBuilder().token(TOKEN).build()

# Komut ve handlerlar
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & filters.Chat(username=KAYNAK_KANAL.replace("@", "")), callback=kanal_mesaj))
app.add_handler(CallbackQueryHandler(button))

# Her 10 dakikada bir RSS/Feed kontrolü
job_queue = app.job_queue
job_queue.run_repeating(feed_kontrol, interval=600, first=10)

app.run_polling()
