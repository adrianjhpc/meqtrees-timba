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
import zoomwin
import printfilter
import random

class ChartPlot(QWidget):

  menu_table = {
        'Reset zoomer': 200,
        'Close': 201,
        'Print': 202,
        'Fixed Scale': 203,
        'Offset Value': 204,
        'Change Vells': 205,
        'Show Channels': 206,
        'Clear Plot': 207,
        'Append': 208,
        'Complex Data': 209,
        'Amplitude': 210,
        'Phase': 211,
        'Real': 212,
        'Imaginary': 213,
        'Close Popups': 214,
        'Show Flags': 215,
        }


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
    self._ref_chan= 0
    self._offset = 0
    self._source = None
    self._max_range = -10000
    self._do_fixed_scale = False
    self._data_label = None
    self.info_marker = None
    self.show_channel_labels = True
    self._append_data = True
    self._plot_label = None
    self._complex_marker = None
    self._ignore_flagged_data = True

    #Create the plot widget
    self._y_title = "Value (Relative Scale)"
    self._x_title = "Time Sequence (Relative Scale)"
    self._plotter = QwtPlot(self)
    self._plotter.setAxisTitle(QwtPlot.yLeft, self._y_title)
    self._plotter.setAxisTitle(QwtPlot.xBottom, self._x_title)

    # set plotter fonts to same size as in display_image.py code
    font = QFont(QApplication.font());
    fi = QFontInfo(font);
    # and scale it down to 70%
    font.setPointSize(fi.pointSize()*0.7);
    # apply font to QwtPlot
    self._plotter.setTitleFont(font);
    for axis in range(0,4):
      self._plotter.setAxisFont(axis,font);
      self._plotter.setAxisTitleFont(axis,font);

    # turn off grid
    self._plotter.enableGridX(False)
    self._plotter.enableGridY(False)

    #Set the background color
    self._plotter.setCanvasBackground(Qt.white)
    
    #Legend
    self._plotter.enableLegend(False)
    self._plotter.enableOutline(True)
    self._plotter.setOutlinePen(QPen(Qt.green))

    # we seem to need a layout for PyQt
    self.vbox_left = QVBoxLayout( self )
    self.vbox_left.setSpacing(10)
    self.box1 = QHBoxLayout( self.vbox_left )
    self.box1.addWidget(self._plotter)

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
    self._ArraySize = 6
    self._x_displacement = self._ArraySize / 6 
    self._data_index = 0
    self.set_x_axis_sizes()

    # Initialize all the arrays containing the curve data 
    # code for this?

    self._closezoom = False
    self._mainpause = False
    
    #initialize the mainplot zoom variables
    self._d_zoomActive = self._d_zoom = False
    self._is_vector = False
    self.source_marker = None
	    
    #initialize zoomcount.  Count the number of zoom windows opened
    self._zoomcount = 0

    # set up pop up text
    font = QFont("Helvetica",10)
    self._popup_text = QLabel(self)
    self._popup_text.setFont(font)
    self._popup_text.setFrameStyle(QFrame.Box | QFrame.Plain)
    # start the text off hidden at 0,0
    self._popup_text.hide()

    # timer to allow redisplay
    self._display_interval_ms = 2000
    self._display_refresh = QTimer(self)
    self._display_refresh.start(self._display_interval_ms)
    self._refresh_flag = True
    self._complex_type = "Amplitude"
    self._amplitude = True
    self._phase = False
    self._real = False
    self._imaginary = False


    # create context menu
    self._mainwin = parent and parent.topLevelWidget()
    self._menu = QPopupMenu(self._mainwin)
    toggle_id = self.menu_table['Close']
    self._menu.insertItem("Close Window", toggle_id)
    self._menu.setItemVisible(toggle_id, False)
    toggle_id = self.menu_table['Reset zoomer']
    self._menu.insertItem("Reset zoomer", toggle_id)
    self._menu.setItemVisible(toggle_id, False)
    toggle_id = self.menu_table['Print']
    self._menu.insertItem("Print", toggle_id)
    toggle_id = self.menu_table['Clear Plot']
    self._menu.insertItem("Clear Plot", toggle_id)
    toggle_id = self.menu_table['Close Popups']
    self._menu.insertItem("Close Popup Windows", toggle_id)
    self._menu.setItemVisible(toggle_id, False)
    toggle_id = self.menu_table['Show Flags']
    self._menu.insertItem("Show Flagged Data", toggle_id)
    toggle_id = self.menu_table['Fixed Scale']
    self._menu.insertItem("Fixed Scale", toggle_id)
    self._menu.setItemVisible(toggle_id, False)
    toggle_id = self.menu_table['Offset Value']
    self._menu.insertItem("Offset Value", toggle_id)
    self._menu.setItemVisible(toggle_id, False)
    toggle_id = self.menu_table['Show Channels']
    self._menu.insertItem("Hide Channel Markers", toggle_id)
    toggle_id = self.menu_table['Append']
    self._menu.insertItem("Replace Vector Data", toggle_id)

    self._complex_submenu = QPopupMenu(self._menu)
    toggle_id = self.menu_table['Amplitude']
    self._complex_submenu.insertItem("Amplitude",toggle_id)
    self._complex_submenu.setItemChecked(toggle_id, self._amplitude)
    toggle_id = self.menu_table['Phase']
    self._complex_submenu.insertItem("Phase (radians)",toggle_id)
    toggle_id = self.menu_table['Real']
    self._complex_submenu.insertItem("Real",toggle_id)
    toggle_id = self.menu_table['Imaginary']
    self._complex_submenu.insertItem("Imaginary",toggle_id)

    toggle_id = self.menu_table['Complex Data']
    self._menu.insertItem("Complex Data Selection  ", self._complex_submenu, toggle_id)
    self._menu.setItemVisible(toggle_id, False)

    self._vells_menu = None
    self._vells_menu_id = 0
    self._vells_keys = {}

    ########### Connections for Signals ############
    self.connect(self._menu,SIGNAL("activated(int)"),self.emit_menu_signal);
    self.connect(self._complex_submenu,SIGNAL("activated(int)"),self.emit_complex_selector);

    #get position where the mouse was pressed
    self.connect(self._plotter, SIGNAL("plotMousePressed(const QMouseEvent &)"),
        self.plotMousePressed)

    #Get position of the mouse released to zoom or to create a zoom window by clicking on the signal 
    self.connect(self._plotter, SIGNAL("plotMouseReleased(const QMouseEvent &)"),
        self.plotMouseReleased)
    self.connect(self._plotter, SIGNAL('plotMouseMoved(const QMouseEvent&)'),
                     self.plotMouseMoved)
    # redisplay
    self.connect(self._display_refresh, SIGNAL("timeout()"), self.refresh_event)

    # construct plot / array storage structures etc
    self.createplot(True)
    
  def setSource(self, source_string):
    self._source = source_string

  def set_x_axis_sizes(self):
    """ changes sizes and values of arrays used to store x-axis 
        values for plot
    """
    self._x1 = zeros((self._ArraySize,), Float32)
    self._x2 = zeros((self._ArraySize,), Float32)
    self._x3 = zeros((self._ArraySize,), Float32)
    self._x4 = zeros((self._ArraySize,), Float32)

    # layout parameter for x_axis offsets 
    if self._ArraySize > 6 * self._x_displacement:
      self._x_displacement = self._ArraySize / 6
    for i in range(self._ArraySize):
      self._x1[i] = float(i)
      self._x2[i] = self._ArraySize + self._x_displacement +i
      self._x3[i] = 2 * (self._ArraySize + self._x_displacement) + i
      self._x4[i] = 3 * (self._ArraySize + self._x_displacement) + i

  def emit_vells_selector(self,menuid):
    self.emit(PYSIGNAL("vells_selector"),(menuid,))

  def emit_menu_signal(self, menuid):
    """ callback to handle events from the context menu """
    self.emit(PYSIGNAL("menu_command"),(menuid,))

  def process_menu(self, menuid):
    """ callback to handle events from the context menu """
    if menuid < 0:
      return
    if menuid == self.menu_table['Reset zoomer']:
      self.reset_zoom()
      return True
    if menuid == self.menu_table['Close']:
      self.quit()
      return True
    if menuid == self.menu_table['Close Popups']:
      self.closezoomfun()
      return True
    if menuid == self.menu_table['Print']:
      self.do_print()
      return True
    if menuid == self.menu_table['Fixed Scale']:
      self.change_scale_type()
      return True
    if menuid == self.menu_table['Offset Value']:
      self.change_offset_value()
      return True
    if menuid == self.menu_table['Show Channels']:
      self.change_channel_display(menuid)
      return True
    if menuid == self.menu_table['Clear Plot']:
      self.clear_plot()
      return True
    if menuid == self.menu_table['Append']:
      if self._append_data:
        self._append_data = False
        self._menu.changeItem(menuid,'Append Vector Data')
      else:
        self._append_data = True
        self._menu.changeItem(menuid,'Replace Vector Data')
      self.clear_plot()
      return True
    if menuid == self.menu_table['Show Flags']:
      self.change_flag_parms(menuid)
      return True
    if menuid == self.menu_table['Complex Data']:
