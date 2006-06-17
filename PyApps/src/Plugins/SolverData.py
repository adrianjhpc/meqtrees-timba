#!/usr/bin/env python

import sys
from numarray import *

from Timba.utils import verbosity
_dbg = verbosity(0,name='SolverData');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

class SolverData:
   """ a class to store solver data and supply the
       data to the browser display """

   def __init__(self, data_label=''):
     self._data_label = data_label
     self._solver_array = None
     self.metrics_rank = None
     self.metrics_chi_0 = None
     self.solver_offsets = None
     self.metrics_unknowns = None
     self.chi_array = None
     self.vector_sum = None
     self.incr_soln_norm = None
     self.sum_incr_soln_norm = None
     self.nonlin = None
     self.prev_unknowns = 0
     self.iteration_number = None
#    self.__init__

   def StoreSolverData(self, incoming_data, data_label=''):
     """ This method stores the data """
     self._data_label = data_label
     if incoming_data.solver_result.has_key("incremental_solutions"):
       self._solver_array = incoming_data.solver_result.incremental_solutions
       self.chi_array = self._solver_array.copy()
       shape = self._solver_array.shape
       #shape[0] = number of interations == num_metrics (see below)
       #shape[1] = total number of solution elements
       if incoming_data.solver_result.has_key("metrics"):
         metrics = incoming_data.solver_result.metrics
# find out how many records in each metric field
         num_metrics = len(metrics)
         num_metrics_rec =  len(metrics[0])
         self.solver_offsets = zeros((num_metrics_rec), Int32)
         self.metrics_rank = zeros((num_metrics,num_metrics_rec), Int32)
         self.metrics_unknowns = zeros((num_metrics,num_metrics_rec), Int32)
         self.metrics_chi_0 = zeros((num_metrics,num_metrics_rec), Float64)
         self.metrics_chi = zeros((num_metrics,num_metrics_rec), Float64)
         self.metrics_fit = zeros((num_metrics,num_metrics_rec), Float64)
         self.metrics_mu = zeros((num_metrics,num_metrics_rec), Float64)
         self.metrics_stddev = zeros((num_metrics,num_metrics_rec), Float64)
         self.metrics_flag = zeros((num_metrics,num_metrics_rec), Bool)
         self.vector_sum = zeros((num_metrics,num_metrics_rec), Float64)
         self.incr_soln_norm = zeros((num_metrics,num_metrics_rec), Float64)
         self.sum_incr_soln_norm = zeros((num_metrics,num_metrics_rec), Float64)
         self.iteration_number = zeros((num_metrics), Int32)
         for i in range(num_metrics):
           if i > 0:
             for j in range(shape[1]):
               self.chi_array[i,j] = self.chi_array[i,j] + self.chi_array[i-1,j]
           self.prev_unknowns = 0
           for j in range(num_metrics_rec):
             metrics_rec =  metrics[i][j]
             try:
               self.metrics_chi_0[i,j] = metrics_rec.chi_0 
               self.metrics_fit[i,j] = metrics_rec.fit 
               self.metrics_chi[i,j] = metrics_rec.chi 
               self.metrics_mu[i,j] = metrics_rec.mu 
               self.metrics_flag[i,j] = metrics_rec.flag 
               self.metrics_stddev[i,j] = metrics_rec.stddev 
               sum_array = 0.0
               sum_array_test = 0.0
               for k in range(self.prev_unknowns,self.prev_unknowns + metrics_rec.num_unknowns):
                  sum_array_test = sum_array_test + self.chi_array[i,k] * self.chi_array[i,k]
                  self.vector_sum[i,j] = self.vector_sum[i,j] + self.chi_array[i,k] * self.chi_array[i,k]
                  sum_array = sum_array + self._solver_array[i,k] * self._solver_array[i,k]
               self.vector_sum[i,j] = sqrt(self.vector_sum[i,j])
               self.incr_soln_norm[i,j] = sqrt(sum_array)
               if i == 0:
                 self.sum_incr_soln_norm[i,j] = self.sum_incr_soln_norm[i,j] + self.incr_soln_norm[i,j] 
               else:
                 self.sum_incr_soln_norm[i,j] = self.sum_incr_soln_norm[i-1,j] + self.incr_soln_norm[i,j] 
               self.metrics_rank[i,j] = metrics_rec.rank +self.prev_unknowns
               self.prev_unknowns = self.prev_unknowns + metrics_rec.num_unknowns
               self.metrics_unknowns[i,j] = metrics_rec.num_unknowns 
               if i == 0:
                 self.solver_offsets[j] = self.prev_unknowns
             except:
               pass
           self.iteration_number[i] = i+1
       if incoming_data.solver_result.has_key("debug_array"):
         debug_array = incoming_data.solver_result.debug_array
# find out how many records in each metric field
         num_debug = len(debug_array)
         num_nonlin =  len(debug_array[0].nonlin)
         self.nonlin = zeros((num_nonlin, num_debug), Float64)
         for j in range(num_debug):
           debug_rec = debug_array[j]
           nonlin = debug_rec.nonlin
           for i in range(num_nonlin):
             self.nonlin[i,j] = debug_rec.nonlin[i]

   def getSolverData(self):
     return self._solver_array

   def getSolverMetrics(self):
     return (self.metrics_rank, self.iteration_number, self.solver_offsets, self.vector_sum, self.metrics_chi_0, self.nonlin, self.sum_incr_soln_norm, self.incr_soln_norm, self.metrics_fit, self.metrics_chi, self.metrics_mu, self.metrics_flag, self.metrics_stddev,self.metrics_unknowns)

def main(args):
  print 'we are in main' 

# Admire
if __name__ == '__main__':
    main(sys.argv)

