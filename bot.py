import requests
from bs4 import BeautifulSoup
import time

# Discord Webhook URL
WEBHOOK = "https://discord.com/api/webhooks/1479095180953911469/UTGcnHjBtpOt-mErqPGlB-X0nQkbwzItuXOEr_C1LNtzq4UO_OqxGQBlbhGktRHUAIVR"

# 監視するURL
URLS = [
    "https://www.amazon.co.jp/hz/wishlist/ls/2HA24VTBOPMGR",
    "https://gi-pt.com/main/wishlist/fan-view/3a1f1c99-440f-ad66-d107-1ed83a03c5cf"
]

seen = set()

def send(msg):
    requests.post(WEBHOOK, json={"content": msg})

def check():
    global seen

    for url in URLS:
        r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(r.text,"html.parser")

        items = soup.find_all("img")

        for i in items:
            name = i.get("alt")

            if name and name not in seen:
                seen.add(name)

                msg = f"🎁 Wishlistに追加！\n{name}\n{url}"
                send(msg)

while True:
    check()
    time.sleep(60)
