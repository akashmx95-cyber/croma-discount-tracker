import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import telegram

# ================= CONFIG =================
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
PINCODE = '110053'
MIN_DISCOUNT = 80

CATEGORY_URLS = [
    "https://www.croma.com/mobile-phones/c/1",
    "https://www.croma.com/laptops/c/3",
    "https://www.croma.com/televisions/c/4",
    "https://www.croma.com/audio-video/c/292",
    "https://www.croma.com/home-appliances/c/5",
    "https://www.croma.com/lp-deals-corner"
]

HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; DiscountTracker/1.0)'}

def calculate_discount(orig, curr):
    try:
        o = float(str(orig).replace('₹','').replace(',','').strip())
        c = float(str(curr).replace('₹','').replace(',','').strip())
        return round(((o - c) / o) * 100, 1) if o > c else 0
    except:
        return 0

def main():
    seen_file = 'seen.json'
    seen = {}
    if os.path.exists(seen_file):
        with open(seen_file) as f:
            seen = json.load(f)

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    notifications = []

    for url in CATEGORY_URLS:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            cards = soup.find_all('div', class_=lambda x: x and 'product' in str(x).lower())
            
            for card in cards[:25]:
                try:
                    name_tag = card.find(['h2', 'h3', 'a'])
                    name = name_tag.get_text(strip=True) if name_tag else None
                    if not name: continue
                    
                    price_tag = card.find(class_=lambda x: x and 'price' in str(x).lower())
                    curr_price = price_tag.get_text(strip=True) if price_tag else ''
                    
                    orig_tag = card.find(class_=lambda x: x and ('mrp' in str(x).lower() or 'strike' in str(x).lower()))
                    orig_price = orig_tag.get_text(strip=True) if orig_tag else curr_price
                    
                    link = url
                    
                    discount = calculate_discount(orig_price, curr_price)
                    
                    if discount >= MIN_DISCOUNT and name not in seen:
                        seen[name] = True
                        msg = f"🔥 **Croma {discount}% OFF** 🔥\n\n**{name}**\n💰 {curr_price}\n📉 {discount}%\n🔗 {link}"
                        notifications.append(msg)
                except:
                    continue
        except:
            continue

    # Send notifications
    for msg in notifications[:10]:   # Limit to avoid spam
        bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')
        time.sleep(3)

    # Save seen products
    with open(seen_file, 'w') as f:
        json.dump(seen, f)

if __name__ == "__main__":
    main()
