#! /usr/bin/python
import serial # for pulling data from Current Cost
import xml.etree.ElementTree as ET # for XML parsing
import time # for printing UNIX timecode
import urllib2 # for sending data to Pachube
import json # for assembling JSON data for Pachube
import sys # for printing errors to stderr
from cosmSender import CosmSender

#########################################
#            CONSTANTS                  #
#########################################

configTree  = ET.parse("config.xml") # load config from config file
SERIAL_PORT = configTree.findtext("serialport") # the serial port to which your Current Cost is attached
API_KEY     = configTree.findtext("apikey") # Your Pachube API Key
FEED        = configTree.findtext("feed")   # Your Pachube Feed number
DATASTREAM  = configTree.findtext("datastream") # Your Pachube datastream


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

print "time\tsensor\twatts"

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

c=CosmSender(API_KEY, FEED, dataStreamDefaults, cacheSize=3)

# continually pull data from current cost, print to stout and send to Cosm
while True:
    # Get data from Current Cost Envi
    sensor, watts = pullFromCurrentCost()

    # Print data to the standard output
    print int(time.time()), "\t", sensor, "\t", watts

    # Send data to Cosm
    try:
        c.sendData(sensor, watts)
    except:
        import traceback
        sys.stderr.write('Generic error: ' + traceback.format_exc())

    sys.stdout.flush()

# TODO
# * Use a file to store mapping between sensor numbers and names
# * automatically start a new data output file when script starts, using the correct numbering
