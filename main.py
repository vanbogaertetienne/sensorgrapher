#!/bin/python

import fetcher
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio
from matplotlib.dates import MinuteLocator, HourLocator, DateFormatter, DayLocator
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas
from matplotlib.dates import MinuteLocator, HourLocator, DateFormatter, DayLocator
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patches as mpatches
from numpy import arange, pi, random, linspace
import threading

class MyWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
	self.set_border_width(3)
	self.sensor1DBID = 0
	self.sensor2DBID = 0
	self.sensor1UIID = 0
	self.sensor2UIID = 0
	self.sensorInterval = 120
	self.sensorLimit = 1

        headerBar = Gtk.HeaderBar()
	headerBar.set_show_close_button(True)
	headerBar.props.title = "Sensor Grapher"
	self.set_titlebar(headerBar)

	refreshButton = Gtk.Button()
	refreshIcon = Gio.ThemedIcon(name="mail-send-receive-symbolic")
	refreshImage = Gtk.Image.new_from_gicon(refreshIcon, Gtk.IconSize.BUTTON)
	refreshButton.add(refreshImage)
	refreshButton.connect("clicked", self.onRefreshClicked)
	headerBar.pack_end(refreshButton)

	self.notebook = Gtk.Notebook()
	self.notebook.set_tab_pos(0)
	self.notebook.connect("switch-page", self.onNotebookChanged)
	self.add(self.notebook)

	self.page1 = Gtk.Grid()
	self.page1.set_border_width(10)
	self.page1.set_column_spacing(20)
	self.page1.set_row_spacing(20)

	self.page1.attach(Gtk.Label('Minimum date available'), 2, 0, 1, 1)
	self.page1.attach(Gtk.Label('Maximum date available'), 3, 0, 1, 1)
        
	sensors1 = Gtk.ListStore(int, str, int)
	sensors2 = Gtk.ListStore(int, str, int)

        sensor1DataRendererText = Gtk.CellRendererText()
        sensor1Data = fetcher.sensors()
	sensor1Data.update()
	count = sensor1Data.count()
	for sensor1Number in range(0, sensor1Data.count()):
	    sensor1Description = sensor1Data.sensorDescription(sensor1Number)
	    sensor1ID = sensor1Data.sensorID(sensor1Number)
	    sensors1.append([sensor1Number, sensor1Description, sensor1ID])
	self.sensor1Combo = Gtk.ComboBox.new_with_model(sensors1)
	self.sensor1Combo.pack_start(sensor1DataRendererText, True)
	self.sensor1Combo.add_attribute(sensor1DataRendererText, "text", 1)
	self.sensor1Combo.connect("changed", self.onComboChanged)
	self.sensor1Combo.set_id_column(2)
	self.sensor1Combo.set_active(0)
	self.page1.attach(Gtk.Label('Sensor 1'), 0, 1, 1, 1)
	self.page1.attach(self.sensor1Combo, 1, 1, 1, 1)
	self.sensor1MinDate = Gtk.Label('')
	self.sensor1MaxDate = Gtk.Label('')
	self.page1.attach(self.sensor1MinDate, 2, 1, 1, 1)
	self.page1.attach(self.sensor1MaxDate, 3, 1, 1, 1)

	sensor2DataRendererText = Gtk.CellRendererText()
        sensor2Data = fetcher.sensors()
	sensor2Data.update()
	count = sensor2Data.count()
	for sensor2Number in range(0, sensor2Data.count()):
	    sensor2Description = sensor2Data.sensorDescription(sensor2Number)
	    sensor2ID = sensor2Data.sensorID(sensor2Number)
	    sensors2.append([sensor2Number, sensor2Description, sensor2ID])
	self.sensor2Combo = Gtk.ComboBox.new_with_model(sensors2)
	self.sensor2Combo.pack_start(sensor2DataRendererText, True)
	self.sensor2Combo.add_attribute(sensor2DataRendererText, "text", 1)
	self.sensor2Combo.connect("changed", self.onComboChanged)
	self.sensor2Combo.set_id_column(2)
	self.sensor2Combo.set_active(0)
	self.page1.attach(Gtk.Label('Sensor 2'), 0, 2, 1, 1)
	self.page1.attach(self.sensor2Combo, 1, 2, 1, 1)
	self.sensor2MinDate = Gtk.Label('')
	self.sensor2MaxDate = Gtk.Label('')
	self.page1.attach(self.sensor2MinDate, 2, 2, 1, 1)
	self.page1.attach(self.sensor2MaxDate, 3, 2, 1, 1)

	sensorIntervalRendererText = Gtk.CellRendererText()
	sensorInterval = Gtk.ListStore(int, str)
	sensorInterval.append([120, '2 minutes'])
	sensorInterval.append([300, '5 minutes'])
	sensorInterval.append([600, '10 minutes'])
	sensorInterval.append([900, '15 minutes'])
	sensorInterval.append([1200, '20 minutes'])
	sensorInterval.append([1800, '30 minutes'])
	sensorInterval.append([2700, '45 minutes'])
	sensorInterval.append([3600, '60 minutes'])
	self.sensorIntervalCombo = Gtk.ComboBox.new_with_model(sensorInterval)
	self.sensorIntervalCombo.pack_start(sensorIntervalRendererText, True)
	self.sensorIntervalCombo.add_attribute(sensorIntervalRendererText, "text", 1)
	self.sensorIntervalCombo.connect("changed", self.onComboChanged)
	self.sensorIntervalCombo.set_active(3)
	self.page1.attach(Gtk.Label('Sensor Data Interval'), 0, 3, 1, 1)
	self.page1.attach(self.sensorIntervalCombo, 1, 3, 1, 1)

        sensorLimitRendererText = Gtk.CellRendererText()
        sensorLimit = Gtk.ListStore(int, str)
        sensorLimit.append([1, '1 Day'])
        sensorLimit.append([2, '2 Days'])
        sensorLimit.append([3, '3 Days'])
        sensorLimit.append([5, '5 Days'])
	sensorLimit.append([7, '1 Week'])
        self.sensorLimitCombo = Gtk.ComboBox.new_with_model(sensorLimit)
        self.sensorLimitCombo.pack_start(sensorLimitRendererText, True)
        self.sensorLimitCombo.add_attribute(sensorLimitRendererText, "text", 1)
        self.sensorLimitCombo.connect("changed", self.onComboChanged)
        self.sensorLimitCombo.set_active(0)
        self.page1.attach(Gtk.Label('Limit Sensor Data'), 0, 4, 1, 1)
        self.page1.attach(self.sensorLimitCombo, 1, 4, 1, 1)

	
	self.notebook.append_page(self.page1, Gtk.Label('Sensors'))

	self.page2 = Gtk.Box()
	self.page2.set_border_width(10)
	self.notebook.append_page(self.page2, Gtk.Label('Graph'))
    
    def onComboChanged(self, combo):
        sensorData = fetcher.sensors()
	sensorData.update()

	try:
	    sensorIter = self.sensor1Combo.get_active_iter()
	    if sensorIter == None:
	        return
	    sensor1Model = self.sensor1Combo.get_model()
	    self.sensor1DBID = sensor1Model[sensorIter][2]
	    self.sensor1UIID = sensor1Model[sensorIter][0]

	    self.sensor1MinDate.set_label(sensorData.sensorMinTimestamp(self.sensor1UIID))
	    self.sensor1MaxDate.set_label(sensorData.sensorMaxTimestamp(self.sensor1UIID))
	except:
	    return
        
	try:
	    sensorIter = self.sensor2Combo.get_active_iter()
	    if sensorIter == None:
	        return
	    sensor2Model = self.sensor2Combo.get_model()
	    self.sensor2DBID = sensor2Model[sensorIter][2]
	    self.sensor2UIID = sensor2Model[sensorIter][0]
	    
	    self.sensor2MinDate.set_label(sensorData.sensorMinTimestamp(self.sensor2UIID))
	    self.sensor2MaxDate.set_label(sensorData.sensorMaxTimestamp(self.sensor2UIID))
	except:
	    return

        try:
	    sensorIntervalIter = self.sensorIntervalCombo.get_active_iter()
	    if sensorIntervalIter == None:
	        return
	    sensorIntervalModel = self.sensorIntervalCombo.get_model()
	    self.sensorInterval = sensorIntervalModel[sensorIntervalIter][0]
	except:
	    return

        try:
	    sensorLimitIter = self.sensorLimitCombo.get_active_iter()
	    if sensorLimitIter == None:
	        return
	    sensorLimitModel = self.sensorLimitCombo.get_model()
	    self.sensorLimit = sensorLimitModel[sensorLimitIter][0]
	except:
	    return

    def onRefreshClicked(self, button):
        self.refresh()

    def refresh(self):
        self.onNotebookChanged(self.notebook, self.page2, 1)

    def onNotebookChanged(self, notebook, page, page_num):
       	if page_num != 1:
	    return
	    
	sensors = fetcher.sensors()
        sensors.update()

	self.onComboChanged(self.sensorIntervalCombo)
        sensor1 = fetcher.sensorData(self.sensor1DBID)
	sensor1.setUpdateInterval(self.sensorInterval)
	sensor1.setLimit(self.sensorLimit)
        sensor1.update()

        sensor2 = fetcher.sensorData(self.sensor2DBID)
	sensor2.setUpdateInterval(self.sensorInterval)
	sensor2.setLimit(self.sensorLimit)
        sensor2.update()

	width = self.page2.get_allocation().width
	height = self.page2.get_allocation().height

        sensor1Timestamps = sensor1.graphData()[0]
	sensor1Data = sensor1.graphData()[1]
	sensor2Timestamps = sensor2.graphData()[0]
	sensor2Data = sensor2.graphData()[1]

	try:
	    self.fig
	except:
	    self.fig = Figure()
	try:
	    self.ax1
	except:
	    self.ax1 = self.fig.add_subplot(111)
	else:
	    self.ax1.cla()
	try:
            self.ax2
        except:
            self.ax2 = self.ax1.twinx()
        else:
            self.ax2.cla()

	print 'Sensor1ID = {}, sensor2ID = {}'.format(self.sensor1DBID, self.sensor2DBID)
        
        bluelabel = '{} ({})'.format(sensors.sensorDescription(self.sensor1UIID), sensors.sensorUnit(self.sensor1UIID))
        redlabel  = '{} ({})'.format(sensors.sensorDescription(self.sensor2UIID), sensors.sensorUnit(self.sensor2UIID))
        
	blueplt = self.ax1.plot_date(sensor1Timestamps, sensor1Data, '-', label=bluelabel)
        redplt = self.ax2.plot_date(sensor2Timestamps, sensor2Data, 'r-', label=redlabel)

	plt.show()
	plt.pause(0.0001)
	try:
	    self.sw
	except:
            self.sw = Gtk.ScrolledWindow()
	    self.page2.pack_start(self.sw, True, True, 0)

        try:
	    self.canvas
	except:
	    self.canvas = FigureCanvas(self.fig)
	    self.sw.add_with_viewport(self.canvas)
	self.fig.canvas.draw()
	threading.Timer(self.sensorInterval, self.refresh)

win = MyWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
win.maximize()
Gtk.main()
