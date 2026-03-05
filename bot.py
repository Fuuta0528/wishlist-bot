import requests
from bs4 import BeautifulSoup
import time

# ===== 設定 =====

AMAZON_URL = "https://www.amazon.co.jp/hz/wishlist/ls/2ZMD47F7CBZ29"
GIPT_URL = "https://gi-pt.com/main/wishlist/fan-view/3a1f1c99-440f-ad66-d107-1ed83a03c5cf"

WEBHOOK = "https://discord.com/api/webhooks/1479095180953911469/UTGcnHjBtpOt-mErqPGlB-X0nQkbwzItuXOEr_C1LNtzq4UO_OqxGQBlbhGktRHUAIVR"

headers = {"User-Agent": "Mozilla/5.0"}

seen_items = set()

# ======================
# Discord通知
# ======================

def send_discord(title, link, image):

    embed = {
        "title": "🎁 Wishlist追加",
        "description": f"[{title}]({link})",
        "color": 5763719
    }

    if image:
        embed["image"] = {"url": image}

    requests.post(WEBHOOK, json={"embeds": [embed]})


# ======================
# Amazon取得
# ======================

def check_amazon():

    results = []

    r = requests.get(AMAZON_URL, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    items = soup.select("div.g-item-sortable")

    for item in items:

        title_tag = item.select_one("h2")
        if not title_tag:
            continue

        title = title_tag.text.strip()

        if "プライム" in title:
            continue
        if "Mastercard" in title:
            continue

        link_tag = item.select_one("a")
        if not link_tag:
            continue

        link = "https://www.amazon.co.jp" + link_tag["href"]

        img_tag = item.select_one("img")
        image = img_tag.get("src") if img_tag else None

        results.append((title, link, image))

    return results


# ======================
# GIPT取得
# ======================

def check_gipt():

    results = []

    r = requests.get(GIPT_URL, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    links = soup.select("a")

    for a in links:

        title = a.text.strip()

        if len(title) < 8:
            continue

        link = a.get("href")
        if not link or not link.startswith("http"):
            continue

        results.append((title, link, None))

    return results


# ======================
# 監視ループ
# ======================

while True:

    print("チェック開始")

    try:

        amazon_items = check_amazon()
        gipt_items = check_gipt()

        all_items = amazon_items + gipt_items

        for title, link, image in all_items:

            uid = title + link

            if uid not in seen_items:

                seen_items.add(uid)
                print("新商品:", title)
                send_discord(title, link, image)

    except Exception as e:
        print("error:", e)

    time.sleep(120)
    print(check_amazon())
print(check_gipt())
