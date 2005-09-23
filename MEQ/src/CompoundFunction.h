//# CompoundFunction.h: Base class for an compound expression node (i.e. with multiple-planed result)
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
//# $Id$

#ifndef MEQ_COMPOUNDFUNCTION_H
#define MEQ_COMPOUNDFUNCTION_H
    
#include <MEQ/Function.h>

namespace Meq { using namespace DMI;

//##ModelId=3F86886E01A8
class CompoundFunction : public Function
{
public:
    //##ModelId=3F86886E03C5
  CompoundFunction (int nchildren=-1,const HIID *labels = 0,int nmandatory=-1);

    //##ModelId=3F86886E03D1
  virtual ~CompoundFunction();

protected:
    
  virtual void evalFlags (vector<Vells::Ref> &out_flags,
                          const vector<const VellSet *> &pvs,
                          const Cells *pcells);
    
  virtual void evalResult (std::vector<Vells> &res,
          const std::vector<const Vells*> &values,
          const Cells *pcells) 
    = 0;

  int checkChildResults (Result::Ref &resref, 
                         std::vector<const VellSet *> &child_vs,
                         const std::vector<Result::Ref> &childres,
                         const int expect_nvs[],
                         const int expect_integrated[]);

  void computeValues (Result &result,const std::vector<const VellSet *> &chvs,
                      const Cells *pcells);
    
};

} // namespace Meq

#endif
