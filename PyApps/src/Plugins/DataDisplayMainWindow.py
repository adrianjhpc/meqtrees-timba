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

# This is a translation to python of the ACSIS IfDisplayMainWindow.cc code

import sys
from qt import *
try:
  from Qwt4 import *
except:
  from qwt import *
from numarray import *
import chartplot
import random

class DisplayMainWindow(QMainWindow):
  """ This class enables the display of a collection
      of ChartPlot widgets contained within a tabwidget
  """
  def __init__(self, parent=None, name=None,num_curves=16):
    QMainWindow.__init__(self, parent, name, Qt.WDestructiveClose)

# ChartPlot strip charts will be displayed via a tab widget
    self._tabwidget = QTabWidget(self)
    self._tab_resized = False
    self._num_curves = num_curves

# create a dictionary of chart plot objects
    self._ChartPlot = {}
    self._click_on = " If you click on an individual stripchart with the left mouse button, a popup window will appear that gives a more detailed view of the data from that particular object."

  def updateEvent(self, data_dict):
    data_type = data_dict['data_type']
    if not self._ChartPlot.has_key(data_type):
      self._ChartPlot[data_type] = chartplot.ChartPlot(num_curves=self._num_curves, parent=self)
      self._ChartPlot[data_type].setDataLabel(data_type)
      self._tabwidget.addTab(self._ChartPlot[data_type], data_type)
      self._tabwidget.showPage(self._ChartPlot[data_type])
      self._tabwidget.resize(self._tabwidget.minimumSizeHint())
      self.resize(self._tabwidget.minimumSizeHint())
      dcm_sn_descriptor = "This window shows stripcharts of the " + data_type + " as a function of time."
      dcm_sn_descriptor = dcm_sn_descriptor + self._click_on
      QWhatsThis.add(self._ChartPlot[data_type], dcm_sn_descriptor)
      self.connect(self._ChartPlot[data_type], PYSIGNAL("quit_event"), self.quit_event)
      self._ChartPlot[data_type].show()
    q_info = "Sequence Number " + str( data_dict['sequence_number'])
    self._ChartPlot[data_type].updateEvent(data_dict['channel'], data_dict['value'], q_info)

  def resizeEvent(self, event):
    keys = self._ChartPlot.keys()
    for i in range(len(keys)):
      self._ChartPlot[keys[i]].resize(event.size())
    self._tabwidget.resize(event.size())

#void IfDisplayMainWindow.set_data_flag(Int channel, Bool flag_value)
#{
#	_ChartPlot(0).set_data_flag(channel,flag_value)
#
## if flag_value == False, we have bad data!
#	if (!flag_value) {
#    		QColor col
#		col.setNamedColor("IndianRed")
#    		statusBar().setPaletteBackgroundColor(col)
#		QString channel_number
#		channel_number.setNum(channel)
#		QString Message = "Bad TSYS detected for channel "+ channel_number 
#    		statusBar().message( Message)
#        	QTimer *timer = new QTimer(this)
#        	connect( timer, SIGNAL(timeout()), this, SLOT(resetStatus()) )
## TRUE means that this will be a one-shot timer
#        	timer.start(500, TRUE)
#	}
#}

#void IfDisplayMainWindow.resetStatus()
#{
#    		QColor col
#    		col.setNamedColor("LightYellow")
#    		statusBar().setPaletteBackgroundColor(col)
#		QString Message = " "
#    		statusBar().message( Message)
#}
#
  def quit_event(self):
    self.close()
  def start_test_timer(self, time):
    # stuff for tests
    self.seq_num = 0
    self._gain = 0
    self._array = zeros((128,), Float32)
    self._array_imag = zeros((128,), Float32)
    self._array_complex = zeros((128,), Complex64)
    self.startTimer(time)

  def timerEvent(self, e):
    self.seq_num = self.seq_num + 1
    data_dict = {}
    data_dict['data_type'] = 'scalar'
    data_dict['sequence_number'] = self.seq_num
    for i in range(16):
      data_dict['channel'] = i
      data_dict['value'] = (i+1) * random.random()
      self.updateEvent(data_dict)

    data_dict['data_type'] = 'another scalar'
    for i in range(16):
      data_dict['channel'] = i
      data_dict['value'] = self._gain + (i+1) * random.random()
      self.updateEvent(data_dict)

    data_dict['data_type'] = 'spectra'
    for j in range(16):
      data_dict['channel'] = j
      if j == 13:
        for i in range(self._array.shape[0]):
          self._array[i] = 11 * random.random()
          self._array_imag[i] = 6 * random.random()
        self._array_complex.setreal(self._array)
        self._array_complex.setimag(self._array_imag)
        data_dict['value'] = self._array_complex
      else:
        for i in range(self._array.shape[0]):
          self._array[i] = (j+1) * random.random()
        data_dict['value'] = self._array
      self.updateEvent(data_dict)

    data_dict['data_type'] = 'tensor demo'
    for i in range(16):
      data_dict['channel'] = i
      data_dict['value'] = {}
      for j in range(4):
        gain = 1.0
        if j == 1 or j == 2:
          gain = 0.1
        for k in range(self._array.shape[0]):
          self._array[k] = gain * random.random()
        data_dict['value'][j] = self._array.copy()
      self.updateEvent(data_dict)

    self._gain = self._gain + 0.5
    return

def make():
    demo = DisplayMainWindow()
    demo.show()
    demo.start_test_timer(1000)
    return demo

def main(args):
    app = QApplication(args)
    demo = make()
    app.setMainWidget(demo)
    app.exec_loop()


# Admire
if __name__ == '__main__':
    main(sys.argv)

