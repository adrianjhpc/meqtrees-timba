from Timba.TDL import *
from Timba.Meq import meq
from Parameterization import *
from Direction import *
import Context

class SkyComponent (Parameterization):
  """A SkyComponent represents an abstract sky model element.
  SkyComponents have an name and an associated direction.
  """;
  def __init__(self,ns,name,direction):
    Parameterization.__init__(self,ns,name);
    if isinstance(direction,Direction):
      self.direction = direction;
    else:
      if not isinstance(direction,(list,tuple)) or len(direction) != 2:
        raise TypeError,"direction: Direction object or (ra,dec) tuple expected";
      ra,dec = direction;
      self.direction = Direction(ns,name,ra,dec);
    
  def radec (self):
    """Returns ra-dec two-pack for this component's direction""";
    return self.direction.radec();
    
  def lmn (self,dir0=None):
    return self.direction.lmn(dir0);
    
  def make_visibilities (self,nodes,array,observation):
    """Abstract method.
    Creates nodes computing nominal visibilities of this component 
    Actual nodes are then created as nodes(name,sta1,sta2) for all array.ifrs().
    Returns partially qualified visibility node which must be qualified 
    with an (sta1,sta2) pair.
    """;
    raise TypeError,type(self).__name__+".make_visibilities() not defined";
    
  def visibilities  (self,array=None,observation=None,nodes=None):
    """Creates nodes computing visibilities of component.
    'array' is an IfrArray object, or None if the global context is to be used.
    'observation' is an Observation object, or None if the global context is 
      to be used.
    If 'nodes' is None, creates visibility nodes as ns.visibility(name,...,p,q), 
    where '...' are any extra qualifiers from observation.radec0().
    Otherwise 'nodes' is supposed to refer to an unqualified node, and 
    visibility nodes are created as nodes(p,q).
    Returns the actual unqualified visibility node that was created, i.e. 
    either 'nodes' itself, or the automatically named nodes""";
    observation = Context.get_observation(observation);
    array = Context.get_array(array);
    if nodes is None:
      nodes = self.ns.visibility.qadd(observation.radec0());
    if not nodes(*(array.ifrs()[0])).initialized():
      self.make_visibilities(nodes,array,observation);
    return nodes;
    
  def corrupt (self,jones,per_station=True,label=None):
    from Meow.CorruptComponent import CorruptComponent
    if per_station:
      return CorruptComponent(self.ns0,self,station_jones=jones,label=label);
    else:
      return CorruptComponent(self.ns0,self,jones=jones,label=label);
      
