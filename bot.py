import os
import requests
from bs4 import BeautifulSoup
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Environment değişkenleri
TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
KANAL = os.environ['KANAL']

# Bot uygulaması
app = ApplicationBuilder().token(TOKEN).build()


# /start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Merhaba! Ürün linkini bana gönder. Ürün fotoğrafı, fiyatı ve butonlarıyla beraber kanalına göndereceğim."
    )


# Ürün bilgilerini çekme fonksiyonu
def get_product_info(url):
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        # Başlık
        title = soup.title.text.strip() if soup.title else "Ürün Başlığı Bulunamadı"

        # Fiyat
        price = None
        for tag in soup.find_all("span"):
            if "₺" in tag.text:
                price = tag.text.strip()
                break
        if not price:
            price = "Fiyat Bulunamadı"

        # Resim
        img = None
        for tag in soup.find_all("img"):
            src = tag.get("src")
            if src and ("product" in src or "media" in src):
                img = src
                break

        if not img:
            img = "https://via.placeholder.com/300x300.png?text=Resim+Bulunamadı"

        return title, price, img

    except Exception:
        return "Ürün Bilgisi Alınamadı", "-", "https://via.placeholder.com/300x300.png?text=Hata"


# Link mesajlarını yakalayıp kanala gönderme
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    if "http" not in url:
        await update.message.reply_text("Lütfen bir ürün linki gönder.")
        return

    # Ürün bilgilerini al
    title, price, img = get_product_info(url)

    # Butonlar
    keyboard = [
        [
            InlineKeyboardButton("Satın Al", url=url),
            InlineKeyboardButton("Google'de Ara", url=f"https://www.google.com/search?q={title}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Kanala gönder
    await context.bot.send_photo(
        chat_id=KANAL,
        photo=img,
        caption=f"{title}\nFiyat: {price}\n\n{url}",
        reply_markup=reply_markup
    )

    await update.message.reply_text("Ürün kanala gönderildi!")


# Handler kayıtları
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))


# Bot çalıştır
if __name__ == "__main__":
    app.run_polling()
