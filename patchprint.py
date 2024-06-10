import feedparser
import requests
import os
import logging
from datetime import datetime
from bs4 import BeautifulSoup

# Configuration
RSS_FEED_URL = 'https://www.wowhead.com/diablo-4/blue-tracker?rss'
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1249406808674533448/sRpLhP0JheWA6xvr9XYzOlwrtqwec4xcobM39PzFlxHATHd294T9KeOgFkxetZE8fr2k'
WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
LAST_PUBLISHED_FILE = os.path.join(WORKING_DIR, 'last_published.txt')
LOG_FILE = os.path.join(WORKING_DIR, 'rss_to_discord.log')

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s %(message)s')

def get_last_published():
    if os.path.exists(LAST_PUBLISHED_FILE):
        with open(LAST_PUBLISHED_FILE, 'r') as file:
            return file.read().strip()
    return None

def set_last_published(published):
    with open(LAST_PUBLISHED_FILE, 'w') as file:
        file.write(published)

def parse_date(entry):
    if 'published_parsed' in entry and entry.published_parsed:
        return datetime(*entry.published_parsed[:6])
    elif 'updated_parsed' in entry and entry.updated_parsed:
        return datetime(*entry.updated_parsed[:6])
    else:
        return None

def extract_post_text(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        post_content = soup.find('div', class_='content-generic-content')
        if post_content:
            return post_content.get_text(strip=True)
    return None

try:
    last_published_str = get_last_published()
    last_published = datetime.fromisoformat(last_published_str) if last_published_str else None

    # Parse the RSS feed
    feed = feedparser.parse(RSS_FEED_URL)
    if feed.entries:
        new_entries = []
        for entry in feed.entries:
            entry_date = parse_date(entry)
            if not entry_date:
                logging.error("No valid date found in an entry.")
                continue
            if "Patch Notes" in entry.title and (not last_published or entry_date > last_published):
                new_entries.append(entry)

        if new_entries:
            # Sort new entries by date to post them in order
            new_entries.sort(key=lambda e: parse_date(e))

            # Post new entries to Discord
            for entry in new_entries:
                post_text = extract_post_text(entry.link)
                if post_text:
                    data = {
                        "content": f"**{entry.title}**\n{entry.link}\n\n{post_text}"
                    }
                    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
                    if response.status_code == 204:
                        logging.info(f"Successfully posted to Discord: {entry.title}")
                    else:
                        logging.error(f"Failed to post to Discord: {response.status_code}")
                else:
                    logging.error(f"Failed to extract post text from: {entry.link}")
            
            # Update the last published date to the most recent entry
            set_last_published(parse_date(new_entries[-1]).isoformat())
        else:
            logging.info("No new entries to post.")
    else:
        logging.info("No entries found in the RSS feed.")
except Exception as e:
    logging.error(f"An error occurred: {e}")
