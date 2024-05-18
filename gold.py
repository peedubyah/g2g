import requests
import logging

# Setup logging
logging.basicConfig(filename='scrape_and_notify.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

# Function to scrape the value
def scrape_value():
    url = 'https://sls.g2g.com/offer/search?service_id=lgc_service_1&brand_id=lgc_game_26891&sort=recommended&page_size=48&cat_id=3c2a9034-2569-4484-92ad-c00e384e7085&currency=USD&country=US'
    headers = {
        'accept': 'application/json, text/plain, /',
        'accept-language': 'en-US,en;q=0.9',
        'dnt': '1',
        'origin': 'https://www.g2g.com/',
        'referer': 'https://www.g2g.com/',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Microsoft Edge";v="122"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error fetching the webpage: {e}")
        return None

    if response.status_code == 200:
        data = response.json()
        try:
            converted_unit_price = data['payload']['results'][0]['converted_unit_price']
            logging.info(f"Scraped value: {converted_unit_price}")
            return converted_unit_price
        except (KeyError, IndexError) as e:
            logging.error(f"Error parsing JSON data: {e}")
            return None
    else:
        logging.error(f"Received unexpected status code {response.status_code}")
        return None

# Function to send the value to Discord webhook
def post_to_discord(value):
    webhook_url = 'https://discord.com/api/webhooks/1210612688909107220/OcIusAZsvd3O-Yth7F3lXW5Ox7XL0T5X6R4pqJJQN128dCk6kCRNLt0O8C63ljl5X1zh'
    embed = {
        "title": "G2G Update",
        "description": ":coin:" f"[1 Million Gold](https://www.g2g.com/categories/diablo-4-gold): **${value}**",
        "color": 15258703,  # Light orange color
        "footer": {
            "text": "Data from G2G"
        }
    }
    data = {
        "embeds": [embed]
    }

    try:
        response = requests.post(webhook_url, json=data)
        response.raise_for_status()
        if response.status_code == 204:
            logging.info("Successfully sent to Discord")
        else:
            logging.error(f"Failed to send to Discord: {response.status_code}, {response.text}")
    except requests.RequestException as e:
        logging.error(f"Error sending to Discord: {e}")

# Main function to execute the task
def main():
    value = scrape_value()
    if value:
        post_to_discord(value)
    else:
        logging.error("Failed to scrape the value")

if __name__ == "__main__":
    main()
