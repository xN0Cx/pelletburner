# pelletburner

DISCLAIMER - This project and code is free to use at your own risk! I assume no responsibility for use of this code in any way.
Any undesirable outcome is of your own doing and own choosing. inspect the code and be safe!
Grouping code from Adafruit, SparkFun and my own contributions.

Main Objective: To create a fully functioning pellet stove controller with off the shelf components that is safe and customizable.


Current Phase: 1
Phase1: 
    Objective: Get a basic UI and working relay board to control pellet stove combustion blower, feed motor, distribution blower, and thermocouple
    Setup GUI and layout with Tkinter
    Setup Thermocouple
    Setup relay controls
    Setup basic logic and temp control
    Ensure basic safety logic is in place

Phase2:
    Merge code and gui to operate as one
    Setup control to turn off distribution blower
    enable the touchscreen controls
    setup persistence of configuration to file

Phase3:
    Setup service and gui programs
    setup service to run constantly with watchdog service for safety
    Setup service and gui inter program communications
    Setup checks to only allow one instance of the service program to run

Bonus:
    Setup long term logging
    Setup MQTT and OpenHAB integration
    

