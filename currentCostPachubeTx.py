#! /usr/bin/python
import serial # for pulling data from Current Cost
import xml.etree.ElementTree as ET # for XML parsing
import urllib2 # for sending data to Pachube
import json # for assembling JSON data for Pachube
import time # for printing UNIX timecode
import sys # for handling errors

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
    watts = None
    while watts == None:
        line = ser.readline()
        try:
            tree  = ET.XML( line )
            watts = tree.findtext("ch1/watts")
        except Exception, inst: # Catch XML errors (occasionally the current cost outputs malformed XML)
            sys.stderr.write("XML error: " + str(inst))
            line = None
        
    ser.flushInput()
    return watts


#########################################
#        PUSH TO PACHUBE                #
#########################################

def pushToPachube( reading ):
    '''For sending a single reading to Pachube'''
    # adapted from http://stackoverflow.com/a/111988
    reading = int(reading)
    jsonData = json.dumps({
                           "version":"1.0.0",
                           "datastreams":[{
                                           "id"           : DATASTREAM,
                                           "current_value": reading,
                                           "min_value"    : 0.0,
                                           "unit": {
                                                    "type"  : "derivedSI",
                                                    "label" : "watt",
                                                    "symbol": "W"}
                                           }
                                          ] 
                           })
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    request = urllib2.Request('http://api.pachube.com/v2/feeds/'+FEED, data=jsonData)
    request.add_header('X-PachubeApiKey', API_KEY)
    request.get_method = lambda: 'PUT'
    try:
        opener.open(request)
#    except urllib2.URLError as reason:
#        sys.stderr.write("URL IO error: " + str(reason) + "\n")
#    except urllib2.HTTPError as reason:
#        sys.stderr.write("HTTP error: " + str(reason) + "\n")
#    except httplib.HTTPException as reason:
#        sys.stderr.write("httplib.HTTPException: " + str(reason) + "\n")
    except Exception:
        import traceback
        sys.stderr.write('Generic error: ' + traceback.format_exc())

#########################################
#          MAIN                         #
#########################################

print "UNIX time \t watts"

# initialise serial port
ser = serial.Serial(SERIAL_PORT, 57600)
ser.flushInput() # get rid of 

# continually pull data from current cost, print to stout and send to pachube
while True:
    data = pullFromCurrentCost()
    print int(time.time()), "\t", data
    pushToPachube( data )
    sys.stdout.flush()
