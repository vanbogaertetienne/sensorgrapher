#!/bin/python

import json
import datetime
import urllib2
import matplotlib.pyplot as plt
from matplotlib.dates import MinuteLocator, HourLocator, DateFormatter, DayLocator
import numpy as np

class sensorData:
    _sensorID = 1
    _data = []
    _updateInterval = 300
    _graphScaling = 1
    _limit = 1

    def __init__(self, sensorID):
        self._sensorID = sensorID

    def update(self):
        url = 'https://vbnetwork.be/~etienne/temptrend/getValues.inc.php?auth=edison1&sensorID={}&interval={}&numdays={}'.format(self.sensorID(), self.updateInterval(), self.limit())
	jsonRequest = urllib2.urlopen(url)
	jsonText = jsonRequest.read()
	try:
            self._data = json.loads(jsonText)
	except  JSONDecodeError:
	    print "Oops! Could not decode the json file"

    def data(self):
        return self._data

    def sensorID(self):
        return self._sensorID

    def graphData(self):
        timestamps = list()
	data = list()
        for line in self.data():
	    i = 0
	    rowDateTime = datetime.datetime.strptime( line['timestamp'], '%Y-%m-%d %H:%M:%S')
	    timestamps.append(rowDateTime)
	    data.append(np.asscalar(np.float64(line['sensorValue']))*self.graphScaling())
        return [timestamps, data]

    def setUpdateInterval(self, updateInterval):
        if ( updateInterval < 120 ):
	    self._updateInterval = 120
	    return
	if ( updateInterval > 3600 ):
	    self._updateInterval = 3600
	    return
	self._updateInterval = updateInterval

    def updateInterval(self):
        return self._updateInterval
    
    def setGraphScaling(self, graphScaling):
        if( graphScaling < 0 ):
	    return
	if( graphScaling > 500 ):
	    self._graphScaling = 500
	    return
	self._graphScaling = graphScaling

    def graphScaling(self):
        return self._graphScaling

    def setLimit(self, days):
        if ( days < 1 ):
            return
        self._limit = days

    def limit( self ):
        return self._limit

class sensors:
    _data = list()

    def update(self):
        url = "https://vbnetwork.be/~etienne/temptrend/getSensors.inc.php?auth=edison1"
	jsonRequest = urllib2.urlopen(url)
	jsonText = jsonRequest.read()
	try:
            self._data = json.loads(jsonText)
	except  JSONDecodeError:
	    print "Oops! Could not decode the json file"
	
    def count(self):
        return len(self._data)

    def sensorID(self, sensorID):
        if ( isinstance( sensorID, (int, long) ) ):
	    return int(self._data[sensorID]['id'])

    def sensorUnit(self, sensorID):
        if ( isinstance( sensorID, (int, long) ) ):
	    return self._data[sensorID]['unit']

    def sensorDescription(self, sensorID):
        if ( isinstance( sensorID, (int, long) ) ):
	    return self._data[sensorID]['description']
    
    def sensorUnitDescription(self, sensorID):
        if ( isinstance( sensorID, (int, long) ) ):
	    return self._data[sensorID]['unitdescription']
    
    def sensorMaxTimestamp( self, sensorID):
    	if ( isinstance( sensorID, (int, long) ) ):
	    return self._data[sensorID]['maxtime']

    def sensorMinTimestamp( self, sensorID):
        if ( isinstance( sensorID, (int, long) ) ):
	    return self._data[sensorID]['mintime']
