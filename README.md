# Kona Serial Obd Python
Allows you to connect to the ecu of the car to obtain SOC, BATTERIES VOLTAGE and STATE OF CHARGE informations. I suggest you to make a simple change to deliver the data to your server or to Home Assistant (personally i prefer Tinytuja).
This project is not for everybody, it's mainly for developers: lots of times with tecnology we can just try and see if it works or not, but i don t suggest you to test this project on your car if you don t know what you are doing.

<img width="500" height="375" alt="immagine" src="https://github.com/user-attachments/assets/51d80612-8e16-491c-a9d5-177f69f21667" />

# Output

Connected to OBD2 adapter on COM5

    Sending: 220105
    >
    Parsed Data: {'SOC_DISPLAY': 39.5, 'SOH': 100.0}
    Sending: 220101
    >
    Parsed Data: {'SOC_BMS': 38.0, 'DC_BATTERY_VOLTAGE': 356.7}

Process finished with exit code 0

# Dependencies
    pip3 install pyserial

# Usage
- Connect to your device and identify witch port is using (useually in windows it's COM5 or COM6 and in linux it is usually /dev/rfcomm0)
- Run the main.py

# My hardware
In order to use this project you will need:
- A hyundai Kona (~2020) or a hyundai Kia niro (kona and kia niro seems to use the same protocol i need to check the exact model of my car )
- An obd2 elm serial bluetooth chip that supports EV ecu (not all supports it). There are plenty of discussion about the "good" and the "bad" OBD, onestly i don t care and bought the cheapest one from aliexpress (photo) and it worked but remember that the OBD needs to be BLUETOOTH SERIAL!!! The use of the software is at your own risk. I am not liable for damage caused by improper use or cheap, fake OBD2 dongle.
- A windows or linux pc with bluez installed (mac os sucks with bluez, good luck setting it up)

<img width="600" height="400" alt="immagine" src="https://github.com/user-attachments/assets/b843a3ee-ab34-4eea-ab8a-98c80fedf239" />

# Known facts
- the car seems to keep the obd running only when turned on or during charge (need to check for edge cases like soc 100% but still plugged)
- the device sometimes responds with NO DATA while charging, the solution seems to reconnect (problem found from EV notify github issues and happened to me only once)

# Resources
There are other resources that helped me a lot in this project like EVNotify inspired me first in this hard journey or the recent project niro-spy that gave me the willingness of sharing
- https://github.com/EVNotify/EVNotify/ 
- https://github.com/Tuoris/niro-spy
- https://github.com/OBDb/Hyundai-Kona-Electric
- https://github.com/JejuSoul/OBD-PIDs-for-HKMC-EVs

# Similiar projects
- https://github.com/nickn17/evDash
- https://github.com/cyberelectronics/Konassist
- https://github.com/openvehicles/Open-Vehicle-Monitoring-System-3
- https://github.com/Tuoris/elm-dashboard

# My projects
- https://github.com/rabdo-alter-ego/kona-serial-obd/



