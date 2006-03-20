#!/usr/bin/python
#############################################
# A simple class to implement coordinate transformations such as
# projections
#############################################

import math
## class to implement projection
class Projector:
  '''This class will perform spherical to rectangular projections
     and vice-versa. It needs the coordinates of the phase center
     in (RA,Dec)
     __ra0,__dec0:coordinates of the phase centre
     __p=rotation angle, default is 0
  '''
  def __init__(self,ra0,dec0,rot=0):
    self.__ra0=ra0
    self.__dec0=dec0
    self.__p=rot
    self.__state=1 # on (1),off (0) projection

  # calculation of the bounds in l,m
  def give_limits(self,min_ra,max_ra,min_dec,max_dec):
   # set to default values 
   x_min=y_min=1000000
   x_max=y_max=-1000000

   #print (x_min,x_max,y_min,y_max)
   # now consider local maxima,minima
   npoints=10

   delta=(max_ra-min_ra)/npoints
   for i in range(0,npoints+1):
    pcoord=min_ra+i*delta
    tmp_val=self.sp_to_rt(pcoord,min_dec)
    if x_min>tmp_val[0]: x_min=tmp_val[0] 
    elif x_max<tmp_val[0]: x_max=tmp_val[0] 
    if y_min>tmp_val[1]: y_min=tmp_val[1] 
    elif y_max<tmp_val[1]: y_max=tmp_val[1] 
    tmp_val=self.sp_to_rt(pcoord,max_dec)
    if x_min>tmp_val[0]: x_min=tmp_val[0] 
    elif x_max<tmp_val[0]: x_max=tmp_val[0] 
    if y_min>tmp_val[1]: y_min=tmp_val[1] 
    elif y_max<tmp_val[1]: y_max=tmp_val[1] 

   delta=(max_dec-min_dec)/npoints
   for i in range(0,npoints+1):
    pcoord=min_dec+i*delta
    tmp_val=self.sp_to_rt(min_ra,pcoord)
    if x_min>tmp_val[0]: x_min=tmp_val[0] 
    elif x_max<tmp_val[0]: x_max=tmp_val[0] 
    if y_min>tmp_val[1]: y_min=tmp_val[1] 
    elif y_max<tmp_val[1]: y_max=tmp_val[1] 
    tmp_val=self.sp_to_rt(max_ra,pcoord)
    if x_min>tmp_val[0]: x_min=tmp_val[0] 
    elif x_max<tmp_val[0]: x_max=tmp_val[0] 
    if y_min>tmp_val[1]: y_min=tmp_val[1] 
    elif y_max<tmp_val[1]: y_max=tmp_val[1] 


   return (x_min,x_max,y_min,y_max)

  # spherical to rectangular
  # SIN projection
  def sp_to_rt(self,ra,dec):
   if self.__state==0: return (ra,dec)
   del_a=ra-self.__ra0
   L=math.cos(dec)*math.sin(del_a)
   M=math.sin(dec)*math.cos(self.__dec0)-math.cos(dec)*math.sin(self.__dec0)*math.cos(del_a)
   if self.__p==0:
     return (L,M)
   else: # we have an axis rotation 
     l=L*math.cos(self.__p)+M*math.sin(self.__p)
     m=-L*math.sin(self.__p)+M*math.cos(self.__p)
     return (l,m)

  # rectangular to spherical
  # SIN projection
  def rt_to_sp(self,l,m):
   if self.__state==0: return (l,m)
   if self.__p==0:
     L=l
     M=m
   else:
     L=l*math.cos(self.__p)-m*math.sin(self.__p)
     M=l*math.sin(self.__p)+m*math.cos(self.__p)

   try:
     dec=math.asin(M*math.cos(self.__dec0)\
        +math.sin(self.__dec0)*math.sqrt(1-L*L-M*M))

     ra=self.__ra0+math.atan(L/(math.cos(self.__dec0)\
        *math.sqrt(1-L*L-M*M)-M*math.sin(self.__dec0)))
   except ValueError:
     return(0,0)
  
   return (ra,dec)

  # turn off projection
  def Off(self):
   self.__state=0

  # turn on projection
  def On(self):
   self.__state=1

  # check if it is on
  def isOn(self):
   return (self.__state!=0)

if __name__=="__main__":
   import random
   p=Projector(random.random()*math.pi,random.random()*math.pi*0.5)
   for i in range(100):
    rr=random.random()*math.pi
    dd=random.random()*math.pi*0.5
    (l,m)=p.sp_to_rt(rr,dd)
    (ra,dec)=p.rt_to_sp(l,m)

    print "(%f,%f)-->(%f,%f)-->(%f,%f)"%(rr,dd,l,m,ra,dec)

   
