import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
import time
import sys
import RGB1602 as RGB1602 # RGC1602.py must be in the same directory as this script
import pdb
import csv
from typing import List


# Set up the LCD screen, 16 characters wide and 2 lines long
lcd = RGB1602.RGB1602(16, 2)

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


def process_response(departures):
    data_to_save = []

    # get the date and time at which the API request was made
    APIrequestTime = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    for bus in departures:
        departureTime = bus['departureTime']
        departureTimeUTC = datetime.fromisoformat(departureTime).astimezone(timezone.utc)
        data_to_save.append({
            'APIrequestTime': APIrequestTime,
            'routeName': bus['routeName'],
            'departureTimeUTC': departureTimeUTC,
            'displayTime': bus['displayTime']
        })
    return data_to_save

def save_dict_to_csv(list_of_dict: List[dict], filename):
    
    with open(filename, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=list_of_dict[0].keys())
        writer.writeheader()
        for d in list_of_dict:
            writer.writerow(d)


# Define function to update bus times and handle errors
def update_bus_times():
    # Get bus times from the API
    bus_times = get_bus_times()
    
    # Extract the "departures" list of dictionaries from the bus_times json
    departures = bus_times[0]['departures']

    # Process the list of dictionaries, gets time the API was requested and converts departure time to UTC
    # Returns a list of dictionaries to save to a csv file
    dicts_to_save = process_response(departures)

    # Save the list of dictionaries to a csv file
    save_dict_to_csv(dicts_to_save, "bus_times.csv")

def read_csv(filename):
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        return list(reader)


def set_lcd_colour(color: str):
    possible_colors = {
        "red": (255, 0, 0),
        "orange": (255, 165, 0),
        "green": (0, 255, 0)
    }
    if color not in possible_colors:
        raise ValueError(f"Invalid color: {color}. Must be one of {possible_colors.keys()}")
    rgb = possible_colors[color]
    lcd.setRGB(rgb[0], rgb[1], rgb[2])


def print_to_lcd(bus_times):
    # Get the first bus from the list of dictionaries
    next_bus = bus_times[0]
    routeName = next_bus['routeName']
    displayTime = next_bus['displayTime']

    # Print message for when next bus will depart and its bus number
    lcd.setCursor(0, 0)
    lcd.printout("") # clear the screen
    lcd.printout(f"Next {routeName}: {displayTime}")

    # Calculate the minutes until the next bus
    departureTimeUTC_str = next_bus['departureTimeUTC']
    departureTimeUTC = datetime.strptime(departureTimeUTC_str, '%Y-%m-%d %H:%M:%S%z').replace(tzinfo=timezone.utc)
    currentTime = datetime.now(timezone.utc)
    minutes = int((departureTimeUTC - currentTime).total_seconds() / 60)

    # Print message depending on how many minutes until the next bus
    lcd.setCursor(0, 1)
    lcd.printout("") # clear the screen
    if minutes <= 10 and minutes > 5:
        lcd.printout("Leave now!")
        set_lcd_colour("green")
    elif minutes == 4 or minutes == 5:
        lcd.printout("Walk quickly!")
        set_lcd_colour("orange")
    elif minutes < 4:
        lcd.printout("Missed this bus!")
        set_lcd_colour("red")
    else:
        lcd.printout(f"in {minutes} mins")
        set_lcd_colour("green")

def main():
    # Read the bus times from the csv file
    bus_times = read_csv("bus_times.csv")

    # Check the time the API was called
    APIrequestTime_str = bus_times[0]['APIrequestTime']
    
    # If the API request time is more than 3 minutes ago, refresh the csv file and reload the new data
    current_time = datetime.now(timezone.utc)
    APIrequestTime = datetime.strptime(APIrequestTime_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)

    if ( current_time - APIrequestTime  ).total_seconds() >= 3 * 60:
        update_bus_times()
        bus_times = read_csv("bus_times.csv")
   
    # Print to the lcd screen
    print_to_lcd(bus_times)


main()


