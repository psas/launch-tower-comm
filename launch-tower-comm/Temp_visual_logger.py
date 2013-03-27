#! /usr/bin/python

# Temperature sensor application that graphs live on the screen
# Depends on matplotlib, wxpython, numpy, and python.
# (c) Phidgets 2012

import os
import pprint
import random
import sys
import wx

import matplotlib       # Provides the graph figures
matplotlib.use('WXAgg') # matplotlib needs a GUI (layout), we use wxPython

from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigCanvas

import numpy as np  # For efficient data array handling
import pylab       

from time import time, sleep

# Phidget specific imports
from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import *
from Phidgets.Devices.TemperatureSensor import *

# Globals
warnings = 0    # Array mis-alignments due to type
looped = False  # When we start re-using array space for efficiency
start = time()

thermocoupleIndex = 0   # The port that the thermocouple is in
thermocoupleType = ThermocoupleType.PHIDGET_TEMPERATURE_SENSOR_K_TYPE

# ================= Phidget Helper Functions =================================

def printPhidgetException(e):
    errorCode = e.device.code
    errorDescription = e.device.description
    print "Phidget Exception " + errorCode + ": " + errorDescription

def printRuntimeException(e):
    errorDescription = e.device.details
    print "Runtime Exception: " + errorDescription

# ================= Phidget Event Handlers ===================================

def thermocoupleAttached(e):
    global thermocoupleIndex
    global thermocoupleType

    serialNum = e.device.getSerialNum()
    print "Temperature Sensor Board " + str(serialNum) + " Attached..."

    try: e.device.setThermocoupleType(thermocoupleIndex, thermocoupleType)
    except PhidgetException as e: printPhidgetException(e)
    e.device.setTemperatureChangeTrigger(thermocoupleIndex, 0)


def thermocoupleDetached(e):
    serialNum = e.device.getSerialNum()
    print "Temperature Sensor Board " + str(serialNum) + " Detached..."

def thermocoupleError(e):
    try:
        errorDescription = e.description
        print "Phidget Error: " + errorDescription
    except PhidgetException as e:
        printPhidgetException(e)

def temperatureChanged(e):
    global start
    global app
    now = time() - start
    try:
        app.updateTemperature(e.temperature, now)
    except NameError as e:
        print "Still waiting for GUI initialization..."

# ================= Main Layout, including Graphs ============================
        
