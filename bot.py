import requests
from bs4 import BeautifulSoup
import time

WEBHOOK = "https://discord.com/api/webhooks/1479095180953911469/UTGcnHjBtpOt-mErqPGlB-X0nQkbwzItuXOEr_C1LNtzq4UO_OqxGQBlbhGktRHUAIVR"

amazon_url = "https://www.amazon.co.jp/hz/wishlist/ls/2ZMD47F7CBZ29"
gipt_url = "https://gi-pt.com/main/wishlist/fan-view/3a1f1c99-440f-ad66-d107-1ed83a03c5cf"

seen = set()

headers = {
    "User-Agent": "Mozilla/5.0"
}

def send_discord(title, name, url, img):

    data = {
        "embeds": [
            {
                "title": title,
                "description": name,
                "url": url,
                "image": {
                    "url": img
                }
            }
        ]
    }

    requests.post(WEBHOOK, json=data)


def check_amazon():

    r = requests.get(amazon_url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    items = soup.select("img")

    for i in items:

        name = i.get("alt")
        img = i.get("src")

        if not name:
            continue

        # Amazon広告排除
        ng = [
            "Amazon",
            "Prime",
            "Mastercard",
            "スポンサー",
            "おすすめ",
            "広告",
            "Audible"
        ]

        if any(word in name for word in ng):
            continue

        if name not in seen:

            seen.add(name)

            send_discord(
                "🎁 Amazon Wishlist追加",
                name,
                amazon_url,
                img
            )


def check_gipt():

    r = requests.get(gipt_url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    items = soup.select("img")

    for i in items:

        name = i.get("alt")
        img = i.get("src")

        if not name:
            continue

        if name not in seen:

            seen.add(name)

            send_discord(
                "🎁 Gi-pt Wishlist追加",
                name,
                gipt_url,
                img
            )


while True:

    try:

        check_amazon()
        check_gipt()

    except Exception as e:
        print("error:", e)

    time.sleep(60)
