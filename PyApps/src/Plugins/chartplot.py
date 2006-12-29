#!/usr/bin/env python

#
# Copyright (C) 2007
# ASTRON (Netherlands Foundation for Research in Astronomy)
# and The MeqTree Foundation
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

# This is a python translation of the ACSIS chartplt.cc code

import sys
from qt import *
try:
  from Qwt4 import *
except:
  from qwt import *
from numarray import *
import maincontrol
import openzoom
import zoomwin
import random

class ChartPlot(QWidget):

  def __init__(self, num_curves=None,parent=None, name=None):
    """ Collects information about timing from setup_parameters dict.
        Resizes and initialises all the variables.  
        creates bottom frame and the chart plot
        Does all the connections
    """
    QWidget.__init__(self, parent, name)

    self.setMouseTracking(True)
    #Constant strings
    self._zoomInfo = "Zoom: Press mouse button and drag"
    self._cursorInfo = "Cursor Pos: Press middle mouse button in plot region"

    self._auto_offset = True
    self._offset = -10000
    self._highest_value = -10000
    self._lowest_value = 10000
    self._do_fixed_scale = False

    #Create the plot widget
    self._plotter = QwtPlot(self)
    self._plotter_has_curve = False
    self._plotter.setAxisTitle(QwtPlot.yLeft, "Signal (Relative Scale)")
    # turn off grid
    self._plotter.enableGridX(False)
    self._plotter.enableGridY(False)

    # turn off axis
    self._plotter.enableAxis(QwtPlot.xBottom, False)
    
    #Set the background color
    self._plotter.setCanvasBackground(Qt.black)
    
    #Legend
    self._plotter.enableLegend(False)
    self._plotter.enableOutline(True)
    self._plotter.setOutlinePen(QPen(Qt.green))

    #Create the bottom frame 
    self._ControlFrame = maincontrol.MainControl(self)
    self._ControlFrame.setFrameStyle(QFrame.Panel|QFrame.Raised)
    self._ControlFrame.setLineWidth(2)

  # we seem to need a layout for PyQt
    self.vbox_left = QVBoxLayout( self )
    self.vbox_left.setSpacing(10)
    self.box1 = QHBoxLayout( self.vbox_left )
    self.box1.addWidget(self._plotter)
    self.box2 = QHBoxLayout(self.vbox_left)
    self.box2.addWidget(self._ControlFrame)
    
    #Number of curves/beams
    if not num_curves is None:
      self._nbcrv = num_curves
      # make sure _nbcrv is a multiple of four
      nbcrv_bin = 4
      divis = self._nbcrv / nbcrv_bin
      if divis * nbcrv_bin < self._nbcrv:
        divis = divis + 1
        self._nbcrv = divis * nbcrv_bin
    else:
      self._nbcrv = 16

    #Initialization of the size of the arrays to put the curve in
    self._ArraySize = 50
    self._DispArraySize = 50
    self._x1 = zeros((self._DispArraySize,), Float32)
    self._x2 = zeros((self._DispArraySize,), Float32)
    self._x3 = zeros((self._DispArraySize,), Float32)
    self._x4 = zeros((self._DispArraySize,), Float32)

    # layout parameter for x_axis offsets 
    self._x_displacement = 50

    for i in range(self._DispArraySize):
      self._x1[i] = float(i)
      self._x2[i] = self._DispArraySize + self._x_displacement +i
      self._x3[i] = 2 * (self._DispArraySize + self._x_displacement) + i
      self._x4[i] = 3 * (self._DispArraySize + self._x_displacement) + i


    # Initialize all the arrays containing the curve data 
    # code for this?

    self._closezoom = False
    self._mainpause = False
    
    #initialize the mainplot zoom variables
    self._d_zoomActive = self._d_zoom = False
	    
    #initialize zoomcount.  Count the number of zoom windows opened
    self._zoomcount = 0

    # set up pop up text
    font = QFont("Helvetica",10)
    self._popup_text = QLabel(self)
    self._popup_text.setFont(font)
    self._popup_text.setFrameStyle(QFrame.Box | QFrame.Plain)
    # start the text off hidden at 0,0
    self._popup_text.hide()
    self._popup_text.setGeometry(0,0,160,48)

    # timer to allow redisplay
    self._display_interval_ms = 1000
    self._display_refresh = QTimer(self)
    self._display_refresh.start(self._display_interval_ms)
    self._refresh_flag = True

    ########### Connections for Signals ############

    #Print
    self.connect(self._ControlFrame._btnPrint, SIGNAL("clicked()"), self.do_print)
    
    #Zoom
    self.connect(self._ControlFrame._btnZoom, SIGNAL("clicked()"), self.zoom)
    
    # Pause
    self.connect(self._ControlFrame._btnPause, SIGNAL("clicked()"), self.chartpltPaused)
    
    #Quit button
    self.connect(self._ControlFrame._btnQuit, SIGNAL("clicked()"), self.quit)

    # set scale
    self.connect(self._ControlFrame._btnSetScale, SIGNAL("clicked()"), self.change_scale_type)

    # set offset
    self.connect(self._ControlFrame._btnSetOffset, SIGNAL("clicked()"), self.change_offset_value)

    #get position where the mouse was pressed
    self.connect(self._plotter, SIGNAL("plotMousePressed(const QMouseEvent &)"),
        self.plotMousePressed)

    #Get position of the mouse released to zoom or to create a zoom window by clicking on the signal 
    self.connect(self._plotter, SIGNAL("plotMouseReleased(const QMouseEvent &)"),
        self.plotMouseReleased)

    # redisplay
    self.connect(self._display_refresh, SIGNAL("timeout()"), self.refresh_event)

    # construct plot / array storage structures etc
    self.createplot()
    

  def destruct_chartplot(self):
    """	turn off global mouse tracking
    """
    QApplication.setGlobalMouseTracking(False)	
    QWidget.setMouseTracking(False) 

			
  def createplot(self):
    """ Sets all the desired parameters for the chart plot
    """
    self._chart_data = {}
    self._updated_data = {}
    self._indexzoom = {}
    self._indexzoom = {}
    self._pause = {}
    self._Zoom = {}
    self._good_data = {}
    self._mrk = {}
    self._position = {}
    self._zoom_title = {}
    self._zoom_pen = {}
    self._main_pen = {}
    self._crv_key = {}
    for i in range (self._nbcrv):
        self._updated_data[i] = False
        self._indexzoom[i] = False
        self._pause[i] = False
        self._Zoom[i] = None
        self._good_data[i] = True
        self._mrk[i] = 0
        self._crv_key[i] = 0
        self._position[i] = ""
        self._zoom_title[i] = "Data for Chart " + str(i)
        self._zoom_pen[i] = Qt.yellow
        self._main_pen[i] = Qt.yellow

    	self._crv_key[i] = self._plotter.insertCurve("Chart " + str(i))
    	self._plotter.setCurvePen(self._crv_key[i], QPen(self._main_pen[i]))

        self._chart_data[i] = []

    # set flags for active curves
    if self._plotter_has_curve:
      self._plotter.removeCurves()

  def do_print(self):
    # taken from PyQwt Bode demo
    try:
      printer = QPrinter(QPrinter.HighResolution)
    except AttributeError:
      printer = QPrinter()
    printer.setOrientation(QPrinter.Landscape)
    printer.setColorMode(QPrinter.Color)
    printer.setOutputToFile(True)
    printer.setOutputFileName('bode-example-%s.ps' % qVersion())
    if printer.setup():
      filter = PrintFilter()
      if (QPrinter.GrayScale == printer.colorMode()):
        filter.setOptions(QwtPlotPrintFilter.PrintAll
                  & ~QwtPlotPrintFilter.PrintCanvasBackground)
      self.plot.print_(printer, filter)

  def zoom(self):
    """ if unzoom is clicked
        disable zooming and put zooming flag back to FALSE
        else 
        put zooming flag to opposite of what it was
        See value of d_zoom
        set according text on the zoom button
    """
    if self._d_zoomActive:
      self._plotter.setAxisAutoScale(QwtPlot.yLeft)
      self._plotter.setAxisAutoScale(QwtPlot.xBottom)
      self._plotter.replot()
      self._d_zoom = False
      self._d_zoomActive = False
    else:
      self._d_zoom = not self._d_zoom
      #Set right text on button and label depending on the value of d_zoom
      if self._d_zoom:
        self._ControlFrame._btnZoom.setText("Unzoom")
        self._ControlFrame._lblInfo.setText(self._zoomInfo)
      else:
        self._ControlFrame._btnZoom.setText("Zoom")
        self._ControlFrame._lblInfo.setText(self._cursorInfo)

  def infoDisplay(self):
    """ Display text under cursor in plot
        Figures out where the cursor is, generates the appropriate text, 
        and puts it on the screen.
    """
    closest_curve, distance, xVal, yVal, index = self._plotter.closestCurve(self._e_pos_x, self._e_pos_y)

    #get value of where the mouse was released
    p2x = self._plotter.invTransform(QwtPlot.xBottom, self._e_pos_x)

