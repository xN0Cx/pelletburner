import datetime as dt
import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk
from tkinter import *

import matplotlib.figure as figure
import matplotlib.animation as animation
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#for thermocouple
import board
import busio
import digitalio
import adafruit_max31856

#for relay
import RPi.GPIO as GPIO
import time
#import tmp102
#import apds9301
###############################################################################
#Setup Thermocouple SPI
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
# allocate a CS pin and set the direction
cs = digitalio.DigitalInOut(board.D5)
cs.direction = digitalio.Direction.OUTPUT
# create a thermocouple object with the above
thermocouple = adafruit_max31856.MAX31856(spi, cs)
###############################################################################
# Parameters and global variables

# Parameters
update_interval = 30000 # Time (ms) between polling/animation updates
update_interval_temp = 5000
max_elements = 5000     # Maximum number of elements to store in plot lists

# Declare global variables
root = None
dfont = None
frame = None
canvas = None
ax1 = None
temp_plot_visible = None
tempset = 1
#TempSlider var
slidertemp = None

#GPIO Pins Setup
cblower = 22
dblower = 23
feedmtr = 24
feedrate = 25

#Status
CBstat = "NA"
DBstat = "NA"
FMstat = "NA"

# Global variable to remember various states
fullscreen = False
temp_plot_visible = True
light_plot_visible = True

###############################################################################
# Functions

# Toggle fullscreen
def toggle_fullscreen(event=None):

    global root
    global fullscreen

    # Toggle between fullscreen and windowed modes
    fullscreen = not fullscreen
    root.attributes('-fullscreen', fullscreen)
    resize(None)

# Return to windowed mode
def end_fullscreen(event=None):

    global root
    global fullscreen

    # Turn off fullscreen mode
    fullscreen = False
    root.attributes('-fullscreen', False)
    resize(None)

# Automatically resize font size based on window size
def resize(event=None):

    global dfont
    global frame

    # Resize font based on frame height (minimum size of 12)
    # Use negative number for "pixels" instead of "points"
    new_size = -max(12, int((frame.winfo_height() / 15)))
    dfont.configure(size=new_size)
#TempSelect
def tempSelect(scaleval):
  global tempset
  TempSelLabel.configure(text ="MANUAL SETTING: "+ scaleval)
  tempset = scaleval
# Toggle the temperature plot
def toggle_temp():

    global canvas
    global ax1
    global temp_plot_visible

    # Toggle plot and axis ticks/label
    temp_plot_visible = not temp_plot_visible
    ax1.collections[0].set_visible(temp_plot_visible)
    ax1.get_yaxis().set_visible(temp_plot_visible)
    canvas.draw()

# Toggle the light plot
#def toggle_light():
# 
#     global canvas
#     global ax2
#     global light_plot_visible
# 
#     # Toggle plot and axis ticks/label
#     light_plot_visible = not light_plot_visible
#     ax2.get_lines()[0].set_visible(light_plot_visible)
#     ax2.get_yaxis().set_visible(light_plot_visible)
#     canvas.draw()
# This function is called periodically from FuncAnimation
def animatetemp(i, ax1, xs, temps, lights, temp_c):

    # Update data to display temperature and light values
    try:
        new_temp = round(((9 / 5) * thermocouple.temperature + 32), 2)
        #new_lux = round(apds9301.read_lux(), 1)
    except:
        pass

    # Update our labels
    temp_c.set(new_temp)

