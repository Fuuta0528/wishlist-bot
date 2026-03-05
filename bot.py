import requests
from bs4 import BeautifulSoup
import time

# Discord Webhook URL
WEBHOOK = "https://discord.com/api/webhooks/1479095180953911469/UTGcnHjBtpOt-mErqPGlB-X0nQkbwzItuXOEr_C1LNtzq4UO_OqxGQBlbhGktRHUAIVR"

# 監視するURL
amazon_url = "https://www.amazon.co.jp/hz/wishlist/ls/2HA24VTBOPMGR"
gipt_url = "https://gi-pt.com/main/wishlist/fan-view/3a1f1c99-440f-ad66-d107-1ed83a03c5cf"

seen = set()

def send(msg):
    requests.post(WEBHOOK, json={"content": msg})

def check_amazon():
    r = requests.get(amazon_url, headers={"User-Agent":"Mozilla/5.0"})
    soup = BeautifulSoup(r.text,"html.parser")

    items = soup.select("img")

    for i in items:
        name = i.get("alt")
        img = i.get("src")

        if name and name not in seen and "Amazon" not in name:
            seen.add(name)

            msg = f"🎁 Amazon Wishlist追加！\n{name}\n{amazon_url}\n{img}"
            send(msg)

def check_gipt():
    r = requests.get(gipt_url, headers={"User-Agent":"Mozilla/5.0"})
    soup = BeautifulSoup(r.text,"html.parser")

    items = soup.select("img")

    for i in items:
        name = i.get("alt")
        img = i.get("src")

        if name and name not in seen:
            seen.add(name)

            msg = f"🎁 Gi-pt Wishlist追加！\n{name}\n{gipt_url}\n{img}"
            send(msg)

while True:
    check_amazon()
    check_gipt()
    time.sleep(60)
