#!/bin/bash

# Change to the project directory
cd /home/amelia/Projects/rpi-lcd

# Wait for network connectivity (try for up to 1 minute)
echo "Waiting for network connectivity..."
for i in {1..12}; do
    if ping -c 1 8.8.8.8 > /dev/null 2>&1; then
        echo "Network is up!"
        break
    fi
    echo "Network not ready yet. Attempt $i/12..."
    sleep 5
done

# Activate the virtual environment
source .venv/bin/activate

# Run the bus display script
echo "Starting bus display script at $(date)"
python scripts/get_next_bus.py 2>&1 | tee -a /home/amelia/bus_script.log
echo "Completed bus display script at $(date)"

# Wait for 20 minutes
echo "Waiting for 30 minutes before clearing screen..."
sleep 1200  # 20 minutes = 1200 seconds

# Clear the LCD display
echo "Clearing LCD display..."
python scripts/clear_lcd.py 2>&1 | tee -a /home/amelia/bus_script.log
