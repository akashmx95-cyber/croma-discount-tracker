import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import telegram
import time

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
MIN_DISCOUNT = 80

CATEGORY_URLS = [
    "https://www.croma.com/lp-deals-corner",
    "https://www.croma.com/lp-bargain-corner"
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def calculate_discount(orig, curr):
    try:
        o = float(str(orig).replace('₹','').replace(',','').strip() or 0)
        c = float(str(curr).replace('₹','').replace(',','').strip() or 0)
        return round(((o - c) / o) * 100, 1) if o > c else 0
    except:
        return 0

def main():
    print(f"[{datetime.now()}] Starting Croma Tracker...")
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    seen = {}
    
    if os.path.exists('seen.json'):
        with open('seen.json') as f:
            seen = json.load(f)

    total_found = 0

    for url in CATEGORY_URLS:
        print(f"Scraping: {url}")
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            print(f"Status Code: {resp.status_code}")
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            cards = soup.find_all(['div', 'article'], class_=lambda x: x and any(word in str(x).lower() for word in ['product', 'item', 'card', 'offer']))
            
            print(f"Found {len(cards)} potential product cards")
            
            for card in cards[:30]:
                try:
                    name_tag = card.find(['h2', 'h3', 'a', 'p'])
                    name_text = name_tag.get_text(strip=True) if name_tag else "No Name"
                    
                    prices = card.find_all(['span', 'div', 'p'], class_=lambda x: x and 'price' in str(x).lower())
                    
                    curr_price = prices[0].get_text(strip=True) if prices else ""
                    orig_price = prices[1].get_text(strip=True) if len(prices) > 1 else curr_price
                    
                    discount = calculate_discount(orig_price, curr_price)
                    
                    if discount >= MIN_DISCOUNT:
                        print(f"✅ High discount found: {discount}% - {name_text[:60]}")
                        msg = f"🔥 **{discount}% OFF on Croma** 🔥\n\n{name_text[:100]}\n💰 {curr_price}\nLink: {url}"
                        bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')
                        time.sleep(3)
                        total_found += 1
                except:
                    continue
                    
        except Exception as e:
            print(f"Error: {e}")

    print(f"Finished. Found {total_found} high discount products.")

if __name__ == "__main__":
    main()