# determine 'actual' x-axis position
    ref_point=0
    if (p2x >= 0) and (p2x < self._ArraySize):
      ref_point = int(p2x)
    elif p2x >= self._ArraySize + self._x_displacement and p2x < (2*self._ArraySize) + self._x_displacement: 
      ref_point = int(p2x - self._ArraySize - self._x_displacement)
    elif p2x >= 2*(self._ArraySize + self._x_displacement) and p2x < (3*self._ArraySize)+(2*self._x_displacement):
      ref_point = int(p2x - (2*(self._ArraySize + self._x_displacement)))
    elif p2x >= 3*(self._ArraySize+self._x_displacement) and p2x < (4*self._ArraySize) + 3*self._x_displacement: 
      ref_point = int(p2x - (3*(self._ArraySize+self._x_displacement)))

    time_offset = ((ref_point) * 0.001 * self._data_interval_ms) + self._display_start_s

    ref_value = 0.0
    if (closest_curve-1 == 0 or closest_curve-1 == (_nbcrv/4) or  closest_curve-1 == (_nbcrv/2) or closest_curve-1 == (3*(_nbcrv/4))):
      ref_value = self._spec_grid_offset(ref_point,closest_curve)
    else:
      ref_value = self._spec_grid(ref_point,closest_curve)

    # lbl and lbl2 are used to compose text for the status bar and pop up display
    lbl2 = QString()
    lbl2.setNum(time_offset,'g',3)
    lbl = "Time = " + lbl2 + "s, Signal="
    lbl2.setNum(ref_value,'g',3)
    lbl += lbl2
    curve_num = QString()
    curve_num.setNum(closest_curve)
    popupmsg = QString()
    popupmsg = "Chart " + curve_num + "\n" + lbl + "\n" + self._position[closest_curve]
    self._popup_text.setText(popupmsg)
    if not self._popup_text.isVisible():
      self._popup_text.show()
    if ((self._popup_text.x() != self._e_pos_x + 30) or (self._popup_text.y() != self._e_pos_y + 30)):
      self._popup_text.move(self._e_pos_x + 30 ,self._e_pos_y + 30)
    # Sets value of the label
    
    lbl += ", " + self._position[closest_curve]
    self._ControlFrame._lblInfo.setText(lbl)

  def plotMousePressed(self, e):
    """ Gets position of the mouse on the chart plot
        puts the mouse where it goes on the plot
        Depending on the position of the zoom button
        if d_zoom
        draws a rectangle
        if not
        the mouse pointer appears as a cross
    """
    # store position
    self._p1 = e.pos()
    # update cursor pos display
    self._e_pos_x = e.pos().x()
    self._e_pos_y = e.pos().y()
    if e.button() == Qt.MidButton: 
      self.infoDisplay()
    if self._d_zoom and not self._d_zoomActive:
      self._plotter.setOutlineStyle(Qwt.Rect) 
    else:
      self._plotter.setOutlineStyle(Qwt.Cross)


  def closezoomfun(self):
    """ Set closezoom flag active to close all the zoom windows 
        once the user clicked
        the close_all_zoom button from the warning
        put closezoom to 1 and replot
    """
    self._closezoom = True
    self.ReplotZoom()

