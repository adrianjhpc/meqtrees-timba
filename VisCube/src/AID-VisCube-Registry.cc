    // This file is generated automatically -- do not edit
    // Generated by /home/oms/LOFAR/autoconf_share/../DMI/aid/build_aid_maps.pl
    #include <DMI/AtomicID.h>
    #include <DMI/TypeInfo.h>
    #include <DMI/DynamicTypeManager.h>
    #include <DMI/Packer.h>
    
#include "TableFormat.h"
BlockableObject * __construct_TableFormat (int n) { return n>0 ? new TableFormat [n] : new TableFormat; }
#include "ColumnarTableTile.h"
BlockableObject * __construct_ColumnarTableTile (int n) { return n>0 ? new ColumnarTableTile [n] : new ColumnarTableTile; }
#include "VisTile.h"
BlockableObject * __construct_VisTile (int n) { return n>0 ? new VisTile [n] : new VisTile; }
#include "VisCube.h"
BlockableObject * __construct_VisCube (int n) { return n>0 ? new VisCube [n] : new VisCube; }
#include "VisCubeSet.h"
BlockableObject * __construct_VisCubeSet (int n) { return n>0 ? new VisCubeSet [n] : new VisCubeSet; }
  
    int aidRegistry_VisCube ()
    {
      static int res = 

        AtomicID::registerId(-1213,"UVData")+
        AtomicID::registerId(-1199,"UVSet")+
        AtomicID::registerId(-1211,"Row")+
        AtomicID::registerId(-1141,"Raw")+
        AtomicID::registerId(-1183,"Sorted")+
        AtomicID::registerId(-1153,"Unsorted")+
        AtomicID::registerId(-1205,"Time")+
        AtomicID::registerId(-1170,"Timeslot")+
        AtomicID::registerId(-1212,"Channel")+
        AtomicID::registerId(-1147,"Num")+
        AtomicID::registerId(-1155,"Control")+
        AtomicID::registerId(-1187,"MS")+
        AtomicID::registerId(-1172,"Integrate")+
        AtomicID::registerId(-1193,"Flag")+
        AtomicID::registerId(-1175,"Exposure")+
        AtomicID::registerId(-1185,"Receptor")+
        AtomicID::registerId(-1179,"Antenna")+
        AtomicID::registerId(-1207,"IFR")+
        AtomicID::registerId(-1140,"SPW")+
        AtomicID::registerId(-1144,"Field")+
        AtomicID::registerId(-1190,"UVW")+
        AtomicID::registerId(-1118,"Data")+
        AtomicID::registerId(-1148,"Integrated")+
        AtomicID::registerId(-1157,"Point")+
        AtomicID::registerId(-1198,"Source")+
        AtomicID::registerId(-1163,"Segment")+
        AtomicID::registerId(-1132,"Corr")+
        AtomicID::registerId(-1145,"Name")+
        AtomicID::registerId(-1200,"Header")+
        AtomicID::registerId(-1188,"Footer")+
        AtomicID::registerId(-1162,"Patch")+
        AtomicID::registerId(-1137,"XX")+
        AtomicID::registerId(-1151,"YY")+
        AtomicID::registerId(-1138,"XY")+
        AtomicID::registerId(-1149,"YX")+
        AtomicID::registerId(-1134,"Chunk")+
        AtomicID::registerId(-1152,"Indexing")+
        AtomicID::registerId(-1035,"Index")+
        AtomicID::registerId(-1196,"Subtable")+
        AtomicID::registerId(-1102,"Type")+
        AtomicID::registerId(-1150,"Station")+
        AtomicID::registerId(-1143,"Mount")+
        AtomicID::registerId(-1146,"Pos")+
        AtomicID::registerId(-1214,"Offset")+
        AtomicID::registerId(-1174,"Dish")+
        AtomicID::registerId(-1160,"Diameter")+
        AtomicID::registerId(-1181,"Feed")+
        AtomicID::registerId(-1161,"Interval")+
        AtomicID::registerId(-1202,"Polarization")+
        AtomicID::registerId(-1156,"Response")+
        AtomicID::registerId(-1167,"Angle")+
        AtomicID::registerId(-1186,"Ref")+
        AtomicID::registerId(-1130,"Freq")+
        AtomicID::registerId(-1171,"Width")+
        AtomicID::registerId(-1184,"Bandwidth")+
        AtomicID::registerId(-1192,"Effective")+
        AtomicID::registerId(-1159,"Resolution")+
        AtomicID::registerId(-1206,"Total")+
        AtomicID::registerId(-1139,"Net")+
        AtomicID::registerId(-1158,"Sideband")+
        AtomicID::registerId(-1215,"IF")+
        AtomicID::registerId(-1165,"Conv")+
        AtomicID::registerId(-1189,"Chain")+
        AtomicID::registerId(-1169,"Group")+
        AtomicID::registerId(-1201,"Desc")+
        AtomicID::registerId(-1209,"Code")+
        AtomicID::registerId(-1136,"Poly")+
        AtomicID::registerId(-1204,"Delay")+
        AtomicID::registerId(-1195,"Dir")+
        AtomicID::registerId(-1178,"Phase")+
        AtomicID::registerId(-1177,"Pointing")+
        AtomicID::registerId(-1164,"Lines")+
        AtomicID::registerId(-1194,"Calibration")+
        AtomicID::registerId(-1203,"Proper")+
        AtomicID::registerId(-1197,"Motion")+
        AtomicID::registerId(-1182,"Sigma")+
        AtomicID::registerId(-1210,"Weight")+
        AtomicID::registerId(-1168,"Origin")+
        AtomicID::registerId(-1191,"Target")+
        AtomicID::registerId(-1180,"Tracking")+
        AtomicID::registerId(-1208,"Beam")+
        AtomicID::registerId(-1135,"Product")+
        AtomicID::registerId(-1173,"Meas")+
        AtomicID::registerId(-1154,"Centroid")+
        AtomicID::registerId(-1176,"AIPSPP")+
        AtomicID::registerId(-1142,"Ignore")+
        AtomicID::registerId(-1166,"VDSID")+
        AtomicID::registerId(-1133,"TableFormat")+
        TypeInfoReg::addToRegistry(-1133,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1133,__construct_TableFormat)+
        AtomicID::registerId(-1131,"ColumnarTableTile")+
        TypeInfoReg::addToRegistry(-1131,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1131,__construct_ColumnarTableTile)+
        AtomicID::registerId(-1128,"VisTile")+
        TypeInfoReg::addToRegistry(-1128,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1128,__construct_VisTile)+
        AtomicID::registerId(-1129,"VisCube")+
        TypeInfoReg::addToRegistry(-1129,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1129,__construct_VisCube)+
        AtomicID::registerId(-1127,"VisCubeSet")+
        TypeInfoReg::addToRegistry(-1127,TypeInfo(TypeInfo::DYNAMIC,0))+
        DynamicTypeManager::addToRegistry(-1127,__construct_VisCubeSet)+
    0;
    return res;
  }
  
  int __dum_call_registries_for_VisCube = aidRegistry_VisCube();

