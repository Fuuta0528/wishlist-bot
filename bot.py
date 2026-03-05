import requests
import time
from bs4 import BeautifulSoup

WEBHOOK = "https://discord.com/api/webhooks/1479095180953911469/UTGcnHjBtpOt-mErqPGlB-X0nQkbwzItuXOEr_C1LNtzq4UO_OqxGQBlbhGktRHUAIVR"
AMAZON_URL = "https://www.amazon.co.jp/hz/wishlist/ls/2HA24VTBOPMGR"

seen = set()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def send_discord(name, img):
    data = {
        "embeds": [
            {
                "title": " 🎁なるる追加",
                "description": name,
                "url": AMAZON_URL,
                "color": 16750848,
                "image": {"url": img} if img else {}
            }
        ]
    }
    requests.post(WEBHOOK, json=data)

def check_amazon():
    print(f"チェック中... ({time.strftime('%H:%M:%S')})")
    try:
        r = requests.get(AMAZON_URL, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.find_all("img")

        for i in items:
            name = i.get("alt")
            img = i.get("src")

            if not name:
                continue

            # --- 【ここを強化！】除外したいキーワードを追加 ---
            ng_words = [
                "Amazon", "Prime", "Mastercard", "スポンサー", "広告", "Audible",
                "切り替え", "その他", "ビュー", "プロフィール", "ギフト設定",
                "保存済み", "削除", "シェア", "フィルター", "並べ替え"
            ]
            
            # もし名前の中にNGワードが1つでも入っていたら無視する
            if any(word in name for word in ng_words):
                continue
            
            # 文字数が極端に短いものもボタンの可能性が高いので無視（例：「次へ」など）
            if len(name) <= 3:
                continue

            if name not in seen:
                seen.add(name)
                print(f"【新着検知】: {name}")
                send_discord(name, img)

    except Exception as e:
        print(f"エラー: {e}")

print("Amazon監視スタート！")
while True:
    check_amazon()
    time.sleep(300) # 5分おき
