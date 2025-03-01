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
LCD = RGB1602.RGB1602(16, 2)

# Load environment variables from .env
load_dotenv()

# Get API key and stop ID from environment variables in the .env file
API_KEY = os.getenv("API_KEY")
STOP_ID = os.getenv("STOP_ID")
# Set up the API header (https://tfe-opendata.readme.io/docs/authentication-1)
HEADERS = {"Authorization": f"Token {API_KEY}"}


# Define function to return a json of bus times from specified bus stop
def get_bus_times(stop_id):
    print(f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} - Requesting bus times from API...")
    # The URL specified is for live_bus_times (https://tfe-opendata.readme.io/docs/live-bus-times)
    api_url = f"https://tfe-opendata.com/api/v1/live_bus_times/{stop_id}"
    response = requests.get(api_url, headers=HEADERS)
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
    bus_times = get_bus_times(STOP_ID)
    
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
        "green": (53, 181, 70),
        "blue": (63, 168, 209)
    }
    if color not in possible_colors:
        raise ValueError(f"Invalid color: {color}. Must be one of {possible_colors.keys()}")
    rgb = possible_colors[color]
    LCD.setRGB(rgb[0], rgb[1], rgb[2])


def minutes_until_bus(bus):
    # Calculate the minutes until the next bus
    departureTimeUTC_str = bus['departureTimeUTC']
    departureTimeUTC = datetime.strptime(departureTimeUTC_str, '%Y-%m-%d %H:%M:%S%z').replace(tzinfo=timezone.utc)
    currentTime = datetime.now(timezone.utc)
    minutes = int((departureTimeUTC - currentTime).total_seconds() / 60)
    return minutes


def get_next_available_bus(bus_times):
    for bus in bus_times:
        minutes = minutes_until_bus(bus)
        if minutes >= 4:
            return bus


def print_to_lcd(next_bus):
    routeName = next_bus['routeName']
    displayTime = next_bus['displayTime']

    # Print message for when next bus will depart and its bus number
    LCD.setCursor(0, 0)
    LCD.printout("") # clear the screen
    LCD.printout(f"Next {routeName}: {displayTime}")

    minutes = minutes_until_bus(next_bus)

    # Print message depending on how many minutes until the next bus
    LCD.setCursor(0, 1)
    LCD.printout("") # clear the screen
    if 5 < minutes <= 10:
        LCD.printout("Leave now!")
        set_lcd_colour("green")
    elif minutes == 5:
        LCD.printout("Walk quickly!")
        set_lcd_colour("orange")
    elif minutes == 4:
        LCD.printout(f"Run!")
        set_lcd_colour("red")
    else:
        LCD.printout(f"in {minutes} mins")
        set_lcd_colour("blue")


def main():
    # Calls the API and saves list of bus time dictionaries to a csv file
    update_bus_times()

    # Get list of dictionaries of buses from the csv file
    bus_times = read_csv("bus_times.csv")

    # Get the next bus time, that's at least 4 minutes away
    bus_time = get_next_available_bus(bus_times)
   
    # Print to the lcd screen
    print_to_lcd(bus_time)


main()


