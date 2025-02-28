import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
import time
import sys
import RGB1602 as RGB1602 # RGC1602.py must be in the same directory as this script

# Set up the LCD screen, 16 characters wide and 2 lines long
lcd = RGB1602.RGB1602(16, 2)
# Change the RGB values so the screen is a pink colour
rgb_pink = (252, 3, 128)

lcd.setRGB(rgb_pink[0], rgb_pink[1], rgb_pink[2])

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
def get_bus_times():
    print(f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} - Requesting bus times from API...")
    response = requests.get(API_URL, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        raise ValueError(f"Error getting bus times: {response.text}. Error code: {response.status_code}") # note this text is in html

# Define function to update bus times and handle errors
def update_bus_times():
    global bus_times, departure, routeName, displayTime, departureTime, departureTimeUTC
    try:
        bus_times = get_bus_times()
        departure = bus_times[0]['departures'][0]
        routeName = departure['routeName']
        displayTime = departure['displayTime']
        departureTime = departure['departureTime']
        departureTimeUTC = datetime.fromisoformat(departureTime).astimezone(timezone.utc)
    except Exception as e:
        print(f"Error updating bus times: {e}")
        return False
    return True

# Initial update of bus times
start_time = datetime.now(timezone.utc)
if not update_bus_times():
    lcd.clear()
    sys.exit(1)

while True:
    # Update current time every loop
    currentTime = datetime.now(timezone.utc)
    # Check if 30 minutes have passed since the start time
    if (currentTime - start_time).total_seconds() >= 30 * 60:
        print(f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} - 30 minutes have passed. Exiting the script.")
        break

    current_hour = currentTime.hour
    current_minute = currentTime.minute
    departure_hour = departureTimeUTC.hour
    departure_minute = departureTimeUTC.minute
    time_difference = departureTimeUTC - currentTime
    minutes = int(time_difference.total_seconds() / 60)

    if departureTimeUTC > currentTime and minutes >= 4:
        # Print message for when next bus will depart and its bus number
        lcd.setCursor(0, 0)
        lcd.printout("") # clear the screen
        lcd.printout(f"Next {routeName}: {displayTime}")

        lcd.setCursor(0, 1)
        lcd.printout("") # clear the screen
        if minutes <= 10 and minutes > 5:
            lcd.printout("Leave now!")
        elif minutes == 4 or minutes == 5:
            lcd.printout("Walk quickly!")
        elif minutes < 4:
            lcd.printout("Missed this bus!")
        else:
            lcd.printout(f"in {minutes} mins")

        # Wait for 30 seconds before printing again
        time.sleep(30)
        
        # Refresh bus times every 3 minutes
        if (datetime.now(timezone.utc) - currentTime).total_seconds() >= (3 * 60):
            if not update_bus_times():
                lcd.clear()
                break
    else:
        # Refresh bus times if the bus has already left
        if not update_bus_times():
            lcd.clear()
            break
