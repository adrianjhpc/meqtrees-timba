#
#% $Id$
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation &
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
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
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from Timba.TDL import *
import Meow
from Meow import Context
from Meow import ParmGroup,Bookmarks
from Meow.Parameterization import resolve_parameter

class IfrGains (object):
  def __init__ (self):
    self.options = [];

  def runtime_options (self):
    return self.options;

  def process_visibilities (self,nodes,input_nodes,ns=None,
                             ifrs=None,tags=None,label='',**kw):
    ns = ns or nodes.Subscope();
    ifrs = ifrs or Context.array.ifrs();
    label = label or 'ifr_gains';
    G = ns.gain;
    def1 = Meow.Parm(1,tags=tags);
    def0 = Meow.Parm(0,tags=tags);
    gains = [];
    for p,q in ifrs:
      gg = [];
      for corr in Context.correlations:
        if corr in Context.active_correlations:
          gain_ri  = [ resolve_parameter(corr,G(p,q,corr,'r'),def1,tags="ifr gain real"),
                       resolve_parameter(corr,G(p,q,corr,'i'),def0,tags="ifr gain imag") ];
          gg.append(G(p,q,corr) << Meq.ToComplex(*gain_ri));
          gains += gain_ri;
        else:
          gg.append(1);
      G(p,q) << Meq.Matrix22(*gg);
      nodes(p,q) << input_nodes(p,q)*G(p,q);

    pg_ifr_ampl = ParmGroup.ParmGroup(label,gains,
                          individual_toggles=False,
                          table_name="%s.fmep"%label,bookmark=False);
    Bookmarks.make_node_folder("%s (interferometer-based gains)"%label,
      [ G(p,q) for p,q in ifrs ],sorted=True,nrow=2,ncol=2);
    ParmGroup.SolveJob("cal_%s"%label,
                       "Calibrate %s (interferometer-based gains)"%label,pg_ifr_ampl);
    
    return nodes;

  def correct_visibilities (self,nodes,input_nodes,ns=None,
                            ifrs=None,tags=None,label='',**kw):
    ns = ns or nodes.Subscope();
    ifrs = ifrs or Context.array.ifrs();
    G = ns.gain;
    for p,q in ifrs:
      nodes(p,q) << input_nodes(p,q)/G(p,q);
    
    return nodes;

class IfrBiases (object):
  def __init__ (self):
    self.options = [];

  def runtime_options (self):
    return self.options;

  def process_visibilities (self,nodes,input_nodes,ns=None,
                             ifrs=None,tags=None,label='',**kw):
    ns = ns or nodes.Subscope();
    ifrs = ifrs or Context.array.ifrs();
    label = label or 'ifr_biases';
    C = ns.bias;
    def0 = Meow.Parm(0,tags=tags);
    biass = [];
    for p,q in ifrs:
      gg = [];
      for corr in Context.correlations:
        if corr in Context.active_correlations:
          bias_ri  = [ resolve_parameter(corr,G(p,q,corr,'r'),def0,tags="ifr bias real"),
                       resolve_parameter(corr,G(p,q,corr,'i'),def0,tags="ifr bias imag") ];
          gg.append(G(p,q,corr) << Meq.ToComplex(*bias_ri));
          biases += bias_ri;
        else:
          gg.append(1);
      C(p,q) << Meq.Matrix22(*gg);
      nodes(p,q) << input_nodes(p,q) + C(p,q);

    pg_ifr_ampl = ParmGroup.ParmGroup(label,biases,
                          individual_toggles=False,
                          table_name="%s.fmep"%label,bookmark=False);
    Bookmarks.make_node_folder("%s (interferometer-based biases)"%label,
      [ G(p,q) for p,q in ifrs ],sorted=True,nrow=2,ncol=2);
    ParmGroup.SolveJob("cal_%s"%label,
                       "Calibrate %s (interferometer-based biases)"%label,pg_ifr_ampl);
    
    return nodes;

  def correct_visibilities (self,nodes,input_nodes,ns=None,
                            ifrs=None,tags=None,label='',**kw):
    ns = ns or nodes.Subscope();
    ifrs = ifrs or Context.array.ifrs();
    C = ns.bias;
    for p,q in ifrs:
      nodes(p,q) << input_nodes(p,q) - C(p,q);
    
    return nodes;
