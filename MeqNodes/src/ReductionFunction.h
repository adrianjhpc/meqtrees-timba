//# ReductionFunction.h: abstract base for reduction funcs (min/max/mean/etc.)
//#
//# Copyright (C) 2003
//# ASTRON (Netherlands Foundation for Research in Astronomy)
//# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
//#
//# This program is free software; you can redistribute it and/or modify
//# it under the terms of the GNU General Public License as published by
//# the Free Software Foundation; either version 2 of the License, or
//# (at your option) any later version.
//#
//# This program is distributed in the hope that it will be useful,
//# but WITHOUT ANY WARRANTY; without even the implied warranty of
//# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//# GNU General Public License for more details.
//#
//# You should have received a copy of the GNU General Public License
//# along with this program; if not, write to the Free Software
//# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#

#ifndef MEQNODES_REDUCTIONFUNCTION_H
#define MEQNODES_REDUCTIONFUNCTION_H
    
#include <MEQ/Function.h>

#include <MeqNodes/TID-MeqNodes.h>
#pragma aidgroup MeqNodes
#pragma types #Meq::Sum

namespace Meq {    


class ReductionFunction : public Function
{
public:
  ReductionFunction (int nchildren=-1,int nmandatory=1);

  // child flags normally swallowed up
  virtual void evaluateFlags (Vells::Ref &,const Request &,const LoShape &,const vector<const Vells*>&)
  {}
  
protected:
  // get flagmask from state
  virtual void setStateImpl (DMI::Record::Ref &rec,bool initializing);

  VellsFlagType flagmask_;
};


} // namespace Meq

#endif
