import requests
from bs4 import BeautifulSoup
import time

WEBHOOK = "https://discord.com/api/webhooks/1479095180953911469/UTGcnHjBtpOt-mErqPGlB-X0nQkbwzItuXOEr_C1LNtzq4UO_OqxGQBlbhGktRHUAIVR"

amazon_url = "https://www.amazon.co.jp/hz/wishlist/ls/2HA24VTBOPMGR"
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
    # ブラウザが裏でデータを取ってきている「本当のデータ置き場」を叩きます
    # URL末尾のID部分はあなたの指定したものに固定しています
    api_url = "https://gi-pt.com/api/v1/wishlist/fan-view/3a1f1c99-440f-ad66-d107-1ed83a03c5cf"
    
    try:
        # データを取得（GIPTのサーバーから直接JSONという形式でデータをもらいます）
        r = requests.get(api_url, headers=headers, timeout=15)
        data = r.json() # HTMLではなく「データの塊」として読み込む

        # 商品リスト（wishlist_items）の中身をループで回す
        # GIPTのデータ構造: data['data']['wishlist_items']
        items = data.get('data', {}).get('wishlist_items', [])

        for item in items:
            # 商品名を取得
            name = item.get('product_name') or item.get('name')
            if not name:
                continue

            # 画像URLを取得
            img = item.get('image_url') or ""
            
            # 商品の個別IDや名前をキーにして重複チェック
            key = f"gipt-{name}"

            if key not in seen:
                seen.add(key)
                send_discord(
                    "🎁 Gi-pt Wishlist追加",
                    name,
                    gipt_url, # 通知用URLは元のページURL
                    img
                )
    except Exception as e:
        print(f"GIPTチェック中にエラー: {e}")

while True:

    try:

        check_amazon()
        check_gipt()

    except Exception as e:
        print("error:", e)

    time.sleep(60)
