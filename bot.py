import requests
from bs4 import BeautifulSoup
import time

WEBHOOK = "ここはそのまま君のWebhook"

amazon_url = "https://www.amazon.co.jp/hz/wishlist/ls/2HA24VTBOPMGR?ref_=wl_fv_le"
gipt_url = "https://gi-pt.com/main/wishlist/fan-view/3a1f1c99-440f-ad66-d107-1ed83a03c5cf"

headers = {
    "User-Agent": "Mozilla/5.0"
}

seen = set()


def send(title, name, url, img):

    data = {
        "embeds":[
            {
                "title": title,
                "description": name,
                "url": url,
                "image":{"url": img}
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

        ng = ["Amazon","広告","Prime","Audible","Mastercard"]

        if any(x in name for x in ng):
            continue

        key = "amazon"+name

        if key not in seen:

            seen.add(key)

            send(
                "🎁 Amazon Wishlist追加",
                name,
                amazon_url,
                img
            )


def check_gipt():

    r = requests.get(gipt_url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    cards = soup.select("div")

    for c in cards:

        img_tag = c.find("img")

        if not img_tag:
            continue

        img = img_tag.get("src")

        if not img:
            continue

        if "gipt" not in img:
            continue

        name = img_tag.get("alt")

        if not name:
            name = "Gi-pt商品"

        key = "gipt"+img

        if key not in seen:

            seen.add(key)

            send(
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

        print(e)

    time.sleep(60)