# close any zoom pop up windows
  def quit(self):
   for curve_no in range(self._nbcrv):
     if self._indexzoom[curve_no]:  
       if not self._Zoom[curve_no] is None:
         self._Zoom[curve_no].Closing()
   self.close()

  def ReplotZoom(self):
    """ If no zoom window opened, sets the flag back to 0
        Looks in the array to see which zooms are opened
        if the closezoom is set to 1
        Close the zoom
        set the flag in the array to 0
        removes 1 from the number of zoom opened
        else
        replot the zoom
    """

    #If no zoom window opened, sets the flag back to 0
    if self._zoomcount==0:
      self._closezoom = False
      
    #Looks in the array to see which zooms are opened
    for curve_no in range(self._nbcrv):
      if self._indexzoom[curve_no] and not self._Zoom[curve_no] is None:
        if self._closezoom:
          #Close the zoom
          self._Zoom[curve_no].close()
          #set the flag in the array to 0
          self._indexzoom[curve_no] = False
          #removes 1 from the number of zoom opened
          self._zoomcount = self._zoomcount - 1
        elif not self._pause[curve_no]:  #replot the zoom
          chart = array(self._chart_data[curve_no])
          self._Zoom[curve_no].update_plot(chart)
          self._Zoom[curve_no]._plotzoom.setMarkerLabel(self._mrk[curve_no], self._position[curve_no])
          self._Zoom[curve_no]._plotzoom.replot()

  def plotMouseReleased(self, e):
    """ If the zoom button is pressed 
        get the coordinates of the rectangle to zoom
        set the axis
        else
        if the offset is placed to its max value
        find to what curve the click corresponds
        call function to create the zoom in a new window
    """

    # some shortcuts
    axl= QwtPlot.yLeft
    axb= QwtPlot.xBottom
  
    #Check if we have to zoom in the chartplt
    if self._d_zoom and not self._d_zoomActive:
      if e.button() == Qt.LeftButton:
        self._d_zoomActive = True
        # Don't invert any scales which aren't inverted
        if e.pos().x() < self._p1.x():
          x1 =  e.pos().x()
          x2 = self._p1.x()
        else:
          x2 =  e.pos().x()
          x1 = self._p1.x()
        if e.pos().y() < self._p1.y():
          y1 =  e.pos().y()
          y2 = self._p1.y()
        else:
          y2 =  e.pos().y()
          y1 = self._p1.y()
