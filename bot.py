import os
import requests
from bs4 import BeautifulSoup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
KANAL = os.environ["KANAL"]


async def start(update, context):
    await update.message.reply_text(
        "Merhaba! Ürün linkini gönder, ben de kanala fotoğraf + fiyat + butonlarla göndereyim."
    )


def scrape_product(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        title = soup.title.text.strip() if soup.title else "Başlık bulunamadı"

        price = None
        for tag in soup.find_all("span"):
            if "₺" in tag.text:
                price = tag.text.strip()
                break
        if not price:
            price = "Fiyat bulunamadı"

        img = None
        for tag in soup.find_all("img"):
            src = tag.get("src")
            if src and ("product" in src or "media" in src):
                img = src
                break
        if not img:
            img = "https://via.placeholder.com/300?text=Resim+Bulunamadı"

        return title, price, img

    except Exception:
        return "Ürün alınamadı", "-", "https://via.placeholder.com/300?text=Hata"


async def handle_link(update, context):
    url = update.message.text

    if "http" not in url:
        await update.message.reply_text("Geçerli bir link gönder.")
        return

    title, price, img = scrape_product(url)

    keyboard = [
        [
            InlineKeyboardButton("Satın Al", url=url),
            InlineKeyboardButton("Google’da Ara", url=f"https://www.google.com/search?q={title}")
        ]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_photo(
        chat_id=KANAL,
        photo=img,
        caption=f"{title}\nFiyat: {price}\n\n{url}",
        reply_markup=markup
    )

    await update.message.reply_text("Kanalına gönderildi 👍")


def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.run_polling()


if __name__ == "__main__":
    main()
