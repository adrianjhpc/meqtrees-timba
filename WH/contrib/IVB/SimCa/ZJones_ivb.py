from Timba.TDL import *
import Meow
from Meow import Context
from Meow import Jones,ParmGroup,Bookmarks

# import the different MIM modules
from Timba.Contrib.MXM.MimModule.KL import KL_MIM
from Timba.Contrib.MXM.MimModule import TID_MIM
from Timba.Contrib.MXM.MimModule import Poly_MIM
#from Timba.Contrib.IVB.MimModule import TID_MIM_2waves
#from Timba.Contrib.IVB.KolMIM import Kolmogorov_MIM_ivb
#@Leiden
import TID_MIM_2waves
import Kolmogorov_MIM_ivb

def _modname (obj):
  if hasattr(obj,'name'):
    name = obj.name;
  elif hasattr(obj,'__name__'):
    name = obj.__name__;
  else:
    name = obj.__class__.__name__;
  return name;


def _modopts (mod,opttype='compile'):
  """for the given module, returns a list of compile/runtime options suitable for passing
  to TDLMenu. If the module implements a compile/runtime_options() method, uses that,
  else simply uses the module itself.""";
  modopts = getattr(mod,opttype+'_options',None);
  # if module defines an xx_options() callable, use that
  if callable(modopts):
    return list(modopts());
  # else if this is a true module, it may have options to be stolen, so insert as is
  elif inspect.ismodule(mod):
    return [ mod ];
  # else item is an object emulating a module, so insert nothing
  else:
    return [];

modules=[KL_MIM,TID_MIM,TID_MIM_2waves,Poly_MIM,Kolmogorov_MIM_ivb];
submenus = [ TDLMenu("Use '%s' module"%_modname(mod),name=_modname(mod),
                     toggle=_modname(mod).replace('.','_'),namespace={},
                     *_modopts(mod,'compile'))
             for mod in modules ];
mainmenu = TDLMenu("MIM model",exclusive="selname",
                   *(submenus));


class ZJones(object):
  def __init__ (self):
      
    self.options = [];

  def runtime_options (self):
    return self.options;

  def compute_jones (self,jones,sources,stations=None,tags=None,label='',**kw):
    stations = stations or Context.array.stations();
    print "selected",selname;
    for mod in modules:
      print _modname(mod),selname;
      if _modname(mod).replace('.','_') == selname:
        self.mim_model=mod;
        break;
    mim = self.mim_model.MIM(jones.Subscope(),None,sources,Context.array,tags=tags);
    mim.compute_jones(jones,tags=tags);
    return jones;

  def compile_options(self):
    return [mainmenu,];

