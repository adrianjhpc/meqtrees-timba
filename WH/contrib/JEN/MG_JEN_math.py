script_name = 'MG_JEN_math.py'

# Short description:
#   Helper functions for easy generation of (math) expression subtrees

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 22 aug 2005: creation

# Copyright: The MeqTree Foundation 


# Import Python modules:
from Timba.TDL import *
from Timba.Meq import meq

from numarray import *
# from string import *
# from copy import deepcopy

from Timba.Contrib.JEN import MG_JEN_exec as MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state as MG_JEN_forest_state

# from Timba.Contrib.JEN import MG_JEN_util as MG_JEN_util
# from Timba.Contrib.JEN import MG_JEN_funklet as MG_JEN_funklet



#================================================================================
# Required functions:
#================================================================================


#--------------------------------------------------------------------------------
# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.

def _define_forest (ns):

   # Generate a list (cc) of one or more root nodes:
   cc = []

   # Make some (f,t) variable input node:
   freq = ns.freq(a=1, b=2) << Meq.Freq()
   time = ns.time(-5, b=2) << Meq.Time()
   input = ns.freqtime << Meq.Add(freq, time)
 
   # Test/demo of importable function: unop()
   unops = False
   unops = 'Cos'
   unops = ['Sin','Cos']
   cc.append(unop(ns, unops, input))

   # Finished: 
   return MG_JEN_exec.on_exit (ns, cc)



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
   MG_JEN_exec.without_meqserver(script_name)









#================================================================================
# Importable function(s): The essence of a MeqGraft (MG) script.
# To be imported into user scripts. 
#================================================================================

#-------------------------------------------------------------------------------
# Recursive function to apply zero or more unary operations on the given node:

def unop (ns, unop=False, node=0):
    if unop == None: return node
    if isinstance(unop, bool): return node
    if isinstance(unop, str): unop = [unop]
    if not isinstance(unop, list): return node
    for unop1 in unop:
        if isinstance(unop1, str):
            node = ns << getattr(Meq, unop1)(node)
    return node
   

#-------------------------------------------------------------------------------

#********************************************************************************




