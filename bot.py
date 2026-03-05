import requests
from bs4 import BeautifulSoup
import time

# Discord Webhook URL
WEBHOOK = "https://discord.com/api/webhooks/1479095180953911469/UTGcnHjBtpOt-mErqPGlB-X0nQkbwzItuXOEr_C1LNtzq4UO_OqxGQBlbhGktRHUAIVR"

# 監視するURL
URLS = [
    "https://www.amazon.co.jp/hz/wishlist/ls/2HA24VTBOPMGR?ref_=wl_fv_le",
    "https://gi-pt.com/main/wishlist/fan-view/3a1f1c99-440f-ad66-d107-1ed83a03c5cf"
]

old_items = set()

def send_discord(msg):
    requests.post(WEBHOOK, json={"content": msg})

def get_items(url):
    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")

        items = []
        for a in soup.find_all("a"):
            text = a.text.strip()
            if len(text) > 10:
                items.append(text)

        return set(items)

    except:
        return set()

while True:

    new_items = set()

    for url in URLS:
        new_items |= get_items(url)

    diff = new_items - old_items

    if diff:
        send_discord("🎁 Wishlist更新！")
        for item in diff:
            send_discord(item)

    old_items = new_items

    time.sleep(300)
