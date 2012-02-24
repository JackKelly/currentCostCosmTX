#! /usr/bin/env python
import serial # for pulling data from Current Cost
import xml.etree.ElementTree as ET # for XML parsing
import urllib2 # for sending data to Pachube
import json # for assembling JSON data for Pachube
import time # for printing UNIX timecode


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

ser = serial.Serial(SERIAL_PORT, 57600)
def pullFromCurrentCost():
    ''' read line of XML from the CurrentCost meter. '''
    # For Current Cost XML details, see currentcost.com/cc128/xml.htm
    watts = None
    while watts == None:
        line = ser.readline()
        tree  = ET.XML( line )
        watts = tree.findtext("ch1/watts")
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
                                           "unit": {
                                                    "type"  : "conversionBasedUnits",
                                                    "label" : "watts",
                                                    "symbol": "W"}
                                           }
                                          ] 
                           })
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    request = urllib2.Request('http://api.pachube.com/v2/feeds/'+FEED, data=jsonData)
    request.add_header('X-PachubeApiKey', API_KEY)
    request.get_method = lambda: 'PUT'
    opener.open(request)


#########################################
#          MAIN                         #
#########################################

print "UNIX time \t watts"

while True:
    data = pullFromCurrentCost()
    print int(time.time()), "\t", data
    pushToPachube( data )