#       x1 = qwtMin(self._p1.x(), e.pos().x())
#       x2 = qwtMax(self._p1.x(), e.pos().x())
#       y1 = qwtMin(self._p1.y(), e.pos().y())
#       y2 = qwtMax(self._p1.y(), e.pos().y())

        # Set fixed scales
        self._plotter.setAxisScale(axl, self._plotter.invTransform(axl,y1), self._plotter.invTransform(axl,y2))
        self._plotter.setAxisScale(axb, self._plotter.invTransform(axb,x1), self._plotter.invTransform(axb,x2))
        self._plotter.replot()
        return
    # pop up a Zoom window
    elif e.button() == Qt.LeftButton:
      #get value of where the mouse was released
      closest_curve, distance, xVal, yVal, index = self._plotter.closestCurve(e.pos().x(), e.pos().y())
      self.zoomcrv(closest_curve-1)
    self._ControlFrame._lblInfo.setText(self._cursorInfo)
    self._plotter.setOutlineStyle(Qwt.Triangle)

  def zoomcrv(self, crv):
    """ If one tries to open a zoom of a curve that is already opened
        open a warning
        Increase the count of the number of curve opened
        Put a flag to indicate wich zoom is opened
        Open a zoompopup of the chosen curve
    """
    if self._indexzoom[crv]:
      if not self._Zoom[crv] is None:
        self._Zoom[crv].show()
