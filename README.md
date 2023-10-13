# Dump1090-AircraftCSV
Creates a CSV and HTML page from Dump1090 data.

Dump1090 is used by multiple flight tracking programs. I personnaly have been messing aroung with FlightRadar24. This script keeps it simple and watches the json file written by dump1090 and writes a CSV file to the html directory for dump1090 so it is accessable. The html file should be saved in the same html directory (/usr/share/dump1090-mutability/html).
<br><br>
I personally like creating a service for these sort of things so below is an example of how do do that. The script needs to be run as root or the user will need to be given rights to the html directory (probably safer).
<br><br>
1. sudo nano /etc/systemd/system/fr24aircraft.service
2. Save the data below in the file
3. sudo systemctl daemon-reload
4. sudo systemctl enable fr24aircraft
5. sudo systemctl start fr24aircraft

```
## /etc/systemd/system/fr24aircraft.service

   [Unit]
   Description=FlightRadar24 Aircraft CSV
   After=network.target

   [Service]
   RemainAfterExit=yes
   WorkingDirectory=/home/pi/
   User=pi
   Group=pi

   # Start Screen and aircraft script
   ExecStart=screen -S fr -d -m sudo ./aircraft.py

   # systemd will kill Screen after the 10-second delay. No explicit kill for Screen needed
   ExecStop=screen -X -S fr quit
   ExecStop=sleep 10
   
   [Install]
   WantedBy=multi-user.target
```