#     print 'in complex data callback'
      return True

  def change_flag_parms(self, menuid):
    if self._ignore_flagged_data:
      self._ignore_flagged_data = False
      self._menu.changeItem(menuid,'Hide Flagged Data')
    else:
      self._ignore_flagged_data = True
      self._menu.changeItem(menuid,'Show Flagged Data')
    self._do_fixed_scale = False
    self._auto_offset = True
    self._offset = 0
    self._max_range = -10000
    for channel in range(self._nbcrv):
      self._updated_data[channel] = True
      self._start_offset_test[channel][self._data_index] = 0
    self.reset_zoom()
    self.refresh_event()

  def emit_complex_selector(self, menuid):
    """ callback to handle events from the context menu """
    self.emit(PYSIGNAL("complex_selector_command"),(menuid,))

  def process_complex_selector(self, menuid):
    """ callback to handle events from the complex data selection
        sub-context menu 
    """
    if menuid < 0:
      return
    self._amplitude = False
    self._phase = False
    self._real = False
    self._imaginary = False

    toggle_id = self.menu_table['Amplitude']
    self._complex_submenu.setItemChecked(toggle_id, self._amplitude)
    toggle_id = self.menu_table['Phase']
    self._complex_submenu.setItemChecked(toggle_id, self._phase)
    toggle_id = self.menu_table['Real']
    self._complex_submenu.setItemChecked(toggle_id, self._real)
    toggle_id = self.menu_table['Imaginary']
    self._complex_submenu.setItemChecked(toggle_id, self._imaginary)

    if menuid == self.menu_table['Amplitude']:
      self._amplitude = True
      toggle_id = self.menu_table['Amplitude']
      self._complex_submenu.setItemChecked(toggle_id, self._amplitude)
      self._plotter.setAxisTitle(QwtPlot.yLeft, "Amplitude (Relative Scale)")
      self._complex_type = "Amplitude"
    if menuid == self.menu_table['Phase']:
      self._phase = True
      toggle_id = self.menu_table['Phase']
      self._complex_submenu.setItemChecked(toggle_id, self._phase)
      self._plotter.setAxisTitle(QwtPlot.yLeft, "Phase (Relative Scale)")
      self._complex_type = "Phase"
    if menuid == self.menu_table['Real']:
      self._real = True
      toggle_id = self.menu_table['Real']
      self._complex_submenu.setItemChecked(toggle_id, self._real)
      self._plotter.setAxisTitle(QwtPlot.yLeft, "Real (Relative Scale)")
      self._complex_type = "Real"
    if menuid == self.menu_table['Imaginary']:
      self._imaginary = True
      toggle_id = self.menu_table['Imaginary']
      self._complex_submenu.setItemChecked(toggle_id, self._imaginary)
      self._plotter.setAxisTitle(QwtPlot.yLeft, "Imaginary (Relative Scale)")
      self._complex_type = "Imaginary"

    self._do_fixed_scale = False
    self._auto_offset = True
    self._offset = 0
    self._max_range = -10000
    for channel in range(self._nbcrv):
      self._updated_data[channel] = True
      self._start_offset_test[channel][self._data_index] = 0
    self.reset_zoom()
    self.refresh_event()
    return True

    
  def reset_zoom(self):
    """ resets data display so all data are visible """
    self._plotter.setAxisAutoScale(QwtPlot.yLeft)
    self._plotter.setAxisAutoScale(QwtPlot.xBottom)
    self._plotter.replot()
    toggle_id = self.menu_table['Reset zoomer']
    self._menu.setItemVisible(toggle_id, False)
    return

  def clear_plot(self):
    """ clear the plot of all displayed data """
    # first remove any markers
    for channel in range(self._nbcrv):
      if not self._source_marker[channel] is None:
        self._plotter.removeMarker(self._source_marker[channel]);
    # remove current curves
    self._plotter.removeCurves()
    self._plotter.replot()
    self._ArraySize = 6
    self._x_displacement = self._ArraySize / 6 
    self.set_x_axis_sizes()
    self.createplot()

  def setDataLabel(self, data_label):
    self._data_label = data_label
    title = self._data_label + " " + self._x_title
    self._plotter.setAxisTitle(QwtPlot.xBottom, title)

  def setPlotLabel(self, plot_label):
    self._plot_label = plot_label

  def destruct_chartplot(self):
    """	turn off global mouse tracking """
    QApplication.setGlobalMouseTracking(False)	
    QWidget.setMouseTracking(False) 
			
  def createplot(self,first_time=False):
    """ Sets all the desired parameters for the chart plot """
    if first_time:
      self._chart_data = {}
      self._flag_data = {}
      self._start_offset_test = {}
      self._updated_data = {}
      self._pause = {}
      self._mrk = {}
      self._position = {}
      self._Zoom = {}
      self._zoom_title = {}
      self._zoom_pen = {}
      self._main_pen = {}
      self._indexzoom = {}
      self._crv_key = {}
      self._source_marker = {}
      for i in range (self._nbcrv):
          self._updated_data[i] = False
          self._indexzoom[i] = False
          self._pause[i] = False
          self._Zoom[i] = None
          self._source_marker[i] = None
          self._mrk[i] = 0
          self._position[i] = ""
          self._zoom_title[i] = "Data for Chart " + str(i)
          self._zoom_pen[i] = Qt.yellow
          self._main_pen[i] = Qt.black
    	  self._crv_key[i] = self._plotter.insertCurve("Chart " + str(i))
    	  self._plotter.setCurvePen(self._crv_key[i], QPen(self._main_pen[i]))
          self._chart_data[i] = {}
          self._flag_data[i] = {}
          self._start_offset_test[i] = {}
    else:
      self._updated_data = {}
      self._pause = {}
      self._mrk = {}
      self._position = {}
      self._main_pen = {}
      self._crv_key = {}
      self._source_marker = {}
      for i in range (self._nbcrv):
          self._updated_data[i] = False
          self._pause[i] = False
          self._source_marker[i] = None
          self._mrk[i] = 0
          self._position[i] = ""
          self._main_pen[i] = Qt.black
    	  self._crv_key[i] = self._plotter.insertCurve("Chart " + str(i))
    	  self._plotter.setCurvePen(self._crv_key[i], QPen(self._main_pen[i]))
          self._chart_data[i] = {}
          self._flag_data[i] = {}
          self._start_offset_test[i] = {}

  def do_print(self):
    # taken from PyQwt Bode demo
    try:
      printer = QPrinter(QPrinter.HighResolution)
    except AttributeError:
      printer = QPrinter()
    printer.setOrientation(QPrinter.Landscape)
    printer.setColorMode(QPrinter.Color)
    printer.setOutputToFile(True)
    printer.setOutputFileName('screen_plot-%s.ps' % qVersion())
    if printer.setup():
      filter = printfilter.PrintFilter()
      if (QPrinter.GrayScale == printer.colorMode()):
        filter.setOptions(QwtPlotPrintFilter.PrintAll
                  & ~QwtPlotPrintFilter.PrintCanvasBackground)
      try:
        self._plotter.print_(printer, filter)
      except:
        try:
          self._plotter.printPlot(printer, filter)
        except:
          print ' printing unavailable'

  def infoDisplay(self):
    """ Display text under cursor in plot
        Figures out where the cursor is, generates the appropriate text, 
        and puts it on the screen.
    """
    closest_curve, distance, xVal, yVal, index = self._plotter.closestCurve(self.xpos, self.ypos)

    #get value of where the mouse was released
    p2x = self._plotter.invTransform(QwtPlot.xBottom, self.xpos)

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

    if self._phase:
      temp_off = ((closest_curve-1) % (self._nbcrv/4) + 0.5 ) * self._offset
    else:
      temp_off = ((closest_curve-1) % (self._nbcrv/4)) * self._offset
    ref_value = yVal - temp_off

    message = self.reportCoordinates(ref_point, ref_value, closest_curve-1)