#       self._Zoom[crv].raise()
      else:
        warning = openzoom.OpenZoom()
        warning.show()
    else:
      #To know how many zoom windows opened (so +1)
      self._zoomcount = self._zoomcount + 1
  
      #Get the color of the curve
      pen = QPen(self._plotter.curvePen(crv))
  
      #Put a flag to indicate wich zoom is open (for reploting)
      self._indexzoom[crv] = True

      #open a zoom of the selected curve
      PlotArraySize = self._x1.nelements()
      chart = array(self._chart_data[crv])
      self._Zoom[crv] = zoomwin.ZoomPopup(crv, self._x1, chart, pen, self)
      if self._good_data[crv]:
        self._Zoom[crv]._plotzoom.setCurvePen(1,QPen(Qt.yellow))
      else:
        self._Zoom[crv]._plotzoom.setCurvePen(1,QPen(Qt.red))
      self._pause[crv] = False
      self._mrk[crv] = self._Zoom[crv]._plotzoom.insertMarker()
      self._Zoom[crv]._plotzoom.setMarkerLineStyle(self._mrk[crv], QwtMarker.VLine)
      self._Zoom[crv]._plotzoom.setMarkerPos(self._mrk[crv], 10,20)
      self._Zoom[crv]._plotzoom.setMarkerLabelAlign(self._mrk[crv], Qt.AlignRight|Qt.AlignTop)
      self._Zoom[crv]._plotzoom.setMarkerPen(self._mrk[crv], QPen(self._zoom_pen[crv], 0, Qt.DashDotLine))
      self._Zoom[crv]._plotzoom.setMarkerLinePen(self._mrk[crv], QPen(Qt.black, 0, Qt.DashDotLine))
      self._Zoom[crv]._plotzoom.setMarkerFont(self._mrk[crv], QFont("Helvetica", 10, QFont.Bold))
      zoom_plot_label = "Sequence (oldest to most recent)"
#     self._Zoom[crv].setLabelText(zoom_plot_label)
      self._Zoom[crv]._plotzoom.setAxisTitle(QwtPlot.xBottom, zoom_plot_label)
      self._Zoom[crv]._plotzoom.setAxisTitle(QwtPlot.yLeft, "Signal Value")
      self.connect(self._Zoom[crv], PYSIGNAL("winclosed"), self.myindex)
      self.connect(self._Zoom[crv], PYSIGNAL("winpaused"), self.zoomPaused)

