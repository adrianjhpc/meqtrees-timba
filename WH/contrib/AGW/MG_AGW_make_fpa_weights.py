#!/usr/bin/python

#
# Copyright (C) 2007
# ASTRON (Netherlands Foundation for Research in Astronomy)
# and The MeqTree Foundation
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
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
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# Short description:
# We read in a group of focal plane array beams, 
# and form a combined, weighted beam. The weights
# are found by getting complex values at specified
# L,M location in the X (|| poln) beams and then
# taking the conjugate transpose.

# We use these weights as an initial starting guess for the
# weights to be used to obtain a nice Gaussian beam. These weights
# are given to the solver, which then proceeds to solve for
# the optimum weights.

# History:
# - 27 Feb 2007: creation:

#=======================================================================
# Import of Python / TDL modules:

# Get TDL and Meq for the Kernel
from Timba.TDL import * 
from Timba.Meq import meqds
from Timba.Meq import meq
from Meow import Bookmarks,Utils

from numarray import *
import os

#setup a bookmark for display of results with a 'Collections Plotter'
Settings.forest_state = record(bookmarks=[
  record(name='Condeqs',page=[
    record(udi="/node/IQUV_complex",viewer="Result Plotter",pos=(2,0)),
    record(udi="/node/condeq",viewer="Result Plotter",pos=(1,0))])]);
# to force caching put 100
#Settings.forest_state.cache_policy = 100

def create_polc(c00=0.0,degree_f=0,degree_t=0):
  """helper function to create a t/f polc with the given c00 coefficient,
  and with given order in t/f""";
  polc = meq.polc(zeros((degree_t+1, degree_f+1))*0.0);
  polc.coeff[0,0] = c00;
  return polc;

def tpolc (tdeg,c00=0.0):
  return Meq.Parm(create_polc(degree_f=0,degree_t=tdeg,c00=c00),
                  node_groups='Parm')
#                 constrain = [-5.0,5.0])

########################################################
def _define_forest(ns):  

  # define location for phase-up
# BEAM_LM = [(0.0,0.0)]
  BEAM_LM = [(0.04,0.04)]
  l_beam,m_beam = BEAM_LM[0]
  ns.l_beam_c << Meq.Constant(l_beam) 
  ns.m_beam_c << Meq.Constant(m_beam)

  # constant for half-intensity determination
  ns.ln_16 << Meq.Constant(-2.7725887)

  # define desired half-intensity width of power pattern (HPBW)
  # as we are fitting total intensity I pattern
  ns.width << Meq.Constant(0.021747)                 

  laxis = ns.laxis << Meq.Grid(axis=2);
  maxis = ns.maxis << Meq.Grid(axis=3);

  # gaussian to which we want to optimize beams
  ns.lm_x_sq << Meq.Sqr(laxis - ns.l_beam_c) + Meq.Sqr(maxis - ns.m_beam_c)
  ns.gaussian << Meq.Exp((ns.lm_x_sq * ns.ln_16)/Meq.Sqr(ns.width));

  ns.lm_beam << Meq.Composer(ns.l_beam_c,ns.m_beam_c);

