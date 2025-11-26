import os
import requests
from bs4 import BeautifulSoup
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
KANAL = os.environ["KANAL"]


def start(update, context):
    update.message.reply_text(
        "Merhaba! Ürün linkini gönder, ben de kanala fotoğraf + fiyat + butonlarla ileteyim."
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
            if src and ("product" in src or "media" in src or "image" in src):
                img = src
                break
        if not img:
            img = "https://via.placeholder.com/300?text=Resim+Bulunamadı"

        return title, price, img

    except:
        return "Ürün alınamadı", "-", "https://via.placeholder.com/300?text=Hata"


def handle_link(update, context):
    url = update.message.text

    if "http" not in url:
        update.message.reply_text("Geçerli bir ürün linki gönder.")
        return

    title, price, img = scrape_product(url)

    keyboard = [
        [
            InlineKeyboardButton("Satın Al", url=url),
            InlineKeyboardButton("Google'da Ara", url=f"https://www.google.com/search?q={title}")
        ]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_photo(
        chat_id=KANAL,
        photo=img,
        caption=f"{title}\nFiyat: {price}\n\n{url}",
        reply_markup=markup
    )

    update.message.reply_text("Ürün kanala gönderildi 👍")


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_link))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
