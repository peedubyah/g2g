import requests
import logging
import csv
from tenacity import retry, stop_after_attempt, wait_fixed
from datetime import datetime

# Setup logging
logging.basicConfig(filename='scrape_and_notify.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

# Retry settings
retry_settings = {
    "stop": stop_after_attempt(5),  # Retry up to 5 times
    "wait": wait_fixed(5)           # Wait 5 seconds between retries
}

# File to save the scraped data
csv_file = 'scraped_data.csv'

# Function to initialize the CSV file
def init_csv():
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "gold_value", "duriel_ticket_price", "varshan_ticket_price"])

# Function to append data to the CSV file
def append_to_csv(timestamp, gold_value, duriel_ticket_price, varshan_ticket_price):
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, gold_value, duriel_ticket_price, varshan_ticket_price])

# Initialize the CSV file
init_csv()

# Function to scrape the Diablo IV gold value
@retry(**retry_settings)
def scrape_gold_value():
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

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    data = response.json()
    converted_unit_price = data['payload']['results'][0]['converted_unit_price']
    logging.info(f"Scraped gold value: {converted_unit_price}")
    return converted_unit_price

# Function to scrape the Duriel Ticket price
@retry(**retry_settings)
def scrape_duriel_ticket_price():
    url = 'https://sls.g2g.com/offer/search?service_id=0765978e-3fdf-48b4-bed3-184823aa439e&brand_id=lgc_game_26891&filter_attr=33821c26:0a926d8a%7C59dd7f4c:f6477539%7C9870fe77:328ce087&page_size=20&group=0&currency=USD&country=US'
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

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    data = response.json()
    formatted_unit_price = data['payload']['results'][0]['formatted_unit_price']
    logging.info(f"Scraped Duriel Ticket price: {formatted_unit_price}")
    return formatted_unit_price

# Function to scrape the Varshan Ticket price
@retry(**retry_settings)
def scrape_varshan_ticket_price():
    url = 'https://sls.g2g.com/offer/search?service_id=0765978e-3fdf-48b4-bed3-184823aa439e&brand_id=lgc_game_26891&filter_attr=33821c26:0a926d8a%7C59dd7f4c:4cce7c55%7C9870fe77:328ce087&page_size=20&group=0&currency=USD&country=US'
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

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    data = response.json()
    formatted_unit_price = data['payload']['results'][0]['formatted_unit_price']
    logging.info(f"Scraped Varshan Ticket price: {formatted_unit_price}")
    return formatted_unit_price

# Function to send the values to Discord webhook
def post_to_discord(gold_value, duriel_ticket_price, varshan_ticket_price):
    webhook_url = 'https://discord.com/api/webhooks/1210612688909107220/OcIusAZsvd3O-Yth7F3lXW5Ox7XL0T5X6R4pqJJQN128dCk6kCRNLt0O8C63ljl5X1zh'
    timestamp = datetime.now().isoformat()
    embed = {
        "title": "G2G Update",
        "description": (
            f":coin: [**1 Million Gold**](https://www.g2g.com/categories/diablo-4-gold): **${gold_value}**\n"
            f":ticket: [**Duriel Ticket Price**](https://www.g2g.com/categories/diablo-4-item-buy/offer/group?fa=33821c26%3A0a926d8a%7C59dd7f4c%3Af6477539%7C9870fe77%3A328ce087): **${duriel_ticket_price}**\n"
            f":ticket: [**Varshan Ticket Price**](https://www.g2g.com/categories/diablo-4-item-buy/offer/group?fa=33821c26%3A0a926d8a%7C59dd7f4c%3A4cce7c55%7C9870fe77%3A328ce087): **${varshan_ticket_price}**"
        ),
        "color": 15258703,  # Light orange color
        "footer": {
            "text": "Data from G2G",
            "icon_url": "https://www.g2g.com/icons/favicon-128x128.png"
        },
        "timestamp": timestamp
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

# Function to send error notifications to a separate Discord webhook
def post_error_to_discord(error_message):
    error_webhook_url = 'https://discord.com/api/webhooks/1241341809037414461/_n6QUSA-sZpmiWnHsVsJI8W2Y7_mwwdmjRIFMWXNoB1dI1F4NxLuYNoaT2qtco0VYMRk'
    data = {
        "content": error_message
    }

    try:
        response = requests.post(error_webhook_url, json=data)
        response.raise_for_status()
        if response.status_code == 204:
            logging.info("Successfully sent error message to Discord")
        else:
            logging.error(f"Failed to send error message to Discord: {response.status_code}, {response.text}")
    except requests.RequestException as e:
        logging.error(f"Error sending error message to Discord: {e}")

# Main function to execute the task
def main():
    try:
        gold_value = scrape_gold_value()
        duriel_ticket_price = scrape_duriel_ticket_price()
        varshan_ticket_price = scrape_varshan_ticket_price()
        if gold_value and duriel_ticket_price and varshan_ticket_price:
            timestamp = datetime.now().isoformat()
            append_to_csv(timestamp, gold_value, duriel_ticket_price, varshan_ticket_price)
            post_to_discord(gold_value, duriel_ticket_price, varshan_ticket_price)
        else:
            error_message = "Failed to scrape one or more values"
            logging.error(error_message)
            post_error_to_discord(error_message)
    except Exception as e:
        error_message = f"Unexpected error: {e}"
        logging.error(error_message)
        post_error_to_discord(error_message)

if __name__ == "__main__":
    main()
