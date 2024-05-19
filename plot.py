import pandas as pd
import matplotlib.pyplot as plt

# Load the data from the CSV file
csv_file = 'scraped_data.csv'
data = pd.read_csv(csv_file)

# Convert the timestamp column to datetime
data['timestamp'] = pd.to_datetime(data['timestamp'])

# Set the timestamp column as the index
data.set_index('timestamp', inplace=True)

# Plot the data
plt.figure(figsize=(10, 6))
plt.plot(data.index, data['gold_value'], label='1 Million Gold')
plt.plot(data.index, data['duriel_ticket_price'], label='Duriel Ticket Price')
plt.plot(data.index, data['varshan_ticket_price'], label='Varshan Ticket Price')
plt.xlabel('Timestamp')
plt.ylabel('Price (USD)')
plt.title('Prices of 1 Million Gold, Duriel Ticket, and Varshan Ticket Over Time')
plt.legend()
plt.grid(True)
plt.tight_layout()

# Save the plot as an image file
plt.savefig('prices_over_time.png')

# Show the plot
plt.show()
