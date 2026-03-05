import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

WEBHOOK = "https://discord.com/api/webhooks/1479095180953911469/UTGcnHjBtpOt-mErqPGlB-X0nQkbwzItuXOEr_C1LNtzq4UO_OqxGQBlbhGktRHUAIVR"
amazon_url = "https://www.amazon.co.jp/hz/wishlist/ls/2HA24VTBOPMGR"
gipt_url = "https://gi-pt.com/main/wishlist/fan-view/3a1f1c99-440f-ad66-d107-1ed83a03c5cf"

seen = set()
headers = {"User-Agent": "Mozilla/5.0"}

def send_discord(title, name, url, img):
    data = {
        "embeds": [{"title": title, "description": name, "url": url, "image": {"url": img}}]
    }
    requests.post(WEBHOOK, json=data)

def check_amazon():
    # Amazonは今の「動いているやり方」を維持
    r = requests.get(amazon_url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    items = soup.select("img")
    for i in items:
        name = i.get("alt")
        img = i.get("src")
        if not name: continue
        ng = ["Amazon", "Prime", "Mastercard", "スポンサー", "おすすめ", "広告", "Audible"]
        if any(word in name for word in ng): continue
        if name not in seen:
            seen.add(name)
            send_discord("🎁 Amazon Wishlist追加", name, amazon_url, img)

def check_gipt():
    # GIPTだけ「ブラウザ」を使って、読み込みを待つ
    options = Options()
    options.add_argument('--headless') # 画面を表示しない
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get(gipt_url)
        time.sleep(7) # 商品が出るまで長めに待つ（ここがキモ！）
        
        soup = BeautifulSoup(driver.page_source, "html.parser")
        # GIPTの構造に合わせて「h5タグ（商品名）」を探す
        items = soup.find_all("h5")
        
        for n in items:
            name = n.get_text(strip=True)
            if not name or name in seen:
                continue
            
            # 画像を取得（h5の近くのimgを探す）
            parent = n.find_parent("div")
            img_tag = parent.find("img") if parent else None
            img = img_tag.get("src") if img_tag else ""
            
            seen.add(name)
            send_discord("🎁 Gi-pt Wishlist追加", name, gipt_url, img)
            print(f"GIPT検知: {name}")
    finally:
        driver.quit() # ブラウザを閉じる

# 監視ループ
while True:
    try:
        check_amazon() # 爆速
        check_gipt()   # ブラウザでじっくり
    except Exception as e:
        print("error:", e)
    time.sleep(60)