# def resizeEvent(self, e):
#   """ When the chartplot window gets resized, everything inside follows
#       Get the size of the whole rectangle
#       Set the sizes for the bottom frame
#   """
#(I) e (QResizeEvent) Event sent by resizing the window
#   rect = QRect(0, 0, e.size().width(), e.size().height()-50)
#   self._plotter.setGeometry(rect)
#   self._ControlFrame.setGeometry(0, rect.bottom() + 1, rect.width(), 50)


  def set_offset(self,parameters=None):
    """ Update the display offset.
    """
    if not parameters is None:
      if parameters.has_key("default_offset"):
        self._offset = parameters.get("default_offset")
        if self._offset < 0.0:
          self._auto_offset = True
          self._offset = -10000
          self._highest_value = -10000
          self._lowest_value = 10000
        else:
          self._auto_offset = False

  def ChartControlData(self):
    """ Resize array if no zoom windows are open.
    """
    #Works if no zoom windows are open
    if self._zoomcount == 0:
      resizex(self._ArraySize)
    else:
      warning = zoomwarn(self)
      warning.set_warning("All zoom windows should be closed\nto perform action.")
      warning.show() 

  def resizex(self, size):
    """ Get the size the arrays should have
        reinitialize the arrays
    """
      
    for i in range(self._nbcrv):
      if self._indexzoom[i] and not self._Zoom[i] is None:
        self._Zoom[i].resize_x_axis(self._DispArraySize)
    # y data with offset for plotting on the main display
    self._spec_grid_offset.resize(self._DispArraySize, self._nbcrv+1)
    self._spec_grid_offset = 0
    self._spec_ptr.resize(self._nbcrv+1)
    for i in range(self._nbcrv):
      self._spec_ptr[i] = dtemp + self._DispArraySize * i 

    # the y values for zoom pop up windows without the offset
    self._spec_grid.resize(self._DispArraySize,self._nbcrv+1)
    self._spec_grid = 0
    self._spec_ptr_actual.resize(self._nbcrv+1)
    for i in range(self._nbcrv):
      self._spec_ptr_actual[i] = dtemp + self._DispArraySize * i 

  def zoomCountmin(self):
    """ Reduces the count of zoom windows opened
    """
    self._zoomcount = self._zoomcount - 1

  def zoomPaused(self, crvtemp):
    if self._pause[crvtemp] == 0:
      self._Zoom[crvtemp]._ControlFrame._btnPause.setText("Resume")
    else:
      self._Zoom[crvtemp]._ControlFrame._btnPause.setText("Pause")
    self._pause[crvtemp] = not self._pause[crvtemp]


  def chartpltPaused(self):
    if not self._mainpause:
      self._ControlFrame._btnPause.setText("Resume")
      self._mainpause = True
    else:
      self._ControlFrame._btnPause.setText("Pause")
      self._mainpause = False

  def myindex(self, crvtemp):
    """ Sets the indexzoom flag of the curve that just closed to False
    """
    self._indexzoom[crvtemp] = False
    self._Zoom[crvtemp].exec_close()

  def updateEvent(self, channel, new_chart_val, q_pos_str):
    """ Update the curve data for the given channel
    """
    # in updateEvent, channel goes from 0 to _nbcrv - 1
    # ---
    # if necessary, first remove old data from front of queue
    # add new data to end of queue
    if len(self._chart_data[channel]) > self._DispArraySize-1:
      differ = len(self._chart_data[channel]) - (self._DispArraySize-1)
      for i in range(differ):
        del self._chart_data[channel][0]
    self._chart_data[channel].append(new_chart_val)
    self._updated_data[channel] = True
    
    # take care of position string
    self._position[channel] = q_pos_str

  def set_data_flag(self, channel, data_flag):
    if data_flag != self._good_data[channel]:
      self._good_data[channel] = data_flag
       # we have bad data if data_flag is False
      if not data_flag:
        self._plotter.setCurvePen(self._crv_key[channel], QPen(Qt.red))
        if self._indexzoom[channel]:
          self._Zoom[channel]._plotzoom.setCurvePen(1,QPen(Qt.red))
        else: 
          self._plotter.setCurvePen(self._crv_key[channel], QPen(Qt.yellow))
          if self._indexzoom[channel]:
            self._Zoom[channel]._plotzoom.setCurvePen(1,QPen(Qt.yellow))

  def change_scale_type(self):
    # click means change to fixed scale
    if self._do_fixed_scale:
      self._do_fixed_scale = False
      self._ControlFrame._btnSetScale.setText("Fixed Scale")
      self._plotter.setAxisAutoScale(QwtPlot.yLeft)
    else: 
      self._do_fixed_scale = True
      self._ControlFrame._btnSetScale.setText("Auto Scale")

      # find current data min and max
      scale_max = self._spec_grid_offset.max()
      scale_min = self._spec_grid_offset.min()

      scale_diff = scale_max - scale_min
      scale_max = scale_max + 0.2 * scale_diff
      scale_min = scale_min - 0.2 * scale_diff 

      AxisParms = ScaleSelector(scale_max, scale_min, self)
      self.connect(AxisParms, PYSIGNAL("scale_values"), self.set_scale_values)
      self.connect(AxisParms, PYSIGNAL("cancel"), self.cancel_scale_request)

  def change_offset_value(self):
    OffSetParam = OffsetSelector(self)
    self.connect(OffSetParam, PYSIGNAL("offset_value"), self.set_offset_value)
    self.connect(OffSetParam, PYSIGNAL("cancel_offset"), self.cancel_offset_request)

  def set_scale_values(self, max_value, min_value):
    if self._do_fixed_scale:
      self._plotter.setAxisScale(QwtPlot.yLeft, min_value, max_value)
      self._plotter.replot()

  def cancel_scale_request(self):
    if self._do_fixed_scale: 
      self._do_fixed_scale = False
      self._ControlFrame._btnSetScale.setText("Fixed Scale")
      self._plotter.setAxisAutoScale(QwtPlot.yLeft)

  def set_offset_value(self, offset_value):
    self._offset = offset_value
    if self._offset < 0.0:
      self._auto_offset = True
      self._offset = -10000
      self._highest_value = -10000
      self._lowest_value = 10000
    else: 
      self._auto_offset = False

  def refresh_event(self):
    """ redisplay plot and zoom
        if refresh flag is true (new data exists)
        call replots
        set refresh flag False
    """

    # -----------
    # update data
    # -----------
    for channel in range(self._nbcrv):
      if self._updated_data[channel]:
        chart = array(self._chart_data[channel])
        index = channel+1
        #Set the values and size with the curves
        if index >= 1 and index <= self._nbcrv/4:
          temp_x = self._x1
        elif index >= (self._nbcrv/4)+1 and index <= self._nbcrv/2:
          temp_x = self._x2
        elif index >= (self._nbcrv/2)+1 and index <= 3*(self._nbcrv/4):
          temp_x = self._x3
        elif index >= (3*(_nbcrv/4))+1 and index <= self._nbcrv:
          temp_x = self._x4
	
        tmp_max = chart.max()
        tmp_min = chart.min()
        # check if we break any highest or lowest limits
        # this is important for offset reasons.
        if tmp_max > self._highest_value:
          self._highest_value = tmp_max
        if tmp_min < self._lowest_value:
          self._lowest_value = tmp_min
        #Get the maximal value of the chart coming in
        self._new_value = self._highest_value - self._lowest_value
        #If the max value of the chart is higher than the set one
        if self._auto_offset and self._offset < self._new_value:
        #set the max value of the offset
          self._offset = 1.1 * self._new_value
        temp_off = (channel % (self._nbcrv/4)) * self._offset
        self._plotter.setCurveData(self._crv_key[channel], temp_x , chart+temp_off)
	 
