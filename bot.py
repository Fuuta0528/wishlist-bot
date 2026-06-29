import requests
import time
from bs4 import BeautifulSoup
import os
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer

# ==================== Render用：タイムアウト防止のダミー窓口 ====================
def run_dummy_server():
    # Renderが指定するポート（窓口の番号）を取得（なければ10000番）
    port = int(os.environ.get("PORT", 10000))
    server_address = ("", port)
    # 接続が来たら200 OKを返すだけの超簡単なサーバー
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"🤖 Render用の窓口をポート {port} で開けました。タイムアウトを防ぎます。")
    httpd.serve_forever()

# ==================== メインのボット処理 ====================

# DiscordのWebhook URL
WEBHOOK = "https://discord.com/api/webhooks/1479095180953911469/UTGcnHjBtpOt-mErqPGlB-X0nQkbwzItuXOEr_C1LNtzq4UO_OqxGQBlbhGktRHUAIVR"

# 監視対象のURL（Amazon ＆ gipt）
amazon_url = "https://www.amazon.co.jp/hz/wishlist/ls/2HA24VTBOPMGR?ref_=wl_fv_le"
gipt_url = "https://gi-pt.com/main/wishlist/fan-view/3a1f1c99-440f-ad66-d107-1ed83a03c5cf"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 既読の画像URLを保存するセット
seen = set()

def send_discord(title, name, url, img):
    """DiscordにEmbed（埋め込み）形式で通知を送る共通関数"""
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
    try:
        requests.post(WEBHOOK, json=data, timeout=10)
    except Exception as e:
        print("Discord送信エラー:", e)

def check_amazon(is_first=False):
    """Amazonのウィッシュリストをチェックする関数"""
    try:
        r = requests.get(amazon_url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.select(".g-item-sortable")

        for i in items:
            name_tag = i.select_one("h2")
            img_tag = i.select_one("img")
            if not img_tag:
                continue

            img = img_tag.get("src")
            name = name_tag.text.strip() if name_tag else "Amazon Wishlist商品"

            if img not in seen:
                seen.add(img)
                # 初回起動時は通知を飛ばさず、2回目以降の「新商品」だけ通知する
                if not is_first:
                    send_discord("🎁なるるwishlist (Amazon)", name, amazon_url, img)
    except Exception as e:
        print("Amazonチェック中にエラーが発生しました:", e)

def check_gipt(is_first=False):
    """giptのウィッシュリストをチェックする関数"""
    try:
        r = requests.get(gipt_url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        
        # gipt内のすべての画像を取得
        img_tags = soup.find_all("img")

        for tag in img_tags:
            img = tag.get("src")
            if not img:
                continue
            
            # 相対パス（/main/...など）を絶対パスに自動修正
            if img.startswith("/"):
                img = "https://gi-pt.com" + img
            
            # ロゴやアイコンなど、商品ではない固定画像を除外（ノイズ対策）
            if any(keyword in img.lower() for keyword in ["logo", "icon", "avatar", "banner", "pwa", "asset"]):
                continue

            if img not in seen:
                seen.add(img)
                # 初回起動時は通知を飛ばさず、2回目以降の「新商品」だけ通知する
                if not is_first:
                    send_discord(
                        "🎁大好きな配信者のgipt",
                        "ウィッシュリストに新しい商品（画像）が追加されたよ！",
                        gipt_url,
                        img
                    )
    except Exception as e:
        print("giptチェック中にエラーが発生しました:", e)

# ==================== メイン処理 ====================
if __name__ == "__main__":
    # 1. 最初に裏側でRender用のダミーサーバーを起動（これでFailedを防ぐわ！）
    threading.Thread(target=run_dummy_server, daemon=True).start()

    print("==========================================")
    print("   Amazon ＆ gipt 同時監視ボット 起動完了   ")
    print("==========================================")
    print("現在、初回のデータ（現在のリスト状態）を読み込んでいます...")
    
    # 起動した瞬間に、今ある商品をすべて既読に登録（一斉通知を防ぐ）
    check_amazon(is_first=True)
    check_gipt(is_first=True)
    
    print(f"初期データの取得が完了しました（総既読画像数: {len(seen)}件）。")
    print("これ以降に新しく追加された商品だけを1分ごとに検知して通知します。")
    print("------------------------------------------")

    while True:
        try:
            # 1分ごとに交互にチェックを実行
            check_amazon(is_first=False)
            check_gipt(is_first=False)
        except Exception as e:
            print("ループ内で予期せぬエラー:", e)
        
        # 60秒（1分）待機
        time.sleep(60)
