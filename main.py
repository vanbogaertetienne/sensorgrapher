#!/bin/python

import fetcher
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.dates import MinuteLocator, HourLocator, DateFormatter, DayLocator
import numpy as np
from matplotlib.figure import Figure
from numpy import arange, pi, random, linspace
import matplotlib.cm as cm

class MyWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
	self.set_border_width(3)
	self.sensorID = 0
	self.sensorInterval = 120
	self.sensorLimit = 1

        headerBar = Gtk.HeaderBar()
	headerBar.set_show_close_button(True)
	headerBar.props.title = "Sensor Grapher"
	self.set_titlebar(headerBar)

	self.notebook = Gtk.Notebook()
	self.notebook.set_tab_pos(0)
	self.notebook.connect("switch-page", self.onNotebookChanged)
	self.add(self.notebook)

	self.page1 = Gtk.Grid()
	self.page1.set_border_width(10)
	self.page1.set_column_spacing(20)
	self.page1.set_row_spacing(20)
        
	sensors = Gtk.ListStore(int, str, int)

        sensorDataRendererText = Gtk.CellRendererText()
        sensorData = fetcher.sensors()
	sensorData.update()
	count = sensorData.count()
	for sensorNumber in range(0, sensorData.count()):
	    sensorDescription = sensorData.sensorDescription(sensorNumber)
	    sensorID = sensorData.sensorID(sensorNumber)
	    sensors.append([sensorNumber, sensorDescription, sensorID])
	self.sensorCombo = Gtk.ComboBox.new_with_model(sensors)
	self.sensorCombo.pack_start(sensorDataRendererText, True)
	self.sensorCombo.add_attribute(sensorDataRendererText, "text", 1)
	self.sensorCombo.connect("changed", self.onComboChanged)
	self.sensorCombo.set_id_column(2)
	self.sensorCombo.set_active(0)
	self.page1.attach(Gtk.Label('Sensors'), 0, 0, 1, 1)
	self.page1.attach(self.sensorCombo, 1, 0, 1, 1)

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
	self.page1.attach(Gtk.Label('Sensor Data Interval'), 0, 1, 1, 1)
	self.page1.attach(self.sensorIntervalCombo, 1, 1, 1, 1)

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
        self.page1.attach(Gtk.Label('Limit Sensor Data'), 0, 2, 1, 1)
        self.page1.attach(self.sensorLimitCombo, 1, 2, 1, 1)
	
	self.notebook.append_page(self.page1, Gtk.Label('Sensors'))

	self.page2 = Gtk.Box()
	self.page2.set_border_width(10)
	self.notebook.append_page(self.page2, Gtk.Label('Graph'))
    
    def onComboChanged(self, combo):
	try:
	    sensorIter = self.sensorCombo.get_active_iter()
	    if sensorIter == None:
	        return
	    sensorModel = self.sensorCombo.get_model()
	    self.sensorID = sensorModel[sensorIter][2]
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
	
    def onNotebookChanged(self, notebook, page, page_num):
       	if page_num != 1:
	    return
	self.onComboChanged(self.sensorIntervalCombo)
        sensor = fetcher.sensorData(self.sensorID)
	sensor.setUpdateInterval(self.sensorInterval)
	sensor.setLimit(self.sensorLimit)
        sensor.update()

	width = self.page2.get_allocation().width
	height = self.page2.get_allocation().height

        sensorTimestamps = sensor.graphData()[0]
	sensorData = sensor.graphData()[1]

	try:
	    self.fig
	except:
	    self.fig = Figure()
	try:
	    self.ax
	except:
	    self.ax = self.fig.add_subplot(111)
	else:
	    self.ax.cla()
        
	self.ax.plot_date(sensorTimestamps, sensorData, '-')

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
	    self.sw.add_with_viewport(self.canvas)
	self.fig.canvas.draw()

win = MyWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
win.maximize()
Gtk.main()
