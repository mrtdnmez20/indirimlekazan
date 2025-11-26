import os
import requests
from bs4 import BeautifulSoup
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, filters

TOKEN = os.environ['8515438168:AAEEgYfGV_0yF4ayUDj8NNO_ZJ7_60PVXwQ']
KANAL = os.environ['@indirimlekazan']

bot = Bot(token=TOKEN)
updater = Updater(TOKEN, use_context=True)
dispatcher = updater.dispatcher

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Merhaba! Bu bot ürün linklerini alıp kanala gönderecek. Ürün linkini atabilirsin."
    )

dispatcher.add_handler(CommandHandler("start", start))

def get_product_info(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.title.text.strip() if soup.title else "Ürün Başlığı Bulunamadı"
        price = None
        for tag in soup.find_all("span"):
            if "₺" in tag.text:
                price = tag.text.strip()
                break
        if not price:
            price = "Fiyat Bulunamadı"
        img = None
        for tag in soup.find_all("img"):
            if tag.get("src") and "product" in tag.get("src"):
                img = tag.get("src")
                break
        if not img:
            img = "https://via.placeholder.com/200x200.png?text=Resim+Bulunamadı"
        return title, price, img
    except:
        return "Ürün Bilgisi Alınamadı", "-", "https://via.placeholder.com/200x200.png?text=Hata"

def handle_link(update: Update, context: CallbackContext):
    url = update.message.text
    if "http" in url:
        title, price, img = get_product_info(url)
        keyboard = [
            [InlineKeyboardButton("Satın Al", url=url),
             InlineKeyboardButton("Google'de Ara", url=f"https://www.google.com/search?q={title}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_photo(
            chat_id=KANAL,
            photo=img,
            caption=f"{title}\nFiyat: {price}\n{url}",
            reply_markup=reply_markup
        )
        update.message.reply_text("Ürün kanala gönderildi!")
    else:
        update.message.reply_text("Lütfen geçerli bir ürün linki gönder.")

dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

updater.start_polling()
updater.idle()
