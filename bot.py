import requests
import time
from bs4 import BeautifulSoup

# --- 設定（ここだけ確認してください） ---
WEBHOOK = "https://discord.com/api/webhooks/1479095180953911469/UTGcnHjBtpOt-mErqPGlB-X0nQkbwzItuXOEr_C1LNtzq4UO_OqxGQBlbhGktRHUAIVR"
AMAZON_URL = "https://www.amazon.co.jp/hz/wishlist/ls/2HA24VTBOPMGR"

# 既読リスト（重複通知を防ぐ）
seen = set()

# ブラウザのふりをする設定
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def send_discord(name, img):
    data = {
        "embeds": [
            {
                "title": "🛒 Amazon Wishlist追加",
                "description": name,
                "url": AMAZON_URL,
                "color": 16750848, # オレンジ色
                "image": {"url": img} if img else {}
            }
        ]
    }
    try:
        requests.post(WEBHOOK, json=data, timeout=10)
    except Exception as e:
        print(f"Discord送信エラー: {e}")

def check_amazon():
    print(f"チェック中... ({time.strftime('%H:%M:%S')})")
    try:
        r = requests.get(AMAZON_URL, headers=headers, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # ページ内の画像(img)をすべて探す
        items = soup.find_all("img")

        for i in items:
            name = i.get("alt") # 画像の説明文（商品名）を取得
            img = i.get("src")   # 画像のURLを取得

            if not name:
                continue

            # 不要な広告やロゴを除外
            ng_words = ["Amazon", "Prime", "Mastercard", "スポンサー", "おすすめ", "広告", "Audible"]
            if any(word in name for word in ng_words):
                continue

            # まだ通知していない商品ならDiscordに送る
            if name not in seen:
                seen.add(name)
                print(f"【新着】{name}")
                send_discord(name, img)

    except Exception as e:
        print(f"エラー発生: {e}")

# --- メイン処理 ---
print("Amazon監視スタート！")
# 初回起動時に「今ある商品」を既読にしたい場合は、下の行の # を消してください
# check_amazon() 

while True:
    check_amazon()
    time.sleep(300) # 5分おきにチェック
