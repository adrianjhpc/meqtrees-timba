from Timba.TDL import *
from Timba.Meq import meq
from SkyComponent import *
from Direction import Direction

class SixpackComponent (SkyComponent):
  """SixpackComponent is an abstract component type that deals with 
  lm plane sixpacks (such as images). Derived classes are expected to 
  implement a sixpack() method that returns a (ra,dec,I,Q,U,V) sixpack,
  This class takes care of setting up the FFTBrick and UVInterpol nodes
  needed for transforming l-m images into the uv plane. And example of
  a derived class would be a FitsImageComponent.";
  """;
  class SixpackDirection (Direction):
    """an sixpack direction is a Direction w/o explicit ra-dec nodes --
    instead it uses the ra/dec supplied by the sixpack""";
    def __init__ (self,ns,name,sixpack):
      Parameterization.__init__(self,ns,name);
      self._sixpack = sixpack;
      
    def radec (self):
      return self._sixpack.sixpack_radec();
  
  def __init__(self,ns,name,direction=None,fluxscale=None):
    # if a direction is not supplied, use the built-in sixpack's direction
    if direction is not None:
      direction = self.SixpackDirection(ns,name,self);
    SkyComponent.__init__(self,ns,name,direction);
    # setup various options
    if fluxscale:
      self._fluxscale = self._parm("fluxscale",float(fluxscale));
    else:
      self._fluxscale = None;
    self._fft_pad_factor = 1.0;
    self._interpol_method = 1;
    self._interpol_debug = True;
    
  def sixpack (self):
    raise TypeError,type(self).__name__+".sixpack() not defined";
    
  def set_options (self,fft_pad_factor=None,interpol_method=None,interpol_debug=None):
    """Sets various options for the fft/interpolation:
    pad_factor (default 1.0):
        The padding factor used for the FFTs. According to RJN, an image 
        should be padded by a factor of ~8; if the signal in an NxN image is 
        restricted to a central core of MxM pixels, then the pad factor 
        should be 8*(M/N)
    interpol_method:  interpolation method for UVInterpol. 
        1: Bi-Cubic Hermite Interpolation (default, most accurate)
        2: 4th order polynomial interpolation
        3: Bi-linear interpolation
    interpol_debug: if True, UVInterpol will provide additional "debug"
        images (of the interpolation points, etc.)
    """;
    if fft_pad_factor is not None:
      self._fft_pad_factor = float(fft_pad_factor);
    if interpol_method is not None:
      self._interpol_method = int(interpol_method);
    if interpol_debug is not None:
      self._interpol_debug = bool(interpol_debug);

  def iquv (self):
    """Returns an IQUV four-pack for this source""";
    iquv = self.ns.iquv;
    if not iquv.initialized():
      if self._fluxscale:
        iquv << \
          (self.ns.iquv0 << Meq.Selector(self.sixpack(),index=(2,3,4,5),multi=True)) \
          * self._fluxscale;
      else:
        iquv << Meq.Selector(self.sixpack(),index=(2,3,4,5),multi=True);
    return iquv;
    
  def sixpack_radec (self):
    """Returns ra-dec two-pack for this component's direction""";
    radec = self.ns.radec("sp");
    if not radec.initialized():
      radec << Meq.Selector(self.sixpack(),index=(0,1),multi=True);
    return radec;
    
  def uvbrick (self):
    brick = self.ns.uvbrick;
    if not brick.initialized():
      brick << Meq.FFTBrick(Meq.Stokes(self.iquv()),
        axes_in=(hiid('l'),hiid('m')),axes_out=(hiid('u'),hiid('v')),
        uvppw=self._fft_pad_factor);
    return brick;
    
  def make_visibilities (self,nodes,array,observation):
    # create a brick
    brick = self.uvbrick();
    uvw = array.uvw_ifr(observation.radec0());
    for ifr in array.ifrs():
      nodes(*ifr) << Meq.UVInterpolWave(brick=brick,uvw=uvw(*ifr),
                        method=self._interpol_method,
                        additional_info=self._interpol_debug);