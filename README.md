Python script for sending power data from a Current Cost
to Cosm (Pachube) and also to log data to a local file.  Can handle
multiple sensors (e.g. multiple Individual Appliance Monitors).

This requires my cosmSender module available from:
https://github.com/JackKelly/cosmSender

To use, you need to create a config.xml file in the following format:

```XML
<config>
  <apikey>YOUR PACHUBE API KEY</apikey>
  <feed>YOUR PACHUBE FEED ID</feed>
  <datastream>YOUR PACHUBE DATASTREAM</datastream>
  <serialport>THE SERIAL PORT TO WHICH YOUR CURRENT COST IS ATTACHED
  e.g. /dev/ttyUSB0</serialport>
  <filename>THE CSV DATAFILE TO OUTPUT TO (including path)</filename>
</config>
```

## Finding the correct serial port

Run a command like "dmesg | grep USB" and then look for a line
which reads something like 
"usb 2-1.2: pl2303 converter now attached to ttyUSB0".  Now
check that this is your Current Cost by running "cat /dev/ttyUSB0"
and you should see a line of XML dumped to the terminal
approximately once every six seconds (or faster if you have
multiple sensors).  Type CTRL+C to exit cat.
If this is your Current Cost then add
"/dev/ttyUSB0" to your confix.xml file.

If you're wondering why we're talking about a "serial port"
when the Current Cost appears to be connected via a USB
cable, the answer is that the USB cable has a little serial
port converter in it.


## Multiple sensors

Optionally, if you have multiple sensors connected to your CurrentCost
(for example if you're using Individual Appliance Monitors) then you
can provide the names for these appliances in sensorNames.csv
file. This is simply an ordered list of appliance names, separated by
a new line.  e.g.:

aggregate
tv
fridge
laptop


## Multiple instances of currentCostCosmTX

If updating one xively / cosm feed from two different programs or
devices you need to use different api keys or will get a 403 error.