# lbl and lbl2 are used to compose text for the status bar and pop up display
#   lbl2 = QString()
#   lbl2.setNum(ref_point,'g',3)
#   lbl = "Time = " + lbl2 + "s, Signal="
#   lbl2.setNum(ref_value,'g',3)
#   lbl += lbl2
#   curve_num = QString()
#   curve_num.setNum(closest_curve)
#   popupmsg = QString()
#   popupmsg = "Chart " + curve_num + "\n" + lbl + "\n" + self._position[closest_curve]

    self._popup_text.setText(message)
    self._popup_text.adjustSize()
    yhb = self._plotter.transform(QwtPlot.yLeft, self._plotter.axisScale(QwtPlot.yLeft).hBound())
    ylb = self._plotter.transform(QwtPlot.yLeft, self._plotter.axisScale(QwtPlot.yLeft).lBound())
    xhb = self._plotter.transform(QwtPlot.xBottom, self._plotter.axisScale(QwtPlot.xBottom).hBound())
    xlb = self._plotter.transform(QwtPlot.xBottom, self._plotter.axisScale(QwtPlot.xBottom).lBound())
    height = self._popup_text.height()
    if self.ypos + height > ylb:
      ymove = self.ypos - 1.5 * height
    else:
      ymove = self.ypos + 0.5 * height
    width = self._popup_text.width()
    if self.xpos + width > xhb:
      xmove = xhb - width
    else:
      xmove = self.xpos
    self._popup_text.move(xmove, ymove)
    if not self._popup_text.isVisible():
      self._popup_text.show()
    
  def plotMouseMoved(self, e):
    if self._popup_text.isVisible():
      self._popup_text.hide()
    return

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
          chart = array(self._chart_data[curve_no][self._data_index])
          flags = array(self._flag_data[curve_no][self._data_index])
          self._Zoom[curve_no].update_plot(chart,flags)