# This function is called periodically from FuncAnimation
#def animate(i, ax1, ax2, xs, temps, lights, temp_c, lux):
def animate(i, ax1, xs, temps, lights, temp_c):

    # Update data to display temperature and light values
    try:
        new_temp = round(((9 / 5) * thermocouple.temperature + 32), 2)
        #new_lux = round(apds9301.read_lux(), 1)
    except:
        pass

    # Update our labels
    temp_c.set(new_temp)
    #lux.set(new_lux)

    # Append timestamp to x-axis list
    timestamp = mdates.date2num(dt.datetime.now())
    xs.append(timestamp)

    # Append sensor data to lists for plotting
    temps.append(new_temp)
    #lights.append(new_lux)

    # Limit lists to a set number of elements
    xs = xs[-max_elements:]
    temps = temps[-max_elements:]
    #lights = lights[-max_elements:]

    # Clear, format, and plot light values first (behind)
    color = 'tab:red'
    ax1.clear()
    ax1.set_ylabel('Temperature (F)', color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.fill_between(xs, temps, 0, linewidth=2, color=color, alpha=0.3)

    # Clear, format, and plot temperature values (in front)
    #color = 'tab:blue'
    #ax2.clear()
    #ax2.set_ylabel('Light (lux)', color=color)
    #ax2.tick_params(axis='y', labelcolor=color)
    #ax2.plot(xs, lights, linewidth=2, color=color)

    # Format timestamps to be more readable
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    fig.autofmt_xdate()

    # Make sure plots stay visible or invisible as desired
    ax1.collections[0].set_visible(temp_plot_visible)
    #ax2.get_lines()[0].set_visible(light_plot_visible)

# Dummy function prevents segfault
def _destroy(event):
    pass

###############################################################################
# Main script

# Create the main window
root = tk.Tk()
root.title("Pellet Burner Dashboard")

# Create the main container
frame = tk.Frame(root)
frame.configure(bg='white')

# Lay out the main container (expand to fit window)
frame.pack(fill=tk.BOTH, expand=1)

# Create figure for plotting
fig = figure.Figure(figsize=(2, 2))
fig.subplots_adjust(left=0.1, right=0.8)
ax1 = fig.add_subplot(1, 1, 1)

# Instantiate a new set of axes that shares the same x-axis
#ax2 = ax1.twinx()

# Empty x and y lists for storing data to plot later
xs = []
temps = []
lights = []

# Variables for holding temperature and light data
temp_c = tk.DoubleVar()
#lux = tk.DoubleVar()

# Create dynamic font for text
dfont = tkFont.Font(size=-24)

# Create a Tk Canvas widget out of our figure
canvas = FigureCanvasTkAgg(fig, master=frame)
canvas_plot = canvas.get_tk_widget()

# Create other supporting widgets
label_temp = tk.Label(frame, text='Temperature:', font=dfont, bg='white')
label_celsius = tk.Label(frame, textvariable=temp_c, font=dfont, bg='white')
label_unitc = tk.Label(frame, text="F", font=dfont, bg='white')
label_CB = tk.Label(frame, text="CB:", font=dfont, bg='white')
label_CBstat = tk.Label(frame, text=CBstat, font=dfont, bg='white')
label_DB = tk.Label(frame, text="DB:", font=dfont, bg='white')
label_DBstat = tk.Label(frame, text=DBstat, font=dfont, bg='white')
label_FM = tk.Label(frame, text="FM:", font=dfont, bg='white')
label_FMstat = tk.Label(frame, text=FMstat, font=dfont, bg='white')
#label_light = tk.Label(frame, text="Light:", font=dfont, bg='white')
#label_lux = tk.Label(frame, textvariable=lux, font=dfont, bg='white')
#label_unitlux = tk.Label(frame, text="lux", font=dfont, bg='white')
button_temp = tk.Button(    frame,
                            text="Toggle Temperature",
                            font=dfont,
                            command=toggle_temp)
# button_light = tk.Button(   frame,
#                             text="Toggle Light",
#                             font=dfont,
#                             command=toggle_light)
button_quit = tk.Button(    frame,
                            text="Quit",
                            font=dfont,
                            command=root.destroy)
#### TEMPERATURE Slider AREA ####
TempSelLabel = tk.Label(frame,font=dfont, text = "Select Temperature")


TempScale = tk.Scale(frame, from_=7,width=100,sliderlength=50,font=dfont, to=1,tickinterval=1,showvalue=0,orient=VERTICAL,resolution=1, command=tempSelect)

# Lay out widgets in a grid in the frame


TempSelLabel.grid(column = 1, row = 0,rowspan=1,columnspan=3)
TempScale.grid(column=0,row=1,rowspan=5,columnspan=2, sticky="WNS")
canvas_plot.grid(   row=1,
                    column=2,
                    rowspan=5,
                    columnspan=7,
                    sticky=tk.W+tk.E+tk.N+tk.S)
label_temp.grid(row=0, column=8, columnspan=2)
label_celsius.grid(row=1, column=8, sticky=tk.E)
label_unitc.grid(row=1, column=9, sticky=tk.W)
label_CB.grid(row=2, column=8, sticky=tk.E)
label_CBstat.grid(row=2, column=9, sticky=tk.W)
label_DB.grid(row=3, column=8, sticky=tk.E)
label_DBstat.grid(row=3, column=9, sticky=tk.W)
label_FM.grid(row=4, column=8, sticky=tk.E)
label_FMstat.grid(row=4, column=9, sticky=tk.W)
#label_light.grid(row=2, column=4, columnspan=2)
#label_lux.grid(row=3, column=4, sticky=tk.E)
#label_unitlux.grid(row=3, column=5, sticky=tk.W)
button_temp.grid(row=6, column=1, columnspan=3)
#button_light.grid(row=5, column=2, columnspan=2)
button_quit.grid(row=6, column=8, columnspan=2)

# Add a standard 5 pixel padding to all widgets
for w in frame.winfo_children():
    w.grid(padx=5, pady=5)

# Make it so that the grid cells expand out to fill window
for i in range(0, 5):
    frame.rowconfigure(i, weight=1)
for i in range(0, 5):
    frame.columnconfigure(i, weight=1)

# Bind F11 to toggle fullscreen and ESC to end fullscreen
root.bind('<F11>', toggle_fullscreen)
root.bind('<Escape>', end_fullscreen)

# Have the resize() function be called every time the window is resized
root.bind('<Configure>', resize)

# Call empty _destroy function on exit to prevent segmentation fault
root.bind("<Destroy>", _destroy)

# Initialize our sensors
#tmp102.init()
#apds9301.init()

# Call animate() function periodically
#fargs = (ax1, ax2, xs, temps, lights, temp_c, lux)
fargs = (ax1, xs, temps, lights, temp_c)
ani = animation.FuncAnimation(  fig,
                                animate,
                                fargs=fargs,
                                interval=update_interval)

ani1 = animation.FuncAnimation(  fig,
                                animatetemp,
                                fargs=fargs,
                                interval=update_interval_temp)

# Start in fullscreen mode and run
toggle_fullscreen()
root.mainloop()
