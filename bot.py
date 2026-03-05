import requests
import time
from bs4 import BeautifulSoup

# 設定
WEBHOOK = "https://discord.com/api/webhooks/1479095180953911469/UTGcnHjBtpOt-mErqPGlB-X0nQkbwzItuXOEr_C1LNtzq4UO_OqxGQBlbhGktRHUAIVR"
amazon_url = "https://www.amazon.co.jp/hz/wishlist/ls/2HA24VTBOPMGR?ref_=wl_fv_le"
gipt_url = "https://gi-pt.com/main/wishlist/fan-view/3a1f1c99-440f-ad66-d107-1ed83a03c5cf"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ja-JP,ja;q=0.9"
}

seen = set()

def send_discord(title, name, url, img):
    data = {
        "embeds": [
            {
                "title": title,
                "description": name,
                "url": url,
                "color": 15844367,
                "image": {"url": img} if img else {}
            }
        ]
    }
    try:
        r = requests.post(WEBHOOK, json=data, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print(f"Discord送信失敗: {e}")

def check_amazon():
    print("Amazonチェック中...")
    r = requests.get(amazon_url, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")
    
    # Amazonのリストアイテムを抽出（複数のセレクタで予備を持たせる）
    items = soup.select('li[id^="item_"], .g-item-sortable')
    
    for i in items:
        # 商品名を取得
        name_tag = i.select_one('a[id^="itemName_"]') or i.select_one('h2 a') or i.select_one('h3')
        if not name_tag: continue
        
        name = name_tag.get_text(strip=True)
        img_tag = i.find('img')
        img = img_tag.get('src') if img_tag else ""
        
        key = f"amazon-{name}"
        if key not in seen:
            print(f"新着(Amazon): {name}")
            seen.add(key)
            send_discord("🛒 Amazon Wishlist追加", name, amazon_url, img)

def check_gipt():
    print("GIPTチェック中...")
    r = requests.get(gipt_url, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")
    
    # GIPTの商品名（h5タグ）を取得
    items = soup.find_all("h5")
    
    for n in items:
        name = n.get_text(strip=True)
        if not name: continue
        
        # 周辺から画像を探す
        parent = n.find_parent("div")
        img_tag = parent.find("img") if parent else None
        img = img_tag.get("src") if img_tag else ""
        
        key = f"gipt-{name}"
        if key not in seen:
            print(f"新着(GIPT): {name}")
            seen.add(key)
            send_discord("🎁 Gi-pt Wishlist追加", name, gipt_url, img)

# --- メイン処理 ---
# 動作確認のため、あえて「起動時の既読処理」を外しています。
# 実行した瞬間にDiscordに通知が来れば成功です。

while True:
    try:
        check_amazon()
        check_gipt()
        print(f"待機中... ({time.strftime('%H:%M:%S')})")
    except Exception as e:
        print(f"エラー発生: {e}")
    
    # テスト時は短め（30秒など）にして、動くのが確認できたら300秒(5分)に戻してください
    time.sleep(60)
