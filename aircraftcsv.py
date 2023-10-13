#!/usr/bin/env python3

import json
import csv
import os
from datetime import datetime, timedelta
import time

# Define the loop interval in seconds
loop_interval = 10

# Define how often to perform cleanup in seconds
clean_every = 60

# Timer
interval_time = 0

# Function to remove data older than 7 days from the CSV file
def remove_old_data(csv_file):
    seven_days_ago = datetime.now() - timedelta(days=7)
    with open(csv_file, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        rows_to_keep = [row for row in reader if row["date"] and datetime.strptime(row["date"], "%Y-%m-%d %H:%M:%S") >= seven_days_ago]

    # Rewrite the CSV file with the filtered data
    with open(csv_file, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_to_keep)

    print("Data older than 7 days removed from", csv_file)

# Function to sort the CSV by the date field in reverse order
def sort_csv_by_date(csv_file):
    with open(csv_file, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        sorted_rows = sorted(reader, key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d %H:%M:%S"), reverse=True)

    with open(csv_file, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sorted_rows)

while True:
    # Update the timer
    interval_time = interval_time + loop_interval

    # Input JSON file
    json_file = "/run/dump1090-mutability/aircraft.json"

    # Output CSV file
    csv_file = "/usr/share/dump1090-mutability/html/output.csv"

    # Get the current date and time
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check if the JSON file exists
    if not os.path.isfile(json_file):
        print(f"JSON file not found: {json_file}")
        exit(1)

    # Load JSON data
    with open(json_file, "r") as jsonfile:
        data = json.load(jsonfile)

    # Create a set to store ICAO24 addresses (hex)
    existing_hex_set = set()

    # Check if the CSV file exists
    csv_exists = os.path.isfile(csv_file)

    # Define fieldnames (all lowercase)
    fieldnames = [
        "date", "hex", "squawk", "flight", "lat", "lon", "nucp", "seenpos",
        "altitude", "vertrate", "track", "speed", "category", "messages", "seen", "rssi"
    ]

    # Open CSV file for writing, and define fieldnames if the file is new
    with open(csv_file, "a", newline="") as csvfile:

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # If the CSV file is new, write the header
        if not csv_exists:
            writer.writeheader()

        # Read existing data from CSV and add ICAO24 addresses (hex) to the set
        with open(csv_file, "r") as existing_csv:
            reader = csv.DictReader(existing_csv)
            for row in reader:
                existing_hex_set.add(row["hex"])

        # Process each aircraft from the JSON data
        for aircraft in data["aircraft"]:
            # Check if the aircraft's hex value already exists in the CSV
            if aircraft["hex"] in existing_hex_set:
                # Update the existing entry with new data and the current date
                with open(csv_file, "r") as existing_csv:
                    reader = csv.DictReader(existing_csv)
                    rows = list(reader)
                    for row in rows:
                        if row["hex"] == aircraft["hex"]:
                            # Update fields in the row only if they are not blank in the JSON
                            for key in fieldnames:
                                if key != "hex" and aircraft.get(key) != "" and aircraft.get(key) != None:  # Check if JSON field is not blank
                                    #if row[key] != aircraft.get(key): print(key, " changed from ", row[key], " to ", aircraft.get(key), " for ", aircraft["hex"])
                                    row[key] = aircraft.get(key)  # Update the field in the row
                            row["date"] = current_date  # Update the date field
                # Write the updated data back to the CSV
                with open(csv_file, "w", newline="") as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)
            else:
                with open(csv_file, "a", newline="") as csvfile:
                     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                     # Add a new entry for the aircraft with the current date
                     aircraft["date"] = current_date
                     # Filter the aircraft data to include only fields present in fieldnames
                     filtered_aircraft = {key: aircraft.get(key, "") for key in fieldnames}
                     writer.writerow(filtered_aircraft)

    print("Conversion complete. Data updated in", csv_file)

    # Sort the CSV by the date field in reverse order
    sort_csv_by_date(csv_file)

    # Remove data older than 7 days from the CSV file
    if interval_time >= clean_every:
        remove_old_data(csv_file)
        interval_time = 0

    # Sleep for the specified loop interval (10 seconds)
    time.sleep(loop_interval) 
