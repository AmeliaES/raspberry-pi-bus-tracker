import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
import time
import json
import math

import sys
import RGB1602 as RGB1602


# Set up the LCD screen
colorR = 64
colorG = 128
colorB = 64

lcd=RGB1602.RGB1602(16,2)
rgb_pink = (252, 3, 128)

lcd.setRGB(rgb_pink[0],rgb_pink[1],rgb_pink[2]);

# Load environment variables from .env
load_dotenv()

# Get API key and stop ID from environment variables in the .env file
API_KEY = os.getenv("API_KEY")
STOP_ID = os.getenv("STOP_ID")

# Set up the API URL and headers (https://tfe-opendata.readme.io/docs/authentication-1)
# The URL specified is for live_bus_times (https://tfe-opendata.readme.io/docs/live-bus-times)
API_URL = f"https://tfe-opendata.com/api/v1/live_bus_times/{STOP_ID}"
HEADERS = {"Authorization": f"Token {API_KEY}"}

# Define function to return a json of bus times from specified bus stop
# def get_bus_times():
#     response = requests.get(API_URL, headers=HEADERS)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         raise ValueError(f"Error getting bus times: {response.text}. Error code: {response.status_code}") # note this text is in html

# bus_times = get_bus_times()

# # Save bus_times as a JSON file called live_bus_times.json
# # whilst testing script as not to make too many API requests

# with open("live_bus_times.json", "w") as json_file:
#     json.dump(bus_times, json_file)

# Load bus_times from the JSON file
with open("live_bus_times.json", "r") as json_file:
    bus_times = json.load(json_file)

# Extract the routeName which is the bus number, eg. 8
routeName = bus_times[0]['departures'][0]['routeName']
# Extract the displayTime which is the time the bus is due to depart
displayTime = bus_times[0]['departures'][0]['displayTime']
# Extract the full departure time, so minutes until next bus can be calculated
departureTime = bus_times[0]['departures'][0]['departureTime']

# Print how many minutes until the next bus
# Get current time and minus the displayTime
departureTimeUTC = datetime.fromisoformat(departureTime).astimezone(timezone.utc)
currentTime = datetime.now(timezone.utc)

while True:
    # Update current time every loop
    currentTime = datetime.now(timezone.utc)
    current_hour = currentTime.hour
    current_minute = currentTime.minute
    departure_hour = departureTimeUTC.hour
    departure_minute = departureTimeUTC.minute

    if departureTimeUTC > currentTime:
        time_difference = departureTimeUTC - currentTime
        minutes = int(time_difference.total_seconds() / 60)

        # Print message for when next bus will depart and it's bus number
        lcd.setCursor(0, 0)
        lcd.printout(f"Next {routeName}: {displayTime}")

        lcd.setCursor(0, 1)
        if minutes <= 10 and minutes > 5:
            lcd.printout("Leave now!")
        elif minutes == 4 or minutes == 5:
            lcd.printout("Walk quickly!")
        elif minutes < 4:
            lcd.printout("Missed this bus!")
        else:
            lcd.printout(f"in {minutes} mins")

        # Wait for 30 secs before printing again
        time.sleep(30)
    else:
        break


  


