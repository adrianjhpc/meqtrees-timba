    // This file is generated automatically -- do not edit
    // Generated by /home/oms/LOFAR/autoconf_share/../Timba/DMI/aid/build_aid_maps.pl
    #ifndef _TypeIter_Meq_h
    #define _TypeIter_Meq_h 1



#define DoForAllOtherTypes_Meq(Do,arg,separator) \
        

#define DoForAllBinaryTypes_Meq(Do,arg,separator) \
        

#define DoForAllSpecialTypes_Meq(Do,arg,separator) \
        

#define DoForAllIntermediateTypes_Meq(Do,arg,separator) \
        

#define DoForAllDynamicTypes_Meq(Do,arg,separator) \
        Do(Meq::Domain,arg) separator \
        Do(Meq::Cells,arg) separator \
        Do(Meq::Request,arg) separator \
        Do(Meq::Vells,arg) separator \
        Do(Meq::VellSet,arg) separator \
        Do(Meq::Result,arg) separator \
        Do(Meq::Funklet,arg) separator \
        Do(Meq::Polc,arg) separator \
        Do(Meq::Node,arg) separator \
        Do(Meq::Function,arg)

#define DoForAllNumericTypes_Meq(Do,arg,separator) \
        
#endif
