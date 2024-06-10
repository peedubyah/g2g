import feedparser
import requests
import os
import logging
from datetime import datetime
from bs4 import BeautifulSoup

# Configuration
RSS_FEED_URL = 'https://www.wowhead.com/diablo-4/blue-tracker?rss'
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1249826161966579844/s8systlKY-LwgoS8sQnOnrvr1SHZ_xn4EnRSbVUP6WEwyIomRqitvLOIiDs_fJIF6ECk'
WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
LAST_PUBLISHED_FILE = os.path.join(WORKING_DIR, 'log/homelab_last_published.txt')
LOG_FILE = os.path.join(WORKING_DIR, 'log/homelab_rss_to_discord.log')

logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

def get_last_published():
    logging.debug("Fetching last published date from file.")
    if os.path.exists(LAST_PUBLISHED_FILE):
        with open(LAST_PUBLISHED_FILE, 'r') as file:
            return file.read().strip()
    return None

def set_last_published(published):
    logging.debug(f"Setting last published date to {published}.")
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
    logging.debug(f"Extracting post text from URL: {url}")
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Log the full HTML to understand its structure
        logging.debug(f"HTML content: {soup.prettify()}")
        
        # Try to find the content within <details> tags
        post_content = soup.find('details')
        if post_content:
            logging.debug("Successfully extracted post text from <details> tag.")
            return post_content.get_text(strip=True)
        else:
            logging.debug("Post content not found in the HTML.")
    else:
        logging.debug(f"Failed to fetch the page. Status code: {response.status_code}")
    return None

try:
    logging.debug("Starting the RSS to Discord script.")
    last_published_str = get_last_published()
    logging.debug(f"Last published date string: {last_published_str}")
    last_published = datetime.fromisoformat(last_published_str) if last_published_str else None

    # Parse the RSS feed
    logging.debug("Parsing the RSS feed.")
    feed = feedparser.parse(RSS_FEED_URL)
    if feed.entries:
        logging.debug(f"Found {len(feed.entries)} entries in the RSS feed.")
        new_entries = []
        for entry in feed.entries:
            logging.debug(f"Processing entry: {entry.title}")
            entry_date = parse_date(entry)
            if not entry_date:
                logging.error("No valid date found in an entry.")
                continue
            if "Patch Notes" in entry.title and (not last_published or entry_date > last_published):
                logging.debug(f"Entry '{entry.title}' is new and contains 'Patch Notes'.")
                new_entries.append(entry)

        if new_entries:
            logging.debug(f"Found {len(new_entries)} new entries to post.")
            # Sort new entries by date to post them in order
            new_entries.sort(key=lambda e: parse_date(e))

            # Post new entries to Discord
            for entry in new_entries:
                post_text = extract_post_text(entry.link)
                if post_text:
                    data = {
                        "content": f"**{entry.title}**\n{entry.link}\n\n{post_text}"
                    }
                    logging.debug(f"Sending data to Discord: {data}")
                    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
                    logging.debug(f"Discord response status code: {response.status_code}")
                    logging.debug(f"Discord response text: {response.text}")
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
