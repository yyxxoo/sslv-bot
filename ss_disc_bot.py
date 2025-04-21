import asyncio
import requests
from datetime import datetime
from bs4 import BeautifulSoup

DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1363855070151573574/Sm94GfUkIEarztz9DfQ9mKTp0YiwFZV7vCRc3kl-GRUx8G6FeA9BCxEpp19PJ3fWgS7h'

# Список ссылок на категории
urls = [
    'https://www.ss.lv/ru/real-estate/premises/garages/bauska-and-reg/',
    'https://www.ss.lv/ru/transport/cars/audi/',
    'https://www.ss.lv/ru/transport/cars/bmw/'
]

sent_ads = set()

async def get_new_ads():
    all_ads = []
    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        ads = ['https://www.ss.lv' + ad['href'] for ad in soup.find_all('a', class_='am')]
        all_ads.extend(ads)
    return all_ads

async def send_discord_message(content):
    data = {
        "content": content
    }
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if response.status_code != 204:
        print(f"Ошибка отправки в Discord: {response.status_code}, {response.text}")

async def check_new_ads():
    ads = await get_new_ads()
    new_ads = [ad for ad in ads if ad not in sent_ads]

    for ad in new_ads:
        now = datetime.now()
        date = now.strftime('%d.%m.%Y')
        time = now.strftime('%H:%M')
        message = (
            f"🚗 **Новое объявление!**\n\n"
            f"📅 **Дата:** {date} {time} \n\n"
            f"🔗 Ссылка на объявление: {ad}\n\n"
        )
        await send_discord_message(message)
        sent_ads.add(ad)

async def main():
    await send_discord_message("🔔 Бот запущен! Начинаю мониторинг на ss.lv")

    while True:
        await check_new_ads()
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
