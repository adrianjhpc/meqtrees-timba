# file: ../Grunt/Visset22.py

# History:
# - 05jan2007: creation (from JEN_SolverChain.py)

# Description:

# The Visset22 class encapsulates a set of 2x2 cohaerency matrices,
# i.e. visbilities. 

#======================================================================================

from Timba.TDL import *
from Timba.Meq import meq

from Timba.Contrib.JEN.Grunt import Matrixet22

from Timba.Contrib.JEN.util import JEN_bookmarks
from Timba.Contrib.JEN import MG_JEN_dataCollect

from copy import deepcopy

# For testing only:
import Meow
from Timba.Contrib.JEN.Grunt import Joneset22



# Global counter used to generate unique node-names
# unique = -1


#======================================================================================

class Visset22 (Matrixet22.Matrixet22):
    """Class that represents a set of 2x2 Cohaerency  matrices"""

    def __init__(self, ns, quals=[], label='<v>',
                 cohset=None, array=None,
                 # observation=None,
                 polrep=None,
                 simulate=False):

        # Interface with Meow system (array, cohset, observation):
        self._array = array                          # Meow IfrArray object
        # self._observation = observation              # Meow Observation object

        # Initialise its Matrixet22 object:
        Matrixet22.Matrixet22.__init__(self, ns, quals=quals, label=label,
                                       polrep=polrep, 
                                       indices=self._array.ifrs(),
                                       simulate=simulate)
        if cohset:
            self._matrixet = cohset
        else:
            quals = self.quals()
            node = self._ns.unity(*quals) << Meq.Matrix22(complex(1.0),complex(0.0),
                                                          complex(0.0),complex(1.0))
            self._matrixet = self._ns.initial(*quals)
            for ifr in self.ifrs():
                self._matrixet(*ifr) << Meq.Identity(node)

        # Some specific Visset22 attributes:
        self._MS_corr_index = [0,1,2,3]                # see make_spigots/make_sinks

        return None

    #-------------------------------------------------------------------

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = str(type(self))
        ss += '  '+str(self.label())
        ss += '  pols='+str(self._pols)
        ss += '  n='+str(len(self.stations()))
        ss += '  quals='+str(self.quals())
        return ss


    def display_specific(self, full=False):
        """Print the specific part of the summary of this object"""
        print '   - MS_corr_index: '+str(self._MS_corr_index)
        return True

    #--------------------------------------------------------------------------

    def stations(self):
        """Return a list of (array) stations"""
        return self._array.stations()                # Meow IfrArray            

    def ifrs (self, select='all'):
        """Get a selection of self._array.ifrs()"""
        return self.indices()                        # Meow IfrArray.ifrs()


    #--------------------------------------------------------------------------
    # Operations on the internal self._matrixet:
    #--------------------------------------------------------------------------


    def insert_accumulist_reqseq (self, key=None, qual=None):
        """Insert a series of reqseq node(s) with the children accumulated
        in self._accumulist (see Matrixet22). The reqseqs will get the current
        matrix nodes as their last child, to which their result is transmitted."""

        cc = self.accumulist(key=key, clear=False)
        n = len(cc)
        if n>0:
            quals = self.quals(append=qual)
            cc.append('placeholder')
            name = 'reqseq'
            if isinstance(key, str): name += '_'+str(key)
            for ifr in self.ifrs():
                cc[n] = self._matrixet(*ifr)         # fill in the placeholder
                self._ns[name](*quals)(*ifr) << Meq.ReqSeq(children=cc, result_index=n,
                                                           cache_num_active_parents=1)
            self._matrixet = self._ns[name](*quals)
        return True

    #--------------------------------------------------------------------------

    def make_spigots (self, input_col='DATA', MS_corr_index=[0,1,2,3], flag_bit=4):
        """Make MeqSpigot nodes per ifr, for reading visibility data from the
        specified column of the Measurement Set (or other data source).
        The input_col can be 'DATA','CORRECTED_DATA','MODEL_DATA','RESIDUALS'
        For XX/YY only, use:
          - If only XX/YY available: MS_corr_index = [0,-1,-1,1]
          - If all 4 corr available: MS_corr_index = [0,-1,-1,3]
          - etc
        For missing corrs, the spigot still returns a 2x2 tensor node, but with
        empty results {}. These are interpreted as zeroes, e.g. in matrix
        multiplication. After that, the results ar no longer empty, so that cannot
        be used for detecting missing corrs! Empty results are ignored by condeqs etc
        See also the wiki-pages...
        """

        self._MS_corr_index = MS_corr_index    # Keep. See also .make_sinks()

        for p,q in self.ifrs():
            self._ns.spigot(p,q) << Meq.Spigot(station_1_index=p-1,
                                               station_2_index=q-1,
                                               # corr_index=self._MS_corr_index,
                                               # flag_bit=flag_bit,
                                               input_column=input_col)
        self._matrixet = self._ns.spigot           
        return True

    #--------------------------------------------------------------------------

    def make_sinks (self, output_col='RESIDUALS',
                    # start=None, pre=None, post=None,
                    vdm='vdm'):
        """Make MeqSink nodes per ifr for writing visibilities back to the MS.
        These are the children of a single VisDataMux node, which issues the
        series of requests that traverse the data. The keyword vdm (default='vdm')
        supplies the name of the VisDataMux node, which is needed for executing the tree."""

        for p,q in self.ifrs():
            self._ns.sink(p,q) << Meq.Sink(self._matrixet(p,q),
                                           station_1_index=p-1,
                                           station_2_index=q-1,
                                           # corr_index=self._MS_corr_index,
                                           output_col=output_col)
        self._matrixet = self._ns.sink
        
        # The single VisDataMux node is the actual interface node.
        # See also TDL_Cohset.py for use of start/pre/post.
        self._ns[vdm] << Meq.VisDataMux(*[self._ns.sink(*ifr) for ifr in self.ifrs()]);

        # Return the actual name of the VisDataMux (needed for tree execution)
        return vdm


    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------

    def addNoise (self, rms=0.1, qual=None, visu=True):
        """Add gaussian noise with given rms to the internal cohset"""
        quals = self.quals(append=qual)
        name = 'addNoise22'
        matrels = self.matrels()
        for ifr in self.ifrs():
            mm = range(4)
            for i in range(4):
                m = matrels[i]
                rnoise = self._ns.rnoise(*quals)(*ifr)(m) << Meq.GaussNoise(stddev=rms)
                inoise = self._ns.inoise(*quals)(*ifr)(m) << Meq.GaussNoise(stddev=rms)
                mm[i] = self._ns.noise(*quals)(*ifr)(m) << Meq.ToComplex(rnoise,inoise)
            noise = self._ns.noise(*quals)(*ifr) << Meq.Matrix22(*mm)
            self._ns[name](*quals)(*ifr) << Meq.Add(self._matrixet(*ifr),noise)
        self._matrixet = self._ns[name](*quals)           
        if visu: return self.visualize(name)
        return None

    #...........................................................................

    def corrupt (self, joneset=None, qual=None, visu=False):
        """Corrupt the internal matrices with the matrices of the given Joneset22 object.
        Transfer the parmgroups of the Joneset22 to its own ParmGroupManager (pgm)."""
        quals = self.quals(append=qual)
        name = 'corrupt22'
        jmat = joneset.matrixet() 
        for ifr in self.ifrs():
            j1 = jmat(ifr[0])
            j2c = jmat(ifr[1])('conj') ** Meq.ConjTranspose(jmat(ifr[1])) 
            self._ns[name](*quals)(*ifr) << Meq.MatrixMultiply(j1,self._matrixet(*ifr),j2c)
        self._matrixet = self._ns[name](*quals)              
        # Transfer any parmgroups (used by the solver downstream)
        self._pgm.merge(joneset._pgm)
        if visu: return self.visualize(name)
        return None

    #...........................................................................

    def correct (self, joneset=None, qual=None, visu=False):
        """Correct the internal matrices with the matrices of the given Joneset22 object."""
        quals = self.quals(append=qual)
        name = 'correct22'
        jmat = joneset.matrixet()
        for ifr in self.ifrs():
            j1i = jmat(ifr[0])('inv') ** Meq.MatrixInvert22(jmat(ifr[0]))
            j2c = jmat(ifr[1])('conj') ** Meq.ConjTranspose(jmat(ifr[1])) 
            j2ci = j2c('inv') ** Meq.MatrixInvert22(j2c)
            self._ns[name](*quals)(*ifr) << Meq.MatrixMultiply(j1i,self._matrixet(*ifr),j2ci)
        self._matrixet = self._ns[name](*quals)              
        # Transfer any accumulist entries (e.g. visualisation dcolls etc)
        # self.merge_accumulist(joneset)
        if visu: return self.visualize(name)
        return None