#         self._Zoom[curve_no]._plotter.setMarkerLabel(self._mrk[curve_no], self._position[curve_no])
          self._Zoom[curve_no]._plotter.replot()

    if self._closezoom:
      toggle_id = self.menu_table['Close Popups']
      self._menu.setItemVisible(toggle_id, False)

  def plotMousePressed(self, e):
      """ callback to handle MousePressed event """
      if Qt.MidButton == e.button():
        xPos = e.pos().x()
        yPos = e.pos().y()
# We get information about the qwt plot curve that is
# closest to the location of this mouse pressed event.
# We are interested in the nearest curve_number and the index, or
# sequence number of the nearest point in that curve.
        curve_number, distance, xVal, yVal, index = self._plotter.closestCurve(xPos, yPos)
      # pop up zoom curve
      elif Qt.LeftButton == e.button():
        self.xpos = e.pos().x()
        self.ypos = e.pos().y()
        self.infoDisplay()
        self._plotter.enableOutline(1)
        self._plotter.setOutlinePen(QPen(Qt.black))
        self._plotter.setOutlineStyle(Qwt.Rect)
      else:
        e.accept()
        self._menu.popup(e.globalPos());

    # onMousePressed()

  def plotMouseReleased(self, e):
      """ callback to handle MouseReleased event """
      if Qt.LeftButton == e.button():
        if self._popup_text.isVisible():
          self._popup_text.hide()
