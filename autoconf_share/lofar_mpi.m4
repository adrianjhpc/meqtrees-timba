#
# lofar_mpi.m4
#
dnl
#
# lofar_MPI
#
# Macro to check for MPICH or ScaMPI mpi.h header file
#
AC_DEFUN(lofar_MPI,dnl
[AC_ARG_ENABLE(mpi,
	[  --enable-mpi            find an MPI implementation (MPICH or ScaMPI) and enable it],
	[with_mpi="yes"], [with_mpi="no"])
AC_ARG_ENABLE(mpi-profiler,
	[  --enable-mpi-profiler   enable MPI profiler [default=no]],
	[mpi_profiler=yes], [mpi_profiler=no])
if test "$with_mpi" = "yes"; then]
lofar_HEADER_MPICH([])dnl
lofar_HEADER_SCAMPI()dnl
[
enable_mpi=0
if test "$enable_mpich" = "yes"; then
  enable_mpi=1
  if test "$enable_scampi" = "yes"; then
]
    AC_MSG_ERROR([Cannot use both MPICH and ScaMPI. Reconfigure with --without-mpich or --without-scampi])
[ fi
else
  if test "$enable_scampi" = "yes"; then
    enable_mpi=1
  fi
fi
if test $enable_mpi = 1; then]
AC_DEFINE(HAVE_MPI,dnl
	1, [Define if we have an MPI implementation installed])dnl
[fi]
[if test "$mpi_profiler" = "yes"; then]
[if test $enable_mpi = 0; then]
AC_MSG_ERROR([Can not enable MPI profiler without enabling MPI])
[else]
AC_DEFINE(HAVE_MPI_PROFILER,dnl
	1, [Define if MPI profiler should be enabled])dnl
[fi]
[fi]
[fi]
)dnl
#
#
# lofar_HEADER_MPICH([VERSION])
#
# Macro to check for MPICH mpi.h header
# -------------------------------------------------
#
AC_DEFUN(lofar_HEADER_MPICH,
[dnl
AC_PREREQ(2.13)dnl
ifelse($1, [], define(MPICH_VERSION,[1.2.1]), define(MPICH_VERSION,$1))
AC_ARG_WITH(mpich,
	[  --with-mpich[=PFX]      prefix where MPICH is installed (default=/usr/local/mpich-]MPICH_VERSION[)],
	[force_mpich=yes; mpich_prefix="$withval"],
	[force_mpich=no;  mpich_prefix=/usr/local/mpich-]MPICH_VERSION)dnl
[
if test "$mpich_prefix" = "no" ; then
  enable_mpich=no
else
  if test "$mpich_prefix" = "yes"; then
    mpich_prefix=/usr/local/mpich-]MPICH_VERSION
[
  fi
  enable_mpich=yes
]
dnl
AC_CHECK_FILE([$mpich_prefix/include/mpi.h],
	[lofar_cv_header_mpich=yes],
	[lofar_cv_header_mpich=no])
[
	if test $lofar_cv_header_mpich = yes ; then

		MPICH_CC="$mpich_prefix/bin/mpicc"
		MPICH_CXX="$mpich_prefix/bin/mpiCC"

		CC="$MPICH_CC"
		CXX="$MPICH_CXX"
]
AC_SUBST(CC)dnl
AC_SUBST(CXX)dnl
AC_DEFINE(HAVE_MPICH,dnl
	1, [Define if MPICH is installed])dnl
[
	else
		if test "$force_mpich" = "yes"; then]
AC_MSG_ERROR([Could not find MPICH in $mpich_prefix])
[		fi
		enable_mpich=no
	fi
fi]
])
#
#
# lofar_HEADER_SCAMPI([DEFAULT_PREFIX])
#
# Macro to check for ScaMPI mpi.h header
# -------------------------------------------------
#
AC_DEFUN(lofar_HEADER_SCAMPI,
[dnl
AC_PREREQ(2.13)dnl
ifelse($1, [], define(SCAMPI_DEFAULT_PREFIX,[/opt/scali]), define(SCAMPI_DEFAULT_PREFIX,$1))
AC_ARG_WITH(scampi,
	[  --with-scampi[=PFX]     prefix where ScaMPI is installed (default=]SCAMPI_DEFAULT_PREFIX[)],
	[force_scampi="yes"; scampi_prefix="$withval"],
	[force_scampi="no";  scampi_prefix=]SCAMPI_DEFAULT_PREFIX)
[
if test "$scampi_prefix" = "no"; then
  enable_scampi=no
else
  if test "$scampi_prefix" = "yes"; then
    scampi_prefix=]SCAMPI_DEFAULT_PREFIX
[
  fi
  enable_scampi=yes
]
dnl
AC_CHECK_FILE([$scampi_prefix/include/mpi.h],
	[lofar_cv_header_scampi=yes],
	[lofar_cv_header_scampi=no])
[
	if test $lofar_cv_header_scampi = yes ; then

		SCAMPI_CFLAGS="-I$scampi_prefix/include"
		SCAMPI_LDFLAGS="-L$scampi_prefix/lib"
		SCAMPI_LIBS="-lmpi"

		CFLAGS="$CFLAGS $SCAMPI_CFLAGS"
		CXXFLAGS="$CXXFLAGS $SCAMPI_CFLAGS"
		LDFLAGS="$LDFLAGS $SCAMPI_LDFLAGS"
		LIBS="$LIBS $SCAMPI_LIBS"
]
AC_SUBST(CFLAGS)
AC_SUBST(CXXFLAGS)
AC_SUBST(LDFLAGS)
AC_SUBST(LIBS)
AC_DEFINE(HAVE_SCAMPI,dnl
	1, [Define if ScaMPI is installed])dnl
[
	else
		if test "$force_scampi" = "yes"; then]
AC_MSG_ERROR([Could not find ScaMPI in $scampi_prefix])
[		fi
		enable_scampi=no
	fi
fi]
])