# read in beam images
 # fit all 30 beams
  BEAMS = range(0,30)
  home_dir = os.environ['HOME']
  # read in beam data
  beam_solvables = []
  parm_solvables = []
  parm_condeqs = []
  for k in BEAMS:
  # read in beam data - y dipole
    infile_name_re_yx = home_dir + '/Timba/WH/contrib/AGW/veidt_fpa/fpa_pat_' + str(k+30) + '_Re_x.fits'
    infile_name_im_yx = home_dir + '/Timba/WH/contrib/AGW/veidt_fpa/fpa_pat_' + str(k+30) +'_Im_x.fits'
    infile_name_re_yy = home_dir + '/Timba/WH/contrib/AGW/veidt_fpa/fpa_pat_' + str(k+30) +'_Re_y.fits'
    infile_name_im_yy = home_dir + '/Timba/WH/contrib/AGW/veidt_fpa/fpa_pat_' + str(k+30) +'_Im_y.fits' 
    ns.image_re_yx(k) << Meq.FITSImage(filename=infile_name_re_yx,cutoff=1.0,mode=2)
    ns.image_im_yx(k) << Meq.FITSImage(filename=infile_name_im_yx,cutoff=1.0,mode=2)
    ns.image_re_yy(k) << Meq.FITSImage(filename=infile_name_re_yy,cutoff=1.0,mode=2)
    ns.image_im_yy(k) << Meq.FITSImage(filename=infile_name_im_yy,cutoff=1.0,mode=2)
    # normalize
    ns.y_im_sq(k) << ns.image_re_yy(k) * ns.image_re_yy(k) + ns.image_im_yy(k) * ns.image_im_yy(k) +\
                  ns.image_re_yx(k) * ns.image_re_yx(k) + ns.image_im_yx(k) * ns.image_im_yx(k)
    ns.y_im(k) <<Meq.Sqrt(ns.y_im_sq(k))
    ns.y_im_max(k) <<Meq.Max(ns.y_im(k))
    ns.norm_image_re_yy(k) << ns.image_re_yy(k) / ns.y_im_max(k)
    ns.norm_image_im_yy(k) << ns.image_im_yy(k) / ns.y_im_max(k)
    ns.norm_image_re_yx(k) << ns.image_re_yx(k) / ns.y_im_max(k)
    ns.norm_image_im_yx(k) << ns.image_im_yx(k) / ns.y_im_max(k)

    ns.resampler_image_re_yy(k) << Meq.Resampler(ns.norm_image_re_yy(k),dep_mask = 0xff)
    ns.resampler_image_im_yy(k) << Meq.Resampler(ns.norm_image_im_yy(k),dep_mask = 0xff)
    ns.sample_wt_re_y(k) << Meq.Compounder(children=[ns.lm_beam,ns.resampler_image_re_yy(k)],common_axes=[hiid('l'),hiid('m')])
    ns.sample_wt_im_y(k) << -1.0 * Meq.Compounder(children=[ns.lm_beam,ns.resampler_image_im_yy(k)],common_axes=[hiid('l'),hiid('m')])
    # I want to solve for these parameters
    ns.beam_wt_re_y(k) << tpolc(0)
    ns.beam_wt_im_y(k) << tpolc(0)
    parm_solvables.append(ns.beam_wt_re_y(k))
    parm_solvables.append(ns.beam_wt_im_y(k))
    beam_solvables.append(ns.beam_wt_re_y(k))
    beam_solvables.append(ns.beam_wt_im_y(k))
    # we need to assign the weights we've extracted as initial guesses
    # to the Parm - can only be done by solving
    ns.condeq_wt_re_y(k) << Meq.Condeq(children=(ns.sample_wt_re_y(k), ns.beam_wt_re_y(k)))
    ns.condeq_wt_im_y(k) << Meq.Condeq(children=(-1.0 * ns.sample_wt_im_y(k), ns.beam_wt_im_y(k)))
    parm_condeqs.append(ns.condeq_wt_re_y(k))
    parm_condeqs.append(ns.condeq_wt_im_y(k))


    ns.beam_weight_y(k) << Meq.ToComplex(ns.beam_wt_re_y(k), ns.beam_wt_im_y(k))

    ns.beam_yx(k) << Meq.ToComplex(ns.norm_image_re_yx(k), ns.norm_image_im_yx(k)) 
    ns.beam_yy(k) << Meq.ToComplex(ns.norm_image_re_yy(k), ns.norm_image_im_yy(k))
    ns.wt_beam_yx(k) << ns.beam_yx(k) * ns.beam_weight_y(k)
    ns.wt_beam_yy(k) << ns.beam_yy(k) * ns.beam_weight_y(k)

  # read in beam data - x dipole
    infile_name_re_xx = home_dir + '/Timba/WH/contrib/AGW/veidt_fpa/fpa_pat_' + str(k) + '_Re_x.fits'
    infile_name_im_xx = home_dir + '/Timba/WH/contrib/AGW/veidt_fpa/fpa_pat_' + str(k) +'_Im_x.fits'
    infile_name_re_xy = home_dir + '/Timba/WH/contrib/AGW/veidt_fpa/fpa_pat_' + str(k) +'_Re_y.fits'
    infile_name_im_xy = home_dir + '/Timba/WH/contrib/AGW/veidt_fpa/fpa_pat_' + str(k) +'_Im_y.fits' 
    ns.image_re_xy(k) << Meq.FITSImage(filename=infile_name_re_xy,cutoff=1.0,mode=2)
    ns.image_im_xy(k) << Meq.FITSImage(filename=infile_name_im_xy,cutoff=1.0,mode=2)
    ns.image_re_xx(k) << Meq.FITSImage(filename=infile_name_re_xx,cutoff=1.0,mode=2)
    ns.image_im_xx(k) << Meq.FITSImage(filename=infile_name_im_xx,cutoff=1.0,mode=2)

    # normalize
    ns.x_im_sq(k) << ns.image_re_xx(k) * ns.image_re_xx(k) + ns.image_im_xx(k) * ns.image_im_xx(k) +\
                  ns.image_re_xy(k) * ns.image_re_xy(k) + ns.image_im_xy(k) * ns.image_im_xy(k)
    ns.x_im(k) <<Meq.Sqrt(ns.x_im_sq(k))
    ns.x_im_max(k) <<Meq.Max(ns.x_im(k))
    ns.norm_image_re_xx(k) << ns.image_re_xx(k) / ns.x_im_max(k)
    ns.norm_image_im_xx(k) << ns.image_im_xx(k) / ns.x_im_max(k)
    ns.norm_image_re_xy(k) << ns.image_re_xy(k) / ns.x_im_max(k)
    ns.norm_image_im_xy(k) << ns.image_im_xy(k) / ns.x_im_max(k)
    ns.resampler_image_re_xx(k) << Meq.Resampler(ns.norm_image_re_xx(k),dep_mask = 0xff)
    ns.resampler_image_im_xx(k) << Meq.Resampler(ns.norm_image_im_xx(k),dep_mask = 0xff)
    ns.sample_wt_re_x(k) << Meq.Compounder(children=[ns.lm_beam,ns.resampler_image_re_xx(k)],common_axes=[hiid('l'),hiid('m')])
    ns.sample_wt_im_x(k) << Meq.Compounder(children=[ns.lm_beam,ns.resampler_image_im_xx(k)],common_axes=[hiid('l'),hiid('m')])
    # I want to solve for these parameters
    ns.beam_wt_re_x(k) << tpolc(0)
    ns.beam_wt_im_x(k) << tpolc(0)
    parm_solvables.append(ns.beam_wt_re_x(k))
    parm_solvables.append(ns.beam_wt_im_x(k))
    beam_solvables.append(ns.beam_wt_re_x(k))
    beam_solvables.append(ns.beam_wt_im_x(k))
    ns.condeq_wt_re_x(k) << Meq.Condeq(children=(ns.sample_wt_re_x(k), ns.beam_wt_re_x(k)))
    ns.condeq_wt_im_x(k) << Meq.Condeq(children=(-1.0 * ns.sample_wt_im_x(k), ns.beam_wt_im_x(k)))
    parm_condeqs.append(ns.condeq_wt_re_x(k))
    parm_condeqs.append(ns.condeq_wt_im_x(k))

    ns.beam_weight_x(k) << Meq.ToComplex(ns.beam_wt_re_x(k), ns.beam_wt_im_x(k))

    ns.beam_xy(k) << Meq.ToComplex(ns.norm_image_re_xy(k), ns.norm_image_im_xy(k)) 
    ns.beam_xx(k) << Meq.ToComplex(ns.norm_image_re_xx(k), ns.norm_image_im_xx(k))
    ns.wt_beam_xy(k) << ns.beam_xy(k) * ns.beam_weight_x(k)
    ns.wt_beam_xx(k) << ns.beam_xx(k) * ns.beam_weight_x(k)

  # solver to 'copy' resampled beam locations to parms as
  # first guess
  ns.solver_parms <<Meq.Solver(children= parm_condeqs,mt_polling=False,num_iter=3,epsilon=1e-4,solvable= parm_solvables)

  ns.voltage_sum_xx << Meq.Add(*[ns.wt_beam_xx(k) for k in BEAMS])
  ns.voltage_sum_xy << Meq.Add(*[ns.wt_beam_xy(k) for k in BEAMS])
  ns.voltage_sum_yx << Meq.Add(*[ns.wt_beam_yx(k) for k in BEAMS])
  ns.voltage_sum_yy << Meq.Add(*[ns.wt_beam_yy(k) for k in BEAMS])

  # normalize beam to peak response
  ns.voltage_sum_xx_r << Meq.Real(ns.voltage_sum_xx)
  ns.voltage_sum_xx_i << Meq.Imag(ns.voltage_sum_xx)
  ns.voltage_sum_xy_r << Meq.Real(ns.voltage_sum_xy)
  ns.voltage_sum_xy_i << Meq.Imag(ns.voltage_sum_xy)

  ns.im_sq_x << ns.voltage_sum_xx_r * ns.voltage_sum_xx_r + ns.voltage_sum_xx_i * ns.voltage_sum_xx_i +\
                  ns.voltage_sum_xy_r * ns.voltage_sum_xy_r + ns.voltage_sum_xy_i * ns.voltage_sum_xy_i
  ns.im_x <<Meq.Sqrt(ns.im_sq_x)
  ns.im_x_max <<Meq.Max(ns.im_x)
  ns.im_x_norm << ns.im_x / ns.im_x_max

  ns.voltage_sum_yy_r << Meq.Real(ns.voltage_sum_yy)
  ns.voltage_sum_yy_i << Meq.Imag(ns.voltage_sum_yy)
  ns.voltage_sum_yx_r << Meq.Real(ns.voltage_sum_yx)
  ns.voltage_sum_yx_i << Meq.Imag(ns.voltage_sum_yx)
  ns.im_sq_y << ns.voltage_sum_yy_r * ns.voltage_sum_yy_r + ns.voltage_sum_yy_i * ns.voltage_sum_yy_i +\
                  ns.voltage_sum_yx_r * ns.voltage_sum_yx_r + ns.voltage_sum_yx_i * ns.voltage_sum_yx_i
  ns.im_y <<Meq.Sqrt(ns.im_sq_y)
  ns.im_y_max <<Meq.Max(ns.im_y)
  ns.im_y_norm << ns.im_y / ns.im_y_max

  ns.voltage_sum_yy_norm << ns.voltage_sum_yy / ns.im_y_max
  ns.voltage_sum_yx_norm << ns.voltage_sum_yx / ns.im_y_max

  ns.voltage_sum_xx_norm << ns.voltage_sum_xx / ns.im_x_max
  ns.voltage_sum_xy_norm << ns.voltage_sum_xy / ns.im_x_max


  ns.E << Meq.Matrix22(ns.voltage_sum_xx_norm, ns.voltage_sum_yx_norm,ns.voltage_sum_xy_norm, ns.voltage_sum_yy_norm)
  ns.Et << Meq.ConjTranspose(ns.E)

 # sky brightness
  ns.B0 << 0.5 * Meq.Matrix22(1.0, 0.0, 0.0, 1.0)

  # observe!
  ns.observed << Meq.MatrixMultiply(ns.E, ns.B0, ns.Et)

  # extract I,Q,U,V etc
  ns.IpQ << Meq.Selector(ns.observed,index=0)        # XX = (I+Q)/2
  ns.ImQ << Meq.Selector(ns.observed,index=3)        # YY = (I-Q)/2
  ns.I << Meq.Add(ns.IpQ,ns.ImQ)                     # I = XX + YY
  ns.Q << Meq.Subtract(ns.IpQ,ns.ImQ)                # Q = XX - YY

  ns.UpV << Meq.Selector(ns.observed,index=1)        # XY = (U+iV)/2
  ns.UmV << Meq.Selector(ns.observed,index=2)        # YX = (U-iV)/2
  ns.U << Meq.Add(ns.UpV,ns.UmV)                     # U = XY + YX
  ns.iV << Meq.Subtract(ns.UpV,ns.UmV)               # iV = XY - YX  <----!!
  ns.V << ns.iV / 1j                                 # V = iV / i
                                                     # (note: i => j in Python)

  # join together into one node in order to make a single request
  ns.IQUV_complex << Meq.Composer(ns.I, ns.Q,ns.U, ns.V)
  ns.IQUV << Meq.Real(ns.IQUV_complex)
  ns.Ins_pol << ns.IQUV / ns.I

  ns.I_real << Meq.Selector(ns.IQUV,index=0)
  ns.resampler_I << Meq.Resampler(ns.I_real)

  ns.condeq<<Meq.Condeq(children=(ns.resampler_I, ns.gaussian))
  ns.solver<<Meq.Solver(ns.condeq,num_iter=20,mt_polling=False,epsilon=1e-4,solvable=beam_solvables)

