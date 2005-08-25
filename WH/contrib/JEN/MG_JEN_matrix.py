script_name = 'MG_JEN_matrix.py'

# Short description:
#   Some useful matrix subtrees 

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 22 aug 2005: creation

# Copyright: The MeqTree Foundation 

#================================================================================
# Import of Python modules:

from Timba.TDL import *
from Timba.Meq import meq

from numarray import *
# from string import *
# from copy import deepcopy

from Timba.Contrib.JEN import MG_JEN_exec as MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state as MG_JEN_forest_state

# from Timba.Contrib.JEN import MG_JEN_util as MG_JEN_util
# from Timba.Contrib.JEN import MG_JEN_twig as MG_JEN_twig
# from Timba.Contrib.JEN import MG_JEN_math as MG_JEN_math
# from Timba.Contrib.JEN import MG_JEN_funklet as MG_JEN_funklet




#================================================================================
# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.
#================================================================================

def _define_forest (ns):

   # Generate a list (cc) of one or more node bundles (bb):
   cc = []

   # Test/demo of importable function: rotation_matrix()
   bb = []
   angle1 = ns.angle1('3c84', x=4, y=5) << Meq.Constant(3)
   # angle2 = ns.angle2(y=5) << Meq.Constant(-1)
   angle2 = -1
   bb.append(rotation_matrix (ns, angle1))
   bb.append(rotation_matrix (ns, [angle2]))
   bb.append(rotation_matrix (ns, [angle1, angle2]))
   cc.append(MG_JEN_exec.bundle(ns, bb, 'rotation'))

   # Test/demo of importable function: ellipticity_matrix()
   bb = []
   angle1 = ns.angle1(x=4, y=5) << Meq.Constant(3)
   angle2 = ns.angle2(y=5) << Meq.Constant(-1)
   bb.append(ellipticity_matrix (ns, angle1))
   bb.append(ellipticity_matrix (ns, [angle2]))
   bb.append(ellipticity_matrix (ns, [angle1, angle2]))
   cc.append(MG_JEN_exec.bundle(ns, bb, 'ellipticity'))
   
   # Test/demo of importable function: phase_matrix()
   bb = []
   angle1 = ns.angle1(x=4, y=5) << Meq.Constant(3)
   angle2 = ns.angle2(y=5) << Meq.Constant(-1)
   bb.append(phase_matrix (ns, angle1))
   bb.append(phase_matrix (ns, [angle2]))
   bb.append(phase_matrix (ns, [angle1, angle2]))
   cc.append(MG_JEN_exec.bundle(ns, bb, 'phase'))


   # Finished: 
   return MG_JEN_exec.on_exit (ns, cc)







#================================================================================
# OPtional: Importable function(s): To be imported into user scripts. 
#================================================================================



#------------------------------------------------------------
# Make a 2x2 rotation matrix

def rotation_matrix (ns, angle=0, qual='auto'):

    qual = MG_JEN_forest_state.autoqual(qual, 'MG_JEN_matrix_rotation')

    different_angles = 0
    if isinstance(angle, (list, tuple)):
        a1 = angle[0]
        a2 = a1
        if len(angle)>1:
            different_angles = 1
            a2 = angle[1]
    else:
        a1 = angle
        a2 = a1
            
    if different_angles:
        cos1 = (ns << Meq.Cos(a1))
        cos2 = (ns << Meq.Cos(a2))
        sin2 = (ns << Meq.Sin(a2))
        sin1 = (ns << Meq.Sin(a1))
        sin1 = (ns << Meq.Negate(sin1))
    else:
        cos1 = (ns << Meq.Cos(a1))
        cos2 = cos1
        sin2 = (ns << Meq.Sin(a1))
        sin1 = (ns << Meq.Negate(sin2))
 
    name = 'rotation_matrix'       
    mat = (ns[name].qmerge(cos1, sin1, cos2, sin2)(qual) << Meq.Composer(
		children=[cos1, sin1, cos2, sin2], dims=[2,2]))

    return mat


#------------------------------------------------------------
# Make a 2x2 ellipticity matrix

def ellipticity_matrix (ns, angle=0, qual='auto'):

    qual = MG_JEN_forest_state.autoqual(qual, 'MG_JEN_matrix_ellipt')

    different_angles = 0
    if isinstance(angle, (list, tuple)):
        a1 = angle[0]
        a2 = a1
        if len(angle)>1:
            different_angles = 1
            a2 = angle[1]
    else:
        a1 = angle
        a2 = a1
            
    if different_angles:
        cos1 = (ns << Meq.Cos(a1))
        cos2 = (ns << Meq.Cos(a2))
        sin1 = (ns << Meq.Sin(a1))
        sin2 = (ns << Meq.Sin(a2))
        isin1 = (ns << Meq.ToComplex(0, sin1))
        isin2 = (ns << Meq.ToComplex(0, sin2))
        isin2 = (ns << Meq.Conj(isin2))

    else:
        cos1 = (ns << Meq.Cos(a1))
        cos2 = cos1
        sin = (ns << Meq.Sin(a1))
        isin2 = (ns << Meq.ToComplex(0, sin))
        isin1 = isin2

    name = 'ellipticity_matrix'      
    mat = (ns[name].qmerge(cos1,isin1, isin2, cos2)(qual) << Meq.Composer(
	children=[cos1, isin1, isin2, cos2], dims=[2,2]))

    return mat

#------------------------------------------------------------
# Make a 2x2 phase matrix

def phase_matrix (ns, angle=0, qual='auto'):

    qual = MG_JEN_forest_state.autoqual(qual, 'MG_JEN_matrix_phase')

    different_angles = 0
    if isinstance(angle, (list, tuple)):
        a1 = angle[0]
        a2 = a1
        if len(angle)>1:
            different_angles = 1
            a2 = angle[1]
    else:
        a1 = angle
        a2 = a1
            
    if different_angles:
        m11 = (ns << Meq.Polar(1, a1))
        m22 = (ns << Meq.Polar(1, a2))

    else:
        m11 = (ns << Meq.Polar(1, a1/2))
        m22 = (ns << Meq.Polar(1, ns << Meq.Negate(a1/2)))

    name = 'phase_matrix'     
    mat = (ns[name].qmerge(m11, m22)(qual) << Meq.Composer(
           children=[m11, 0, 0, m22], dims=[2,2]))
    return mat





#********************************************************************************
# Initialisation and test routines
#********************************************************************************

#--------------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(script_name)


#--------------------------------------------------------------------------------
# Tree execution routine (may be called from the browser):
# The 'mqs' argument is a meqserver proxy object.

def _test_forest (mqs, parent):
   return MG_JEN_exec.meqforest (mqs, parent)

#--------------------------------------------------------------------------------
# Test routine to check the tree for consistency in the absence of a server

if __name__ == '__main__':
    if True:
        # This is the default:
        MG_JEN_exec.without_meqserver(script_name)

    else:
       # This is the place for some specific tests during development.
       print '\n**',script_name,':\n'
       ns = NodeScope()
       if 1:
          rr = rotation_matrix (ns, angle=1)
          MG_JEN_exec.display_subtree (rr, 'rotation_matrix', full=1)
          
       if 1:
          rr = ellipticity_matrix (ns, angle=1)
          MG_JEN_exec.display_subtree (rr, 'ellipticity_matrix', full=1)
          
       if 1:
          rr = phase_matrix (ns, angle=1)
          MG_JEN_exec.display_subtree (rr, 'phase_matrix', full=1)
          
       print '\n** end of',script_name,'\n'

#********************************************************************************




