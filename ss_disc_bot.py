import asyncio
import requests
from bs4 import BeautifulSoup
import discord
import os

TOKEN = "https://discord.com/api/webhooks/1363855070151573574/Sm94GfUkIEarztz9DfQ9mKTp0YiwFZV7vCRc3kl-GRUx8G6FeA9BCxEpp19PJ3fWgS7h"
CHANNEL_ID = '1363182020314005522' # замени на свой ID канала 1363182020314005522

CATEGORIES_FILE = 'categories.txt'

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

categories = set()
sent_ads = set()

def load_categories():
    if os.path.exists(CATEGORIES_FILE):
        with open(CATEGORIES_FILE, 'r', encoding='utf-8') as file:
            for line in file:
                link = line.strip()
                if link:
                    categories.add(link)

def save_categories():
    with open(CATEGORIES_FILE, 'w', encoding='utf-8') as file:
        for link in categories:
            file.write(link + '\n')

async def get_new_ads(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return ['https://www.ss.lv' + ad['href'] for ad in soup.find_all('a', class_='am')]

async def check_ads_loop():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    while not client.is_closed():
        for url in categories:
            try:
                ads = await get_new_ads(url)
                new_ads = [ad for ad in ads if ad not in sent_ads]
                for ad in new_ads:
                    await channel.send(f"🚗 Новое объявление: {ad}")
                    sent_ads.add(ad)
            except Exception as e:
                print(f"Ошибка при проверке {url}: {e}")
        await asyncio.sleep(60)

@client.event
async def on_ready():
    print(f'✅ Бот {client.user} запущен!')
    load_categories()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('/add '):
        link = message.content.split('/add ', 1)[1]
        if link not in categories:
            categories.add(link)
            save_categories()
            await message.channel.send(f"✅ Ссылка добавлена: {link}")
        else:
            await message.channel.send(f"⚠️ Ссылка уже есть в списке.")

    elif message.content.startswith('/remove '):
        link = message.content.split('/remove ', 1)[1]
        if link in categories:
            categories.remove(link)
            save_categories()
            await message.channel.send(f"🗑️ Ссылка удалена: {link}")
        else:
            await message.channel.send(f"❌ Такой ссылки нет в списке.")

    elif message.content.startswith('/list'):
        if categories:
            await message.channel.send("🗂️ Отслеживаемые категории:\n" + "\n".join(categories))
        else:
            await message.channel.send("📭 Список пуст.")

    elif message.content.startswith('/clear'):
        categories.clear()
        save_categories()
        await message.channel.send("🧹 Все категории очищены.")

    elif message.content.startswith('/help'):
        help_text = (
            "**📚 Список команд:**\n\n"
            "`/add [ссылка]` — добавить новую ссылку\n"
            "`/remove [ссылка]` — удалить ссылку\n"
            "`/list` — показать все ссылки\n"
            "`/clear` — очистить все ссылки\n"
            "`/help` — показать это сообщение\n"
        )
        await message.channel.send(help_text)

client.loop.create_task(check_ads_loop())
client.run(TOKEN)