class MainFrame(wx.Frame):

    def __init__(self, parent, id, title=None):

        global thermocoupleIndex
        global thermocoupleType

        # Create the Phidget software object, hook in the event function, and open the object
        # Note that these functions can run into trouble - for stable code, add exception catching
        thermocouple = TemperatureSensor()
        thermocouple.setOnAttachHandler(thermocoupleAttached)
        thermocouple.setOnDetachHandler(thermocoupleDetached)
        thermocouple.setOnErrorhandler(thermocoupleError)
        thermocouple.setOnTemperatureChangeHandler(temperatureChanged)
        thermocouple.openPhidget()

        self.thermocouple = thermocouple

        # Sizing information.  Pixels sizes for the Frame are dpi * length
        self.dpi = 100
        self.height = 5
        self.width = 10

        wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition, 
                          ((self.width * self.dpi), (self.height * self.dpi)))

        # Maximum total time (seconds) to be displayed on x axis 
        self.maximumData = 60
        # Number of data points before cropping the visual graph arrays
        self.maximumArray = 3000    

        while not thermocouple.isAttached():
            sleep(0.1)

        initialTemperature = thermocouple.getTemperature(thermocoupleIndex)

        # ---------- GUI Variables

        # Other inputs in the GUI
        self.avgOver = 50      # Averaging window

        # Graph Arrays
        self.data = [initialTemperature]       # Yellow line, actual measured temp
        self.time = [0]                        # Total time elapsed, x axis
        self.avgData = [initialTemperature]    # Blue line, averaged temp

        # --------- Helper Background Variables

        # Total time elapsed
        self.totalTime = 0        

        # Though graph arrays are recycled, these store all data for export
        self.fileTime = [0]
        self.fileTemperature = [initialTemperature]

        # --------- GUI and graph initialization

        self.panel = wx.Panel(self, -1)


        self.initPlot()
        self.createMenu()


        self.canvas = FigCanvas(self.panel, -1, self.fig)

        # This times fires every 100 ms to redraw the graphs
        self.redrawTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onRedrawTimer, self.redrawTimer)        
        self.redrawTimer.Start(100)
       
        # -------- GUI components

        self.graphBox = wx.BoxSizer(wx.VERTICAL)
        self.graphBox.Add(self.canvas, 1, flag=wx.LEFT | wx.TOP | wx.GROW) 

        self.panel.SetSizer(self.graphBox)
        self.panel.Show()

    # ------------------ Event Handler Functions

    def onClose(self, event):
        self.thermocouple.closePhidget()
        self.Close()

    def updateTemperature(self,temperature,time):

        avgSum = 0
        window = self.avgOver if self.avgOver < len(self.data) else len(self.data)
        for a in range(window):
            avgSum = avgSum + self.data[(-1 * a)]
        avgSum = avgSum / window
        self.avgData.append(float(avgSum))

        self.data.append(float(temperature))
        self.time.append(float(time))
        self.totalTime = time

        if len(self.data) > self.maximumArray:
            global looped
            if not looped:
                print "Starting re-use of graph arrays for efficiency..."
                looped = True
            self.time.pop(0)
            self.avgData.pop(0)
            self.data.pop(0)

        self.fileTime.append(float(time))
        self.fileTemperature.append(float(temperature))

    # ---------- Plot and canvas (graph) functionality

    # Size, color, etc
    def initPlot(self):
        self.fig = Figure((self.width, (self.height)), dpi=self.dpi)

        self.axes = self.fig.add_subplot(111)
        self.axes.set_axis_bgcolor('black')
        self.axes.set_title('Temperature and Average', size=12)
        self.axes.set_xlabel("Time (seconds)", size=10)
        self.axes.set_ylabel("Degrees C", size=10)

        pylab.setp(self.axes.get_xticklabels(), fontsize=8)
        pylab.setp(self.axes.get_yticklabels(), fontsize=8)

        self.plotData = self.axes.plot(
            self.data, 
            linewidth=1,
            color=(1, 1, 0),
            )[0]


        self.plotAvg = self.axes.plot(
            self.avgData, 
            linewidth=1,
            color=(0, 0, 1),
            )[0]


    # What gets called each on each redraw timer fire event
    def drawPlot(self):

        gap = self.maximumData
        xmax = self.totalTime if self.totalTime > gap else gap      
        xmin = xmax - gap

        ymin = round(min(self.data), 0) - (0.1 * abs(round(min(self.data), 0)))
        ymax = round(max(self.data), 0) + (0.1 * round(max(self.data), 0))

        self.axes.set_xbound(lower=xmin, upper=xmax)
        self.axes.set_ybound(lower=ymin, upper=ymax)
        
        self.axes.grid(True, color='gray')
        pylab.setp(self.axes.get_xticklabels(), 
            visible=True)

        self.plotAvg.set_data(np.array(self.time), np.array(self.avgData))
        self.plotData.set_data(np.array(self.time), np.array(self.data))

        self.canvas.draw()

    def onRedrawTimer(self, event): 
        global warnings 
        try:         
            self.drawPlot()
        except RuntimeError as e:
            warnings = warnings + 1

    # ------------------ Top Menu

    # The top menu under File, including saving as csv, image, or exiting.
    # This also handles the Ctrl-X shortcut for exiting.
    def createMenu(self):
        self.menuBar = wx.MenuBar()
        
        self.menuFile = wx.Menu()
        menuSaveCSV = self.menuFile.Append(-1, "&Save plot as CSV", "Save data to csv")
        self.Bind(wx.EVT_MENU, self.onSaveCSV, menuSaveCSV)
        menuSave = self.menuFile.Append(-1, "&Save plot as image", "Save plot to image")
        self.Bind(wx.EVT_MENU, self.onSavePlot, menuSave)
        self.menuFile.AppendSeparator()
        menuExit = self.menuFile.Append(-1, "E&xit\tCtrl-X", "Exit")
        self.Bind(wx.EVT_MENU, self.onClose, menuExit)
                
        self.menuBar.Append(self.menuFile, "&File")
        self.SetMenuBar(self.menuBar)


    # ----- Save as Image
    def onSavePlot(self, event):
        fileChoices = "PNG (*.png)|*.png"
        
        dlg = wx.FileDialog(
            self, 
            message="Save plot as...",
            defaultDir=os.getcwd(),
            defaultFile="plot.png",
            wildcard=fileChoices,
            style=wx.SAVE)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.canvas.print_figure(path, dpi=self.dpi)

    # ----- Save as file 

    # Note this saves -all- data from self.fileX variables
    def onSaveCSV(self, event):
        fileChoices = "CSV (*.csv)|*.csv"
        
        dlg = wx.FileDialog(
            self, 
            message="Save data as...",
            defaultDir=os.getcwd(),
            defaultFile="plot.csv",
            wildcard=fileChoices,
            style=wx.SAVE)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            outFile = open(path, 'w')

            outFile.write("Time,Temp\n")
            for i in range(len(self.data)):
                outFile.write(str(self.fileTime[i]) + ",")
                outFile.write(str(self.fileTemperature[i]) + "\n")
            outFile.close()

# ====================== Main Class, Holding Frame ==========================

class MainClass(wx.App):
    def OnInit(self):
        self.frame = MainFrame(None, -1, 'Temperature Graph')
        self.frame.Show(True)
        self.frame.Centre()
        return True

    # The event trigger for the Phidget is passed through the Main Class
    def updateTemperature(self, temperature, time):
        self.frame.updateTemperature(temperature, time)

# Actually start the program
app = MainClass(0)
app.MainLoop()

# Warnings usually only occur for very fast Phidgets, like Motors
print "Done, " + str(warnings) + " plot delays due to timing events"
exit(0)

#=============================================================================
# EOF
#=============================================================================


