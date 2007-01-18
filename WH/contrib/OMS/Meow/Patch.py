from SkyComponent import *
import Context

class Patch (SkyComponent):
  def __init__(self,ns,name,direction):
    SkyComponent.__init__(self,ns,name,direction);
    self._components = [];
    
  def add (self,*comps):
    """adds components to patch""";
    self._components += comps;
    
  def make_visibilities (self,nodes,array,observation):
    array = array or Context.array;
    observation = observation or Context.observation;
    if not array or not observation:
      raise ValueError,"array or observation not specified in global Meow.Context, or in this function call";
    radec0 = observation.radec0();
    # no components -- use 0
    if not self._components:
      [ nodes(*ifr) << 0.0 for ifr in array.ifrs() ];
    else:
      compvis = [ comp.visibilities(array,observation) for comp in self._components ];
      # add them up per-ifr
      [ nodes(*ifr) << Meq.Add(*[vis(*ifr) for vis in compvis])
        for ifr in array.ifrs()
      ];
    return nodes;
