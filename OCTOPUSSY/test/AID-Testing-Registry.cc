    // This file is generated automatically -- do not edit
    // Generated by /home/oms/LOFAR/autoconf_share/../DMI/aid/build_aid_maps.pl
    #include <DMI/AtomicID.h>
    #include <DMI/TypeInfo.h>
    #include <DMI/DynamicTypeManager.h>
    #include <DMI/Packer.h>
    
  
    int aidRegistry_Testing ()
    {
      static int res = 

        AtomicID::registerId(-1114,"EchoWP")+
        AtomicID::registerId(-1121,"Ping")+
        AtomicID::registerId(-1116,"Pong")+
        AtomicID::registerId(-1120,"Reply")+
        AtomicID::registerId(-1032,"Timestamp")+
        AtomicID::registerId(-1117,"Invert")+
        AtomicID::registerId(-1118,"Data")+
        AtomicID::registerId(-1119,"Count")+
        AtomicID::registerId(-1115,"Process")+
    0;
    return res;
  }
  
  int __dum_call_registries_for_Testing = aidRegistry_Testing();