#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []

    num_stations = 3
    ANTENNAS = range(1,num_stations+1)
    array = Meow.IfrArray(ns,ANTENNAS)

    cohset = None
    if False:
        observation = Meow.Observation(ns)
        allsky = Meow.Patch(ns, 'nominall', observation.phase_centre)
        l = 1.0
        m = 1.0
        src = '3c84'
        src_dir = Meow.LMDirection(ns, src, l, m)
        source = Meow.PointSource(ns, src, src_dir, I=1.0, Q=0.1, U=-0.1, V=0.01)
        allsky.add(source)
        cohset = allsky.visibilities(array, observation)
    vis = Visset22(ns, label='test', quals='yyc', array=array, cohset=cohset)
    vis.display('initial')

    if True:
        G = Joneset22.GJones(ns, stations=array.stations(), simulate=True)
        D = Joneset22.DJones(ns, stations=array.stations(), simulate=True)
        jones = G
        jones = D
        jones = Joneset22.Joneseq22([G,D])
        vis.corrupt(jones, visu=True)
        vis.addNoise(rms=0.05, visu=True)
        vis.display('after corruption')
        if False:
            vis.correct(jones, visu=True)

    if True:
        pred = Visset22(ns, label='nominal', quals='xxc', array=array, cohset=cohset)
        pred.display('initial')
        G = Joneset22.GJones(ns, stations=array.stations(), simulate=False)
        D = Joneset22.DJones(ns, stations=array.stations(), simulate=False)
        jones = G
        jones = D
        jones = Joneset22.Joneseq22([G,D])
        pred.corrupt(jones, visu=True)
        vis.display('after corruption')
        vis.make_solver(pred, parmgroup='*')
        # vis.make_solver(pred, parmgroup='Ggain')
        if True:
            vis.correct(jones, visu=True)

    if True:
        vis.insert_accumulist_reqseq()
  
    # vis.display('final')
    cc.append(vis.bundle())

    ns.result << Meq.ReqSeq(children=cc)
    return True