# assume a change of <= 2 screen pixels is just due to clicking
# left mouse button for no good reason
        if abs(self.xpos - e.pos().x()) > 2 and abs(self.ypos - e.pos().y()) > 2:
          self._plotter.setOutlineStyle(Qwt.Cross)

          xmin = min(self.xpos, e.pos().x())
          xmax = max(self.xpos, e.pos().x())
          ymin = min(self.ypos, e.pos().y())
          ymax = max(self.ypos, e.pos().y())
          xmin = self._plotter.invTransform(QwtPlot.xBottom, xmin)
          xmax = self._plotter.invTransform(QwtPlot.xBottom, xmax)
          ymin = self._plotter.invTransform(QwtPlot.yLeft, ymin)
          ymax = self._plotter.invTransform(QwtPlot.yLeft, ymax)
          self._plotter.enableOutline(0)
          self._plotter.setAxisScale(QwtPlot.xBottom, xmin, xmax)
          self._plotter.setAxisScale(QwtPlot.yLeft, ymin, ymax)
          self.xmin = xmin
          self.xmax = xmax
          self.ymin = ymin
          self.ymax = ymax
          self.axis_xmin = xmin
          self.axis_xmax = xmax
          self.axis_ymin = ymin
          self.axis_ymax = ymax
          toggle_id = self.menu_table['Reset zoomer']
          self._menu.setItemVisible(toggle_id, True)
          self._plotter.replot()
        else:
          self._plotter.replot()
      elif e.button() == Qt.MidButton:
        closest_curve, distance, xVal, yVal, index = self._plotter.closestCurve(e.pos().x(), e.pos().y())
        # pop up a zoom curve
        self.zoomcrv(closest_curve-1)
      self._plotter.setOutlineStyle(Qwt.Triangle)

    # onMouseReleased()

  def reportCoordinates(self, x, y, crv):
    """Format mouse coordinates as real world plot coordinates.
    """
    if not self._plot_label is None:
      plot_label = self._plot_label[crv+self._ref_chan] + ': '
    else:
      plot_label = str(crv+self._ref_chan) + ': '
    temp_str = "nearest x=%-.3g" % x
    temp_str1 = " y=%-.3g" % y
    message = plot_label + temp_str + temp_str1 
    return message
    # reportCoordinates()

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
        Message = "A zoom of this curve is already opened"
        zoom_message = QMessageBox("chartplot.py",
                       Message,
                       QMessageBox.Warning,
                       QMessageBox.Ok | QMessageBox.Default,
                       QMessageBox.NoButton,
                       QMessageBox.NoButton)
        zoom_message.exec_loop()
#       self._Zoom[crv].raise()
    else:
      #To know how many zoom windows opened (so +1)
      self._zoomcount = self._zoomcount + 1
  
      #Get the color of the curve
      pen = QPen(self._plotter.curvePen(crv))
  
      #Put a flag to indicate wich zoom is open (for reploting)
      self._indexzoom[crv] = True

      #open a zoom of the selected curve
      PlotArraySize = self._x1.nelements()
      chart = array(self._chart_data[crv][self._data_index])
      flags = array(self._flag_data[crv][self._data_index])
      self._Zoom[crv] = zoomwin.ZoomPopup(crv+self._ref_chan, self._x1, chart, flags, pen, self)
      if not self._source is None:
        self._Zoom[crv].setCaption(self._source)
        
      if not self._data_label is None:
        if not self._plot_label is None:
          plot_label = self._plot_label[crv+self._ref_chan]
        else:
          plot_label = None
        self._Zoom[crv].setDataLabel(self._data_label, plot_label, self._is_vector)
      self._pause[crv] = False
      # what is all this marker stuff used for?
#     self._mrk[crv] = self._Zoom[crv]._plotter.insertMarker()
#     self._Zoom[crv]._plotter.setMarkerLineStyle(self._mrk[crv], QwtMarker.VLine)
#     self._Zoom[crv]._plotter.setMarkerPos(self._mrk[crv], 10,20)
#     self._Zoom[crv]._plotter.setMarkerLabelAlign(self._mrk[crv], Qt.AlignRight|Qt.AlignTop)
#     self._Zoom[crv]._plotter.setMarkerPen(self._mrk[crv], QPen(self._zoom_pen[crv], 0, Qt.DashDotLine))
#     self._Zoom[crv]._plotter.setMarkerLinePen(self._mrk[crv], QPen(Qt.black, 0, Qt.DashDotLine))
#     self._Zoom[crv]._plotter.setMarkerFont(self._mrk[crv], QFont("Helvetica", 10, QFont.Bold))
      self.connect(self._Zoom[crv], PYSIGNAL("winclosed"), self.myindex)
      self.connect(self._Zoom[crv], PYSIGNAL("winpaused"), self.zoomPaused)

      # make sure option to close all Popup windows is seen
      toggle_id = self.menu_table['Close Popups']
      self._menu.setItemVisible(toggle_id, True)

  def set_offset(self,parameters=None):
    """ Update the display offset.
    """
    if not parameters is None:
      if parameters.haskey("default_offset"):
        self._offset = parameters.get("default_offset")
        if self._offset < 0.0:
          self._auto_offset = True
          self._offset = 0
          self._max_range = -10000
        else:
          self._auto_offset = False

  def set_offset_scale(self,new_scale):
    """ Update the display offset.
    """
    self._offset = new_scale
    if self._offset < 0.0:
      self._auto_offset = True
      self._offset = 0
      self._max_range = -10000
    else:
      self._auto_offset = False

    for channel in range(self._nbcrv):
      self._updated_data[channel] = True
      self._start_offset_test[channel][self._data_index] = 0
    self.reset_zoom()

  def set_auto_scaling(self):
    """ Update the display offset.
    """
    self._auto_offset = True
    self._offset = 0
    self._max_range = -10000
    for channel in range(self._nbcrv):
      self._updated_data[channel] = True
      self._start_offset_test[channel][self._data_index] = 0
    self.reset_zoom()

  def ChartControlData(self):
    """ Resize array if no zoom windows are open.
    """
    #Works if no zoom windows are open
    if self._zoomcount == 0:
      resizex(self._ArraySize)
    else:
      Message = "All zoom windows should be closed\nto perform action."
      zoom_message = QMessageBox("chartplot.py",
                     Message,
                     QMessageBox.Warning,
                     QMessageBox.Ok | QMessageBox.Default,
                     QMessageBox.NoButton,
                     QMessageBox.NoButton)
      zoom_message.exec_loop()

