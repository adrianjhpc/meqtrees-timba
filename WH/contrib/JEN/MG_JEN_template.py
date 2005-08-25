script_name = 'MG_JEN_template.py'

# Short description:
# Template for the generation of MeqGraft scripts

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 24 aug 2005: creation

# Copyright: The MeqTree Foundation 

#================================================================================
# How to use this template:
# - Copy it to a suitably named script file (e.g. MG_JEN_xyz.py)
# - Fill in the correct script_name at the top
# - Fill in the author and the short description
# - Replace the example importable function with specific ones
# - Make the specific _define_forest() function
# - Remove this 'how to' recipe

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

   # Test/demo of importable function:
   bb = []
   bb.append(importable_example (ns, arg1=1, arg2=2))
   bb.append(importable_example (ns, arg1=3, arg2=4))
   cc.append(MG_JEN_exec.bundle(ns, bb, 'bundle_1'))

   bb = []
   bb.append(importable_example (ns, arg1=1, arg2=5))
   bb.append(importable_example (ns, arg1=1, arg2=6))
   cc.append(MG_JEN_exec.bundle(ns, bb, 'bundle_2'))

   # Finished: 
   return MG_JEN_exec.on_exit (ns, cc)




#================================================================================
# Optional: Importable function(s): To be imported into user scripts.
#================================================================================

#-------------------------------------------------------------------------------
# Example:

def importable_example(ns, qual='auto', **pp):

    # If necessary, make an automatic qualifier:
    qual = MG_JEN_forest_state.autoqual('MG_JEN_template_example')

    default = array([[1, pp['arg1']/10],[pp['arg2']/10,0.1]])
    node = ns.dummy(qual) << Meq.Parm(default)
    return node






#********************************************************************************
# Initialisation and testing routines
# NB: this section should always be at the end of the script
#********************************************************************************

#-------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(script_name)

#-------------------------------------------------------------------------
# Meqforest execution routine (may be called from the browser):
# The 'mqs' argument is a meqserver proxy object.
# If not explicitly supplied, a default request will be used.

def _test_forest (mqs, parent):
   return MG_JEN_exec.meqforest (mqs, parent)

#-------------------------------------------------------------------------
# Test routine to check the tree for consistency in the absence of a server

if __name__ == '__main__':
    if True:
        # This is the default:
        MG_JEN_exec.without_meqserver(script_name)

    else:
       # This is the place for some specific tests during development.
       print '\n**',script_name,':\n'
       # ns = NodeScope()
       # ............
       # MG_JEN_exec.display_subtree (rr, 'rr', full=1)
       print '\n** end of',script_name,'\n'

#********************************************************************************
#********************************************************************************




