import requests
from bs4 import BeautifulSoup
import time

# ===== 設定 =====
AMAZON_URL = "https://www.amazon.co.jp/hz/wishlist/ls/2HA24VTBOPMGR"
GIPT_URL = "https://gi-pt.com/main/wishlist/fan-view/3a1f1c99-440f-ad66-d107-1ed83a03c5cf"

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1479095180953911469/UTGcnHjBtpOt-mErqPGlB-X0nQkbwzItuXOEr_C1LNtzq4UO_OqxGQBlbhGktRHUAIVR"

CHECK_INTERVAL = 300  # 5分

headers = {
    "User-Agent": "Mozilla/5.0"
}

seen_items = set()


# ======================
# Discord通知
# ======================

def send_discord(title, link):

    data = {
        "content": f"🎁 **Wishlist追加**\n{title}\n{link}"
    }

    requests.post(DISCORD_WEBHOOK, json=data)


# ======================
# Amazonチェック
# ======================

def check_amazon():

    try:

        r = requests.get(AMAZON_URL, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")

        items = soup.select("div.g-item-sortable")

        results = []

        for item in items:

            title_tag = item.select_one("h2 a")

            if not title_tag:
                continue

            title = title_tag.text.strip()

            # 不要通知除外
            if "プライム会員" in title:
                continue

            if "Amazon Mastercard" in title:
                continue

            link = "https://www.amazon.co.jp" + title_tag["href"]

            results.append((title, link))

        return results

    except Exception as e:
        print("Amazon error:", e)
        return []


# ======================
# GIPTチェック
# ======================

def check_gipt():

    try:

        r = requests.get(GIPT_URL, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")

        items = soup.select("a")

        results = []

        for item in items:

            title = item.text.strip()

            if len(title) < 8:
                continue

            link = item.get("href")

            if not link:
                continue

            if "http" not in link:
                continue

            results.append((title, link))

        return results

    except Exception as e:
        print("GIPT error:", e)
        return []


# ======================
# メイン監視
# ======================

while True:

    print("チェック開始")

    amazon_items = check_amazon()
    gipt_items = check_gipt()

    all_items = amazon_items + gipt_items

    for title, link in all_items:

        uid = title + link

        if uid not in seen_items:

            seen_items.add(uid)

            print("新規:", title)

            send_discord(title, link)

    time.sleep(CHECK_INTERVAL)