# this is the equivalent of zoomwarn2.py - use this instead if and when ...
#   Message = "Please put the offset at its maximum value\nbefore zooming by a click on the plot"
#   zoom2_message = QMessageBox("chartplot.py",
#                  Message,
#                  QMessageBox.Warning,
#                  QMessageBox.Ok | QMessageBox.Default,
#                  QMessageBox.NoButton,
#                  QMessageBox.NoButton)
#   zoom2_message.exec_loop()

  def resizex(self, size):
    """ Get the size the arrays should have
        reinitialize the arrays
    """
      
    for i in range(self._nbcrv):
      if self._indexzoom[i] and not self._Zoom[i] is None:
        self._Zoom[i].resize_x_axis(self._ArraySize)
    # y data with offset for plotting on the main display
    self._spec_grid_offset.resize(self._ArraySize, self._nbcrv+1)
    self._spec_grid_offset = 0
    self._spec_ptr.resize(self._nbcrv+1)
    for i in range(self._nbcrv):
      self._spec_ptr[i] = dtemp + self._ArraySize * i 

    # the y values for zoom pop up windows without the offset
    self._spec_grid.resize(self._ArraySize,self._nbcrv+1)
    self._spec_grid = 0
    self._spec_ptr_actual.resize(self._nbcrv+1)
    for i in range(self._nbcrv):
      self._spec_ptr_actual[i] = dtemp + self._ArraySize * i 

  def zoomCountmin(self):
    """ Reduces the count of zoom windows opened
    """
    self._zoomcount = self._zoomcount - 1

  def zoomPaused(self, crvtemp):
    self._pause[crvtemp-self._ref_chan] = not self._pause[crvtemp-self._ref_chan]


  def myindex(self, crvtemp):
    """ Sets the indexzoom flag of the curve that just closed to False
    """
    self._indexzoom[crvtemp-self._ref_chan] = False
    self._Zoom[crvtemp-self._ref_chan].exec_close()

  def updateEvent(self, data_dict):
    """ Update the curve data for the given channel
    """
    # in updateEvent, channel goes from 0 to _nbcrv - 1
    # ---
    # if necessary, first remove old data from front of queue
    # add new data to end of queue

    # do we have an incoming dictionary?
    q_pos_str = "Sequence Number " + str( data_dict['sequence_number'])
    self._source = data_dict['source']
    channel_no = data_dict['channel']
    new_chart_val = data_dict['value']
    new_chart_flags = data_dict['flags']
    has_keys = True
    add_vells_menu = False
    try:
      data_keys = new_chart_val.keys()
      add_vells_menu = True
    except:
      has_keys = False
      data_keys = []
      data_keys.append(0)

    if channel_no >=  self._nbcrv:
      factor = int (channel_no / self._nbcrv)
      self._ref_chan = factor * self._nbcrv
      channel = channel_no - self._ref_chan
    else:
      channel = channel_no
    first_vells = True
    for keys in data_keys:
      if not self._chart_data[channel].has_key(keys):
        self._chart_data[channel][keys] = []
        self._flag_data[channel][keys] = []
        self._start_offset_test[channel][keys] = 0
        if len(data_keys) > 1:
          if self._vells_menu is None:
            self._vells_menu = QPopupMenu(self._menu)
            QObject.connect(self._vells_menu,SIGNAL("activated(int)"),self.emit_vells_selector);
            toggle_id = self.menu_table['Change Vells']
            self._menu.insertItem("Change Selected Vells  ",self._vells_menu,toggle_id)
          menu_label = str(keys)
          if not self._vells_keys.has_key(menu_label):
            self._vells_menu.insertItem(menu_label, self._vells_menu_id)
            if first_vells:
              self._vells_menu.setItemChecked(self._vells_menu_id, True)
              first_vells = False
            self._vells_menu_id = self._vells_menu_id + 1
            self._vells_keys[menu_label] = 1

      if has_keys:
        incoming_data = new_chart_val[keys]
        incoming_flags = new_chart_flags[keys]
      else:
        incoming_data = new_chart_val
        incoming_flags = new_chart_flags
      #print 'incoming flags ', incoming_flags
# first, do we have a scalar?
      is_scalar = False
      scalar_data = 0.0
      flag_data = 0
      try:
        shape = incoming_data.shape
# note: if shape is 1 x N : 1 time point with N freq points
# note: if shape is N x 1 or (N,) : N time points with 1 freq point
#     _dprint(3,'data_array shape is ', shape)
      except:
        is_scalar = True
        scalar_data = incoming_data
        if not incoming_flags is None:
          flag_data = incoming_flags
      if not is_scalar and len(shape) == 1:
        if shape[0] == 1:
          is_scalar = True
          scalar_data = incoming_data[0]
          if not incoming_flags is None:
            flag_data = incoming_flags[0]
          
      if is_scalar:
        #print 'scalar is ', scalar_data
