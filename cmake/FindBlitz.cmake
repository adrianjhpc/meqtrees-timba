# - Find blitz
# Find the native BLITZ includes and library
#
#  BLITZ_INCLUDE_DIR - where to find blitz.h, etc.
#  BLITZ_LIBRARY_DIR - where to find blitz libraries.
#  BLITZ_LIBRARIES   - List of libraries when using blitz.
#  BLITZ_FOUND       - True if blitz found.


IF (BLITZ_INCLUDE_DIR)
    # Already in cache, be silent
    SET(BLITZ_FIND_QUIETLY TRUE)
ENDIF (BLITZ_INCLUDE_DIR)

FIND_PATH(BLITZ_INCLUDE_DIR blitz PATHS /opt/mpp/blitz/0.9/inlcude )

SET(BLITZ_NAMES blitz)
FIND_LIBRARY(BLITZ_LIBRARY NAMES ${BLITZ_NAMES} PATHS $ENV{BLITZ_LIBRARY_DIR} ${BLITZ_LIBRARY_DIR} /opt/mpp/blitz/0.9/lib )

# handle the QUIETLY and REQUIRED arguments and set BLITZ_FOUND to TRUE if.
# all listed variables are TRUE
INCLUDE(FindPackageHandleCompat)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(BLITZ DEFAULT_MSG BLITZ_LIBRARY BLITZ_INCLUDE_DIR)

IF(BLITZ_FOUND)
    SET( BLITZ_LIBRARIES ${BLITZ_LIBRARY} )
ELSE(BLITZ_FOUND)
    SET( BLITZ_LIBRARIES )
ENDIF(BLITZ_FOUND)

MARK_AS_ADVANCED( BLITZ_LIBRARY BLITZ_INCLUDE_DIR )