#---------------------------------------------------------------

def _tdl_job_execute (mqs, parent):
    """Execute the forest, starting at the named node"""
    domain = meq.domain(1.0e8,1.1e8,1,10)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=10, num_time=11)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       



#=======================================================================
# Test program (standalone):
#=======================================================================

if __name__ == '__main__':
    ns = NodeScope()

    if 1:
        import Meow
        num_stations = 3
        ANTENNAS = range(1,num_stations+1)
        array = Meow.IfrArray(ns,ANTENNAS)
        observation = Meow.Observation(ns)
        cohset = None
        if False:
            allsky = Meow.Patch(ns, 'nominall', observation.phase_centre)
            l = 1.0
            m = 1.0
            src = '3c84'
            src_dir = Meow.LMDirection(ns, src, l, m)
            source = Meow.PointSource(ns, src, src_dir, I=1.0, Q=0.1, U=-0.1, V=0.01)
            allsky.add(source)
            cohset = allsky.visibilities(array, observation)
        vis = Visset22(ns, label='test', array=array, cohset=cohset)
        vis.display()

    if 1:
        G = Joneset22.GJones (ns, stations=array.stations(), simulate=True)
        vis.corrupt(G, visu=True)
        # vis.addNoise(rms=0.05, visu=True)
        vis.correct(G, visu=True)
        vis.display('after corruption')

    if 1:
        vis.insert_accumulist_reqseq()
        vis.display(full=True)
        

    if 0:
        G = Joneset22.GJones (ns, stations=array.stations(), simulate=True)
        D = Joneset22.DJones (ns, stations=array.stations(), simulate=True)
        jones = Joneset22.Joneseq22([G,D])
        vis.corrupt(jones, visu=True)
        vis.display('after corruption')


#=======================================================================
# Remarks:

#=======================================================================