#     if len(self._chart_data[channel]) > self._ArraySize-1:
#       differ = len(self._chart_data[channel]) - (self._ArraySize-1)
#       for i in range(differ):
#         del self._chart_data[channel][0]
        self._chart_data[channel][keys].append(scalar_data)
        self._flag_data[channel][keys].append(flag_data)
        self._updated_data[channel] = True

        # take care of position string
        self._position[channel] = q_pos_str
  
      # otherwise we have an array (assumed to be 1D for the moment), 
      # so we add to the stored chart data in its entirety
      else:
        self._is_vector = True
        num_elements = 1
        for i in range(len(incoming_data.shape)):
          num_elements = num_elements * incoming_data.shape[i]
        flattened_array = reshape(incoming_data.copy(),(num_elements,))
        if num_elements > 1 and incoming_data.shape[0] == 1:
          if  self._data_label is None:
            self._plotter.setAxisTitle(QwtPlot.xBottom, "Frequency Spectrum per Tile Block (Relative Scale)")
          else:
            self._plotter.setAxisTitle(QwtPlot.xBottom, self._data_label + " Frequency Spectrum per Tile Block (Relative Scale)")
        if self._append_data: 
          for i in range(len(flattened_array)):
            self._chart_data[channel][keys].append(flattened_array[i])
        else:
          self._chart_data[channel][keys] = flattened_array
        self._updated_data[channel] = True

        if incoming_flags is None:
          flattened_array = zeros((num_elements,), Int32)
        else:
          flattened_array = reshape(incoming_flags.copy(),(num_elements,))
        if self._append_data: 
          for i in range(len(flattened_array)):
            self._flag_data[channel][keys].append(flattened_array[i])
        else:
          self._flag_data[channel][keys] = flattened_array
          self._start_offset_test[channel][keys] = 0

      if self._ArraySize < len(self._chart_data[channel][keys]):
        self._ArraySize = len(self._chart_data[channel][keys])
        self.set_x_axis_sizes()

  def update_vells_selector(self, menuid):
    for i in range(self._vells_menu_id):
      self._vells_menu.setItemChecked(i, False)
    self._vells_menu.setItemChecked(menuid, True)
    self._data_index = int(menuid)
    self._do_fixed_scale = False
    self._auto_offset = True
    self._offset = 0
    self._max_range = -10000
    for channel in range(self._nbcrv):
      self._updated_data[channel] = True
    self.reset_zoom()
    self.refresh_event()

  def change_scale_type(self):
    # click means change to fixed scale
    toggle_id = self.menu_table['Fixed Scale']
    if self._do_fixed_scale:
      self._do_fixed_scale = False
      self._menu.changeItem(toggle_id,'Fixed Scale')
      self._plotter.setAxisAutoScale(QwtPlot.yLeft)
    else: 
      self._do_fixed_scale = True
      self._menu.changeItem(toggle_id, 'Auto Scale')

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

  def change_channel_display(self, toggle_id):
    if self.show_channel_labels:
      self.show_channel_labels = False
      self._menu.changeItem(toggle_id, 'Show Channel Markers')
    else:
      self.show_channel_labels = True
      self._menu.changeItem(toggle_id, 'Hide Channel Markers')
    self._do_fixed_scale = False
    self._auto_offset = True
    self._offset = 0
    self._max_range = -10000
    for channel in range(self._nbcrv):
      self._updated_data[channel] = True
      self._start_offset_test[channel][self._data_index] = 0
    self.refresh_event()


  def set_scale_values(self, max_value, min_value):
    if self._do_fixed_scale:
      self._plotter.setAxisScale(QwtPlot.yLeft, min_value, max_value)
      self._plotter.replot()

  def cancel_scale_request(self):
    if self._do_fixed_scale: 
      self._do_fixed_scale = False
      toggle_id = self.menu_table['Fixed Scale']
      self._menu.changeItem(toggle_id,'Fixed Scale')
      self._plotter.setAxisAutoScale(QwtPlot.yLeft)

  def set_offset_value(self, offset_value):
    self._offset = offset_value
    if self._offset < 0.0:
      self._auto_offset = True
      self._offset = 0
      self._max_range = -10000
    else: 
      self._auto_offset = False


  def refresh_event(self):
    """ redisplay plot and zoom
        if refresh flag is true (new data exists)
        call replots
        set refresh flag False
    """
    # first determine offsets
    if self._auto_offset:
      for channel in range(self._nbcrv):
        if self._updated_data[channel] and self._chart_data[channel].has_key(self._data_index):
          try:
            chart = array(self._chart_data[channel][self._data_index])
            #print 'shape chart ', chart.shape, ' ', chart
          except:
            self._updated_data[channel] = False
            pass
          try:
            flags = array(self._flag_data[channel][self._data_index])
          except:
            self._updated_data[channel] = False
            pass
          # no actual data?
          if chart.shape[0] < 1:
            self._updated_data[channel] = False
          if self._updated_data[channel]:
            test_chart = compress(flags==0,chart)
            if test_chart.shape[0] > 0:
              if chart.type() == Complex32 or chart.type() == Complex64:
                toggle_id = self.menu_table['Complex Data']
                self._menu.setItemVisible(toggle_id, True)
                complex_chart = test_chart.copy()
                if self._amplitude:
                  self._plotter.setAxisTitle(QwtPlot.yLeft, "Amplitude (Relative Scale)")
                  cplx_chart = abs(complex_chart)
                elif self._real:
                  self._plotter.setAxisTitle(QwtPlot.yLeft, "Real (Relative Scale)")
                  cplx_chart = complex_chart.getreal()
                elif self._imaginary:
                  self._plotter.setAxisTitle(QwtPlot.yLeft, "Imaginary (Relative Scale)")
                  cplx_chart = complex_chart.getimag()
                else:
                  self._plotter.setAxisTitle(QwtPlot.yLeft, "Phase (Relative Scale)")
                  real_chart = complex_chart.getreal()
                  imag_chart = complex_chart.getimag()
                  cplx_chart = arctan2(imag_chart,real_chart)
                tmp_max = cplx_chart.max()
                tmp_min = cplx_chart.min()
              else:
                self._amplitude = False
                toggle_id = self.menu_table['Complex Data']
                self._menu.setItemVisible(toggle_id, False)
                tmp_max = test_chart.max()
                tmp_min = test_chart.min()
              chart_range = abs(tmp_max - tmp_min)
              # check if we break any highest or lowest limits
              # this is important for offset reasons.
              if chart_range > self._max_range:
                self._max_range = chart_range
              self._start_offset_test[channel][self._data_index] = chart.shape[0]

      #set the max value of the offset
      if 1.1 * self._max_range > self._offset:
        self._offset = 1.1 * self._max_range

        if self._offset < 0.001:
          self._offset = 0.001
        self.emit(PYSIGNAL("auto_offset_value"),(self._offset,))

    # -----------
    # now update data
    # -----------

    for channel in range(self._nbcrv):
      if self._updated_data[channel] and self._chart_data[channel].has_key(self._data_index):
        index = channel+1
        #Set the values and size with the curves
        if index >= 1 and index <= self._nbcrv/4:
          temp_x = self._x1
        elif index >= (self._nbcrv/4)+1 and index <= self._nbcrv/2:
          temp_x = self._x2
        elif index >= (self._nbcrv/2)+1 and index <= 3*(self._nbcrv/4):
          temp_x = self._x3
        elif index >= (3*(self._nbcrv/4))+1 and index <= self._nbcrv:
          temp_x = self._x4

        if self._phase:
          temp_off = (channel % (self._nbcrv/4) + 0.5 ) * self._offset
        else:
          temp_off = (channel % (self._nbcrv/4)) * self._offset

        chart = array(self._chart_data[channel][self._data_index])
        flags = array(self._flag_data[channel][self._data_index])
        if chart.type() == Complex32 or chart.type() == Complex64:
          complex_chart = chart.copy()
          if self._amplitude:
            self._plotter.setCurvePen(self._crv_key[channel], QPen(Qt.red))
            cplx_chart = abs(complex_chart)
          elif self._real:
            self._plotter.setCurvePen(self._crv_key[channel], QPen(Qt.blue))
            cplx_chart = complex_chart.getreal()
          elif self._imaginary:
            self._plotter.setCurvePen(self._crv_key[channel], QPen(Qt.gray))
            cplx_chart = complex_chart.getimag()
          else:
            self._plotter.setCurvePen(self._crv_key[channel], QPen(Qt.green))
            real_chart = complex_chart.getreal()
            imag_chart = complex_chart.getimag()
            cplx_chart = arctan2(imag_chart,real_chart)
          # don't display flagged data
          if self._ignore_flagged_data:
            x_plot_values = compress(flags==0,temp_x)
            y_plot_values = compress(flags==0,cplx_chart)
            if y_plot_values.shape[0] == 0:
              y_plot_values = None
          else:
            x_plot_values = temp_x
            y_plot_values = cplx_chart

          if not y_plot_values is None: 
            self._plotter.setCurveData(self._crv_key[channel], x_plot_values , y_plot_values+temp_off)
            ylb = y_plot_values[0] + temp_off 
        else:
          self._plotter.setCurvePen(self._crv_key[channel], QPen(Qt.black))
          # don't display flagged data
          if self._ignore_flagged_data:
            x_plot_values = compress(flags==0,temp_x)
            y_plot_values = compress(flags==0,chart)
            if y_plot_values.shape[0] == 0:
              y_plot_values = None
          else:
            x_plot_values = temp_x
            y_plot_values = chart

          if not y_plot_values is None: 
            self._plotter.setCurveData(self._crv_key[channel], x_plot_values , y_plot_values+temp_off)
            ylb = y_plot_values[0] + temp_off 

        # update marker with info about the plot
        if not self._source_marker[channel] is None:
          self._plotter.removeMarker(self._source_marker[channel]);
        if not y_plot_values is None and self.show_channel_labels:
          if not self._plot_label is None:
            message = self._plot_label[channel + self._ref_chan]
          else:
            message =  str(channel + self._ref_chan)
