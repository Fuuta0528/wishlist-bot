import requests
import time
from bs4 import BeautifulSoup

WEBHOOK = "https://discord.com/api/webhooks/1479095180953911469/UTGcnHjBtpOt-mErqPGlB-X0nQkbwzItuXOEr_C1LNtzq4UO_OqxGQBlbhGktRHUAIVR"

# AmazonのURL
amazon_url = "https://www.amazon.co.jp/hz/wishlist/ls/2HA24VTBOPMGR?ref_=wl_fv_le"

# 【修正点1】GIPTのURLを「ファン公開用」に変更しました
gipt_url = "https://gi-pt.com/main/wishlist/fan-view/3a1f1c99-440f-ad66-d107-1ed83a03c5cf"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 既読リスト
seen = set()

def send_discord(title, name, url, img):
    data = {
        "embeds": [
            {
                "title": title,
                "description": name,
                "url": url,
                "image": {"url": img} if img else {}
            }
        ]
    }
    # タイムアウトを設定してプログラムが止まらないようにする
    try:
        requests.post(WEBHOOK, json=data, timeout=10)
    except Exception as e:
        print("Discord送信エラー:", e)

def check_amazon():
    r = requests.get(amazon_url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    items = soup.select(".g-item-sortable")

    for i in items:
        # Amazonの商品名取得をより確実に
        name_tag = i.select_one("h2 a") or i.select_one("h3 a") or i.select_one("[id^='itemName']")
        img_tag = i.select_one("img")

        if not name_tag:
            continue

        name = name_tag.text.strip()
        img = img_tag.get("src") if img_tag else ""
        
        # 名前をキーにする（画像URLは変わることがあるため）
        key = f"amazon-{name}"

        if key not in seen:
            seen.add(key)
            send_discord("🛒 Amazon Wishlist追加", name, amazon_url, img)

def check_gipt():
    r = requests.get(gipt_url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    # 【修正点2】GIPTのカード要素（h5タグ）をベースに取得するように変更
    # GIPTは画像に特定のキーワードが入らないため、構造から取得します
    items = soup.find_all("h5") # 商品名はh5タグに入っています

    for n in items:
        name = n.text.strip()
        if not name:
            continue
            
        # その商品の画像を探す
        # h5タグの親要素からimgタグを探す
        parent = n.find_parent("div", class_="card") or n.parent
        img_tag = parent.find("img") if parent else None
        img = img_tag.get("src") if img_tag else ""

        key = f"gipt-{name}"

        if key not in seen:
            seen.add(key)
            send_discord("🎁 Gi-pt Wishlist追加", name, gipt_url, img)

# 初回実行：起動時に今のリストを「既読」にする
# (これがないと、起動した瞬間に今ある商品が全部通知されます)
print("初期リストを取得中...")
check_amazon()
check_gipt()
print("監視を開始しました。")

while True:
    try:
        check_amazon()
        check_gipt()
        print(f"チェック完了: {time.strftime('%H:%M:%S')}")
    except Exception as e:
        print("error:", e)

    # 1分だと短すぎてサイトに拒否される可能性があるため、5分(300)推奨
    time.sleep(300)
