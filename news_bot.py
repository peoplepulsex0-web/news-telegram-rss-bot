# news_bot.py
import os
import time
import json
import feedparser
import requests
from threading import Thread

POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "300"))
DELAY_BETWEEN_MESSAGES = float(os.getenv("DELAY_BETWEEN_MESSAGES", "2"))
SENT_STORE_FILE = os.getenv("SENT_STORE_FILE", "sent.json")

TELEGRAM_BOT_TOKEN = os.getenv("8355515207:AAFq9cHnWOfp_TYXVv33r5hkXHeB_Hj9bb0")
CHAT_ID = os.getenv("-1002747662140")

FEEDS = {
    "Local News": [
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://www.theguardian.com/world/rss"
    ],
    "Elections": [
        "https://feeds.bbci.co.uk/news/politics/rss.xml",
        "https://www.politico.eu/tag/elections/feed/"
    ],
    "Government and Policy": [
        "https://www.theguardian.com/politics/rss"
    ],
    "Economy and Finance": [
        "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
        "https://www.ft.com/?format=rss"
    ],
    "Opinions and Analysis": [
        "https://www.theguardian.com/uk/commentisfree/rss"
    ],
    "World News": [
        "https://feeds.bbci.co.uk/news/world/rss.xml"
    ],
    "Conflicts and Crises": [
        "https://www.hrw.org/rss/news"
    ],
    "Global Politics": [
        "https://www.theguardian.com/world/rss",
        "https://www.diplomatie.gouv.fr/en/backend-fd.php3"
    ],
    "Diplomacy": [
        "https://news.un.org/feed/subscribe/en/news/topic/peace-and-security/feed/rss.xml"
    ],
    "Disasters and Emergencies": [
        "https://reliefweb.int/updates/rss.xml"
    ],
    "Football": [
        "https://feeds.bbci.co.uk/sport/football/rss.xml",
        "https://www.skysports.com/rss/12040"
    ],
    "Basketball": [
        "https://feeds.bbci.co.uk/sport/basketball/rss.xml"
    ],
    "Tennis": [
        "https://feeds.bbci.co.uk/sport/tennis/rss.xml"
    ],
    "Transfers and Rumors": [
        "https://www.90min.com/posts.rss"
    ],
    "Smartphones": [
        "https://www.cnet.com/rss/news/",
        "https://www.gsmarena.com/rss-news-reviews.php3"
    ],
    "Artificial Intelligence": [
        "https://techcrunch.com/tag/artificial-intelligence/feed/",
        "https://www.analyticsinsight.net/feed/"
    ],
    "Gadgets and Reviews": [
        "https://www.techradar.com/rss"
    ],
    "Software Updates": [
        "https://www.zdnet.com/news/rss.xml",
        "https://www.ghacks.net/feed/"
    ],
    "Movies and TV": [
        "https://www.hollywoodreporter.com/feed/",
        "https://variety.com/feed/"
    ],
    "Celebrity News": [
        "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",
        "https://www.usmagazine.com/feed/"
    ],
    "Fashion and Style": [
        "https://www.theguardian.com/fashion/rss",
        "https://www.harpersbazaar.com/rss/all.xml"
    ]
}

def load_sent_store(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_sent_store(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def send_telegram_message(text, parse_mode=None, disable_web_page_preview=False):
    if not TELEGRAM_BOT_TOKEN or not CHAT_ID:
        print("Telegram token or chat id not set.")
        return None
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "disable_web_page_preview": disable_web_page_preview
    }
    if parse_mode:
        payload["parse_mode"] = parse_mode
    try:
        r = requests.post(url, data=payload, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print("Telegram send error:", e)
        return None

def fetch_and_send_news(sent_store, first_run=False):
    updated = False
    for category, urls in FEEDS.items():
        for url in urls:
            feed = feedparser.parse(url)
            if not getattr(feed, "entries", None):
                continue
            for entry in feed.entries[:10]:
                link = entry.get("link")
                title = entry.get("title", "No title")
                if not link:
                    continue
                sent_store.setdefault(url, [])
                if first_run:
                    if link not in sent_store[url]:
                        sent_store[url].append(link)
                    continue
                if link not in sent_store[url]:
                    message = f"<b>{category}</b>\n{title}\n{link}"
                    send_telegram_message(message, parse_mode="HTML")
                    print(f"Sent: {title}")
                    sent_store[url].append(link)
                    updated = True
                    time.sleep(DELAY_BETWEEN_MESSAGES)
    if updated or first_run:
        save_sent_store(SENT_STORE_FILE, sent_store)

def run_loop():
    sent_store = load_sent_store(SENT_STORE_FILE)
    print("First run: collecting existing items (will not send).")
    fetch_and_send_news(sent_store, first_run=True)
    print("Initial collection complete. Bot will now send new items only.")
    while True:
        try:
            fetch_and_send_news(sent_store, first_run=False)
            print(f"Waiting {POLL_INTERVAL} seconds...")
            time.sleep(POLL_INTERVAL)
        except Exception as e:
            print("Error in main loop:", e)
            time.sleep(10)

def start_background():
    t = Thread(target=run_loop, daemon=True)
    t.start()
