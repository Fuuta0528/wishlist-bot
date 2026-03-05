import requests
import time
from bs4 import BeautifulSoup

WEBHOOK = "https://discord.com/api/webhooks/1479095180953911469/UTGcnHjBtpOt-mErqPGlB-X0nQkbwzItuXOEr_C1LNtzq4UO_OqxGQBlbhGktRHUAIVR"

amazon_url = "https://www.amazon.co.jp/hz/wishlist/ls/2HA24VTBOPMGR?ref_=wl_fv_le"

headers = {
    "User-Agent": "Mozilla/5.0"
}

seen = set()

def send_discord(title, name, url, img):

    data = {
        "embeds": [
            {
                "title": title,
                "description": name,
                "url": url,
                "image": {"url": img}
            }
        ]
    }

    requests.post(WEBHOOK, json=data)


def check_amazon():

    r = requests.get(amazon_url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    items = soup.select(".g-item-sortable")

    for i in items:

        name_tag = i.select_one("h2")
        img_tag = i.select_one("img")

        if not img_tag:
            continue

        img = img_tag.get("src")
        name = name_tag.text.strip() if name_tag else "Amazon Wishlist商品"

        key = img

        if key not in seen:

            seen.add(key)

            send_discord(
                "🎁なるるwishlist",
                name,
                amazon_url,
                img
            )


while True:

    try:

        check_amazon()
        check_gipt()

    except Exception as e:
        print("error:", e)

    time.sleep(60)
