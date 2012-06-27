#! /usr/bin/python
import serial # for pulling data from Current Cost
import xml.etree.ElementTree as ET # for XML parsing
import time # for printing UNIX timecode
import urllib2 # for sending data to Pachube
import json # for assembling JSON data for Pachube
import sys # for printing errors to stderr
from cosmSender import CosmSender
import os # to find names of existing files

#########################################
#            CONSTANTS                  #
#########################################

configTree  = ET.parse("config.xml") # load config from config file
SERIAL_PORT = configTree.findtext("serialport") # the serial port to which your Current Cost is attached
API_KEY     = configTree.findtext("apikey") # Your Cosm API Key
FEED        = configTree.findtext("feed")   # Your Cosm Feed number
FILENAME    = configTree.findtext("filename") # File to save data to

#########################################
#     SENSOR NAMES                      #
#########################################
try:
    f = open('sensorNames.csv')
    lines = f.readlines()
    sensorNames = [ line.strip() for line in lines ]
except:
    sys.stderr.write('WARNING: sensorNames.csv not found.  Will just use sensor numbers instead.\n')
    sensorNames = None

#########################################
#          PULL FROM CURRENT COST       #
#########################################

def pullFromCurrentCost():
    ''' read line of XML from the CurrentCost meter and return instantaneous power consumption. '''
    # For Current Cost XML details, see currentcost.com/cc128/xml.htm
    
    # Read XML from Current Cost.  Try again if nothing is returned.
    watts  = None
    sensor = None
    while watts == None:
        line = ser.readline()
        try:
            tree  = ET.XML( line )
            watts  = tree.findtext("ch1/watts")
            sensor = tree.findtext("sensor")
        except Exception, inst: # Catch XML errors (occasionally the current cost outputs malformed XML)
            sys.stderr.write("XML error: " + str(inst))
            line = None
        
    ser.flushInput()
    return sensor, watts


#########################################
#          MAIN                         #
#########################################

# initialise serial port
ser = serial.Serial(SERIAL_PORT, 57600)
ser.flushInput()

# Setup CosmSender
dataStreamDefaults = {
    "min_value"    : "0.0",
    "unit": { "type"  : "derivedSI",
              "label" : "watt",
              "symbol": "W"
            }
    }

c = CosmSender(API_KEY, FEED, dataStreamDefaults, cacheSize=10)

# continually pull data from current cost, write to file, print to stout and send to Cosm
while True:
    # Get data from Current Cost Envi
    sensor, watts = pullFromCurrentCost()

    # open data file
    try:
        datafile = open(FILENAME, 'a+')
    except Exception, e:
        sys.stderr.write("""ERROR: Failed to open data file " + FILENAME +
Has it been configured correctly in config.xml?""")
        raise

    # Print data to the file
    UNIXtime = str ( int( round(time.time()) ) )
    string   = UNIXtime + "\t" + sensor + "\t" + watts + "\n"
    datafile.write( string )
    datafile.close()
    print string,

    # Send data to Cosm
    if sensorNames == None:
        sensorName = sensor
    else:
        sensorName = sensor + '_' + sensorNames[int(sensor)]

    try:
        c.sendData(sensorName, watts)
    except:
        import traceback
        sys.stderr.write('Generic error: ' + traceback.format_exc())

    sys.stdout.flush()

c.flush()