# text marker giving source of point that was clicked
          self._source_marker[channel] = self._plotter.insertMarker()
          xlb = temp_x[0]
          self._plotter.setMarkerPos(self._source_marker[channel], xlb, ylb)
          self._plotter.setMarkerLabelAlign(self._source_marker[channel], Qt.AlignRight | Qt.AlignTop)
          fn = self._plotter.fontInfo().family()
          self._plotter.setMarkerLabel(self._source_marker[channel], message,
            QFont(fn, 7, QFont.Bold, False),
            Qt.blue, QPen(Qt.red, 2), QBrush(Qt.yellow))
	 
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
    self._array = zeros((128,), Float32)
    self.startTimer(time)

  def timerEvent(self, e):
#   self.counter = 1.0 + 1 * random.random()
#   self.updateEvent(1, self.counter, 'xyz')
#   self.counter = 1.0 + 1 * random.random()
#   self.updateEvent(3, self.counter, 'xyz')
#   self.counter = 1.0 + 1 * random.random()
#   self.updateEvent(9, self.counter, 'xyz')


    for i in range(self._array.shape[0]):
      self._array[i] = 0.05 * random.random()
    self.updateEvent(1, self._array, 'spectra')

    for i in range(self._array.shape[0]):
      self._array[i] = 3 * random.random()
    self.updateEvent(3, self._array, 'spectra')

    for i in range(self._array.shape[0]):
      self._array[i] = 11 * random.random()
    self.updateEvent(11, self._array, 'spectra')

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