# need to update any corresponding Zoom window     
#        self._Zoom[channel].resize_x_axis(len(self._chart_data[channel]))
        # Wait that all the channels are modified before 
        # plotting with the new x array
        if not self._mainpause:
          self._refresh_flag = True
	
        #Put the integration number back to 1 for next time
        self._updated_data[channel] = False
      # --------------
      # refresh screen
      # --------------
      if self._refresh_flag: 
        self._plotter.replot()
        self.ReplotZoom()
      self._refresh_flag = False


  def cancel_offset_request(self):
    return        # do nothing

  def start_test_timer(self, time):
    # stuff for tests
    self.counter = 1.0
    self.startTimer(time)

  def timerEvent(self, e):
    self.counter = 1.0 + 1 * random.random()
    self.updateEvent(1, self.counter, 'xyz')
    self.counter = 1.0 + 1 * random.random()
    self.updateEvent(3, self.counter, 'xyz')
    self.counter = 1.0 + 1 * random.random()
    self.updateEvent(9, self.counter, 'xyz')
    return

def make():
    demo = ChartPlot()
    demo.show()
    demo.start_test_timer(500)
    return demo

def main(args):
    app = QApplication(args)
    demo = make()
    app.setMainWidget(demo)
    app.exec_loop()


# Admire
if __name__ == '__main__':
    main(sys.argv)

