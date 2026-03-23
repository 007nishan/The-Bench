import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import sys

# Add current folder to path
root_dir = os.path.abspath(os.path.dirname(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app
from models import db, FeedItem

FEED_URLS = {
    "jobs": "https://www.livelaw.in/job-updates",
    "corporate": "https://www.livelaw.in/corporate-law",
    "international": "https://www.livelaw.in/more/international",
    "labour": "https://www.livelaw.in/labour-service",
    "tech": "https://www.livelaw.in/tech-law"
}

def clean_text(text):
    if not text: return ""
    # Strip Live Law signatures
    noise = ["Live Law", "LiveLaw", "all about law", "livelaw", "LIVELAW"]
    for word in noise:
        text = text.replace(word, "The Bench")
    return text.strip()

def scrape_feed(category, url):
    print(f"Scraping {category} from {url}...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            print(f"Failed to fetch {url}: {res.status_code}")
            return
            
        soup = BeautifulSoup(res.content, 'html.parser')
        # Updated selectors based on static HTML inspection
        cards = soup.select('div.sup_crt_col_border_bottom.grid_page')
        
        if not cards:
            print(f"No explicit cards found on {category}. Trying standard grid iteration.")
            cards = soup.select('div.col-md-4') or soup.find_all('div', class_=lambda x: x and ('card' in x or 'list-item' in x))
            
        print(f"Found {len(cards)} items to process.")

        print(f"Found {len(cards)} items to process.")
        
        for card in cards[:6]: # limit to 6
            title_node = card.select_one('h5') or card.select_one('h1') or card.select_one('a')
            desc_node = card.select_one('p')
            img_node = card.select_one('img')
            
            title = clean_text(title_node.get_text() if title_node else "")
            desc = clean_text(desc_node.get_text() if desc_node else "")
            
            print(f"[{category}] Parsed Title: {title}")
            
            # Find link
            link = ""
            if title_node and title_node.name == 'a':
                link = title_node.get('href', "")
            elif card.find('a'):
                link = card.find('a').get('href', "")
                
            if link and not link.startswith('http'):
                link = "https://www.livelaw.in" + link
                
            img_url = ""
            if img_node:
                img_url = img_node.get('data-src') or img_node.get('src') or ""
            
            if title and title not in ["LoginAccount", "Subscribe Premium"]:
                # Upsert into DB
                existing = FeedItem.query.filter_by(title=title, category=category).first()
                if not existing:
                    item = FeedItem(
                        category=category,
                        title=title,
                        description=desc,
                        image_url=img_url,
                        source_link=link
                    )
                    db.session.add(item)
                    print(f"Saved: {title}")
                    
        db.session.commit()
            
    except Exception as e:
        print(f"Error scraping {category}: {e}")

def run():
    with app.app_context():
        # Optional: Clear old feeds if you want fresh only (uncomment if desired)
        # FeedItem.query.delete()
        
        for category, url in FEED_URLS.items():
            scrape_feed(category, url)

if __name__ == '__main__':
    run()
