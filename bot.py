import os
import requests
from bs4 import BeautifulSoup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
KANAL = os.environ["KANAL"]


async def start(update, context):
    await update.message.reply_text(
        "Merhaba! Ürün linkini gönder, ben de kanala foto + fiyat + butonlarla göndereyim."
    )


def scrape(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        title = soup.title.text.strip() if soup.title else "Başlık bulunamadı"

        price = None
        for span in soup.find_all("span"):
            if "₺" in span.text:
                price = span.text.strip()
                break
        if not price:
            price = "Fiyat bulunamadı"

        img = None
        for img_tag in soup.find_all("img"):
            src = img_tag.get("src")
            if src and ("product" in src or "media" in src or "image" in src):
                img = src
                break

        if not img:
            img = "https://via.placeholder.com/300?text=Resim+Yok"

        return title, price, img
    except:
        return "Ürün Alınamadı", "-", "https://via.placeholder.com/300?text=Hata"


async def handle_link(update, context):
    text = update.message.text

    if "http" not in text:
        await update.message.reply_text("Geçerli bir ürün linki gönder.")
        return

    title, price, img = scrape(text)

    buttons = [
        [
            InlineKeyboardButton("Satın Al", url=text),
            InlineKeyboardButton("Google'da Ara", url=f"https://www.google.com/search?q={title}")
        ]
    ]

    markup = InlineKeyboardMarkup(buttons)

    await context.bot.send_photo(
        chat_id=KANAL,
        photo=img,
        caption=f"{title}\nFiyat: {price}\n\n{text}",
        reply_markup=markup
    )

    await update.message.reply_text("Ürün kanala gönderildi 👍")


async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    await app.run_polling()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
