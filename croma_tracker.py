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
    try:
        print(f"[{datetime.now()}] Starting Croma Tracker...")
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        print("Telegram Bot initialized")
        
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
                print("HTML parsed successfully")
                
                cards = soup.find_all(['div', 'article'], class_=lambda x: x and any(word in str(x).lower() for word in ['product', 'item', 'card', 'offer']))
                print(f"Found {len(cards)} potential product cards")
                
                # ... rest of the loop remains same
                
            except Exception as e:
                print(f"Error scraping {url}: {e}")
                
        print(f"Finished. Found {total_found} high discount products.")
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