# ns.req_seq<<Meq.ReqMux(ns.solver_parms, ns.solver(0), ns.solver(1), ns.Ins_pol)
  ns.req_seq<<Meq.ReqSeq(ns.solver_parms, ns.solver, ns.Ins_pol)

  # Note: we are observing with linearly-polarized dipoles. If we
  # want the aips++ imager to generate images in the sequence I,Q,U,V
  # make sure that the newsimulator setspwindow method uses
  # stokes='XX XY YX YY' and not stokes='RR RL LR LL'. If you
  # do the latter you will get the images rolled out in the
  # order I,U,V,Q!

########################################################################
def _test_forest(mqs,parent):

# any large time range will do
  t0 = 0.0;
  t1 = 1.5e70

  f0 = 0.5
  f1 = 1.5

  lm_range = [-0.15,0.15];
  lm_num = 50;
  counter = 0
  request = make_request(counter=counter, dom_range = [[f0,f1],[t0,t1],lm_range,lm_range], nr_cells = [1,1,lm_num,lm_num])
# execute request
  mqs.meq('Node.Execute',record(name='req_seq',request=request),wait=True);

#####################################################################
def make_request(counter=0,Ndim=4,dom_range=[0.,1.],nr_cells=5):

    """make multidimensional request, dom_range should have length 2 or be a list of
    ranges with length Ndim, nr_cells should be scalar or list of scalars with length Ndim"""
    forest_state=meqds.get_forest_state();
    axis_map=forest_state.axis_map;
    
    range0 = [];
    if is_scalar(dom_range[0]):
        for i in range(Ndim):		
            range0.append(dom_range);
    else:
        range0=dom_range;
    nr_c=[];
    if is_scalar(nr_cells):
        for i in range(Ndim):		
            nr_c.append(nr_cells);
    else:
        nr_c =nr_cells;
    dom = meq.domain(range0[0][0],range0[0][1],range0[1][0],range0[1][1]); #f0,f1,t0,t1
    cells = meq.cells(dom,num_freq=nr_c[0],num_time=nr_c[1]);
    
    # workaround to get domain with more axes running 

    for dim in range(2,Ndim):
        id = axis_map[dim].id;
        if id:
            dom[id] = [float(range0[dim][0]),float(range0[dim][1])];
            step_size=float(range0[dim][1]-range0[dim][0])/nr_c[dim];
            startgrid=0.5*step_size+range0[dim][0];
            grid = [];
            cell_size=[];
        for i in range(nr_c[dim]):
            grid.append(i*step_size+startgrid);
            cell_size.append(step_size);
            cells.cell_size[id]=array(cell_size);
            cells.grid[id]=array(grid);
            cells.segments[id]=record(start_index=0,end_index=nr_c[dim]-1);

    cells.domain=dom;
    rqid = meq.requestid(domain_id=counter)
    request = meq.request(cells,rqtype='ev',rqid=rqid);
    return request;

if __name__=='__main__':
  ns=NodeScope()
  _define_forest(ns)
  ns.Resolve()
  print "Added %d nodes" % len(ns.AllNodes())
  
