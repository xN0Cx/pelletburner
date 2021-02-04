import board
import busio
import digitalio
import adafruit_max31856
import RPi.GPIO as GPIO
import time
import os
from pynput import keyboard

# Set GPIO PINS
GPIO.setmode(GPIO.BCM)
#Define Global Variables

tempset = 350
templevel = 4
countx = 0
cb = 22
db = 23
fm = 24
fr = 25
cb_state = "Off"
db_state = "Off"
fm_state = "Off"
fr_state = "Off"
cyclestate = "Ready"
temp = 0
state = 0

GPIO.setup(cb, GPIO.OUT)
GPIO.setup(db, GPIO.OUT)
GPIO.setup(fm, GPIO.OUT)
GPIO.setup(fr, GPIO.OUT)

clear = lambda: os.system('clear')
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
# allocate a CS pin and set the direction
cs = digitalio.DigitalInOut(board.D5)
cs.direction = digitalio.Direction.OUTPUT
# create a thermocouple object with the above
thermocouple = adafruit_max31856.MAX31856(spi, cs)

def on_press(key):
    global tempset
    global templevel
    try:
        if key.char == '1':
            tempset = 200
            templevel = 1
            print("Temp Selection 1")
        elif key.char == '2':
            tempset = 250
            templevel = 2
            print("Temp Selection 2")
        elif key.char == '3':
            tempset = 300
            templevel = 3
            print("Temp Selection 3")
        elif key.char == '4':
            tempset = 350
            templevel = 4
            print("Temp Selection 4")
        elif key.char == '5':
            tempset = 400
            templevel = 5
            print("Temp Selection 5")
        elif key.char == '6':
            tempset = 450
            templevel = 6
            print("Temp Selection 6")
        elif key.char == '7':
            tempset = 500
            templevel = 7
            print("Temp Selection 7")
    except AttributeError:
         print('\n\nInvalid Key pressed: {0} '.format(key), "Please use keys 1-7\n")

# def on_release(key):
#     print('{0} released'.format(key))
#     if key == keyboard.Key.esc:
#         return False
            

def screen_print():
    global cb_state
    global db_state
    global fm_state
    global tempset
    global templevel
    global temp
    global cyclestate
    print("\nCombustion: ", cb_state, "\t\t","Internal temperature set to: ", tempset,"\n")
    print("Distribution: ", db_state, "\t\t","Cycle State: ", cyclestate, "\n")
    print("Feed motor: ", fm_state, "\t\t","Current Temperature: %.2f" % temp, "\n\n")
    print("To select new temperature setting: Use keys 1(Low) though 7(High)")
    print("Current stove temp selection: ",templevel)
    print("\n\n\n\n")
    time.sleep(1.0)


def int_feed():
    cycle_timer = time.time()
    while time.time() - cycle_timer < 15:
        GPIO.output(fm, GPIO.LOW)
        fm_state = 'On'
        screen_print()

    while time.time() - cycle_timer < 75:
        GPIO.output(fm, GPIO.HIGH)
        fm_state = 'Off'
        screen_print()


def feed():
    GPIO.output(fm, GPIO.LOW)
    fm_state = 'On'
    screen_print()


def read_temp():
    # SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
    # SPDX-License-Identifier: MIT
    global temp
    global spi
    global cs
    global thermocouple
    time.sleep(1.0)
    temp = (9 / 5) * thermocouple.temperature + 32


def main():
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    global tempset
    global cb_state
    global db_state
    global cyclestate
    GPIO.output(cb, GPIO.HIGH)
    GPIO.output(db, GPIO.HIGH)
    GPIO.output(fm, GPIO.HIGH)
    GPIO.output(fr, GPIO.HIGH)
    clear()
         
    while 5 > 4:
        GPIO.output(cb, GPIO.LOW)
        GPIO.output(db, GPIO.LOW)
        cb_state = 'On'
        db_state = 'On'
        read_temp()
        while temp < 130:
            cyclestate = 'Start'
            read_temp()
            screen_print()
        cyclestate = 'Normal'

        screen_print()
        read_temp()
        if temp < tempset and temp > 130:
            read_temp()
            feed()

        elif temp > tempset:
            int_feed_timer = time.time()
            while time.time() - int_feed_timer < 75:
                cyclestate = 'Intermittent'
                read_temp()
                int_feed()




        else:
            time.sleep(1.0)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        # here you put any code you want to run before the program
        # exits when you press CTRL+C
        print('\r', "Inturrupt pressed, Executing shutdown", end='')
        print("\n*******CLOSE MANUAL FEED********")
        print("\nShutdown in progress, while temp is HOT, \n Combustion motor will run.")
        print("\nDistribution Blower OFF")
        GPIO.output(db, GPIO.HIGH)
        while temp > 100:
            read_temp()
            GPIO.output(fm, GPIO.LOW)
            time.sleep(5)
            print('\r', "Shutdown Cycle   Stove Temp: %.2f" % temp, end='')
            print("\nMANUAL FEED SHOULD BE CLOSED", end='')
            GPIO.output(fm, GPIO.HIGH)
            time.sleep(300)
            read_temp()
    except:
        # this catches ALL other exceptions including errors.
        # You won't get any error messages for debugging
        # so only use it once your code is working
        print("\nOther error or exception occurred!")
        print("\nShutdown in progress, while temp is HOT, \n Combustion motor will run.")
        print(" *********CLOSE MANUAL FEED********** ")
        print("\nDistribution Blower OFF")
        GPIO.output(db, GPIO.HIGH)
        while temp > 100:
            read_temp()
            print("\rShutdown in progress        Stove Temp: %.2f" % temp)
            GPIO.output(fm, GPIO.LOW)
            time.sleep(5)
            GPIO.output(fm, GPIO.HIGH)
            print('\r', "Shutdown in progress        Stove Temp: %.2f" % temp)
            time.sleep(300)
            read_temp()

    finally:
        print(" Cleaning up GPIO, SHUTDOWN complete!")
        GPIO.cleanup()  # this ensures a clean exit
