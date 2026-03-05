import requests
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

WEBHOOK = "https://discord.com/api/webhooks/1479095180953911469/UTGcnHjBtpOt-mErqPGlB-X0nQkbwzItuXOEr_C1LNtzq4UO_OqxGQBlbhGktRHUAIVR"

AMAZON_URL = "https://www.amazon.co.jp/hz/wishlist/ls/2HA24VTBOPMGR?ref_=wl_fv_le"
GIPT_URL = "https://gi-pt.com/main/wishlist/fan-view/3a1f1c99-440f-ad66-d107-1ed83a03c5cf"

known_items = set()


def send_discord(title, url, image):

    data = {
        "embeds": [
            {
                "title": title,
                "url": url,
                "image": {"url": image}
            }
        ]
    }

    requests.post(WEBHOOK, json=data)


def check_amazon():

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(AMAZON_URL, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    items = soup.select("img")

    for i in items:

        title = i.get("alt")
        image = i.get("src")

        if not title or not image:
            continue

        # Amazon商品画像だけ通す
        if "images-na.ssl-images-amazon.com" not in image:
            continue

        # 広告除外
        if "Amazon" in title or "プライム" in title or "読み放題" in title:
            continue

        if title not in known_items:

            known_items.add(title)

            print("Amazon追加:", title)

            send_discord(
                f"🎁 Amazon Wishlist追加\n{title}",
                AMAZON_URL,
                image
            )


def check_gipt():

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    driver.get(GIPT_URL)

    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    items = soup.select("img")

    for i in items:

        image = i.get("src")

        if not image:
            continue

        # Gi-ptの商品画像だけ
        if "product" not in image:
            continue

        title = image.split("/")[-1]

        if title not in known_items:

            known_items.add(title)

            print("Gi-pt追加:", title)

            send_discord(
                f"🎁 Gi-pt Wishlist追加",
                GIPT_URL,
                image
            )

    driver.quit()


print("BOT起動")

while True:

    try:

        check_amazon()
        check_gipt()

    except Exception as e:

        print("エラー:", e)

    time.sleep(60)
