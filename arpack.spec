%define build_parpack 0
%define _disable_rebuild_configure 1
%define _disable_lto 2

# To build PARPACK, we'll need a FORTRAN 77 MPI implementation.

%define build_mpich 0
%define build_openmpi 1

%{?_with_parpack: %{expand: %%global build_parpack 1}}
%{?_without_parpack: %{expand: %%global build_parpack 0}}

%{?_with_mpich: %{expand: %%global build_mpich 1}}
%{?_with_openmpi: %{expand: %%global build_openmpi 1}}
%{?_without_mpich: %{expand: %%global build_mpich 0}}
%{?_without_openmpi: %{expand: %%global build_openmpi 0}}

Name:		arpack
Version:	3.1.5
Release:	1
Group:		Sciences/Mathematics
License:	BSD
Summary:	Fortran 77 subroutines for solving large scale eigenvalue problems

URL:		http://forge.scilab.org/index.php/p/arpack-ng/
Source0:	http://forge.scilab.org/index.php/p/arpack-ng/downloads/get/arpack-ng-%{version}.tar.gz
Provides:	%{name}-ng = %{version}-%{release}
BuildRequires:	autoconf
BuildRequires:	gcc-gfortran
BuildRequires:	blas-devel
BuildRequires:	lapack-devel
BuildRequires:	openmpi

%if %{build_parpack}
%if %{build_mpich}
BuildRequires:	mpi2f77
%endif
%if %{build_openmpi}
BuildRequires:	libopenmpi-devel
%endif
%endif

%define major		2
%define libname		%mklibname %{name} %{major}
%define develname	%mklibname %{name} -d
%if %{build_parpack}
%define plibname	%mklibname p%{name} %{major}
%define pdevelname	%mklibname p%{name} -d
%endif

%description
ARPACK is a collection of Fortran 77 subroutines designed to solve large
scale eigenvalue problems.

The package is designed to compute a few eigenvalues and corresponding
eigenvectors of a general n by n matrix A. It is most appropriate for
large sparse or structured matrices A where structured means that a
matrix-vector product w <- Av requires order n rather than the usual
order n**2 floating point operations. This software is based upon an
algorithmic variant of the Arnoldi process called the Implicitly
Restarted Arnoldi Method (IRAM).

%package -n %{libname}
Summary:	Runtime libraries for ARPACK

Group:		Sciences/Mathematics

%description -n %{libname}
ARPACK is a collection of Fortran 77 subroutines designed to solve
large scale eigenvalue problems. This package contains runtime
libraries needed to run arpack based applications.

%package -n %{develname}
Summary:	Files needed for developing ARPACK based applications

Group:		Sciences/Mathematics
Requires:	%{libname} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Provides:	%{name}-ng-devel = %{version}-%{release}

%description -n %{develname}
ARPACK is a collection of Fortran 77 subroutines designed to solve
large scale eigenvalue problems. This package contains the .so
library links used for building ARPACK based applications.

%if %{build_parpack}

%package -n %{plibname}
Summary:	Runtime libraries for PARPACK

Group:		Sciences/Mathematics

%description -n %{plibname}
ARPACK is a collection of Fortran 77 subroutines designed to solve
large scale eigenvalue problems. This package contains runtime
libraries needed to run arpack based applications.

PARPACK is a parallel version of ARPACK that utilizes MPI.

%package -n %{pdevelname}
Summary:	Files needed for developing ARPACK based applications

Group:		Sciences/Mathematics
Requires:	%{libname} = %{version}-%{release}
Provides:	p%{name}-devel = %{version}-%{release}

%description -n %{pdevelname}
ARPACK is a collection of Fortran 77 subroutines designed to solve
large scale eigenvalue problems. PARPACK is a parallel version of
ARPACK that utilizes MPI. This package contains the .so library 
links used for building PARPACK based applications.

%endif

%prep

# Whoa, a logical XOR implementation for RPM!
%if !(%{build_mpich} || %{build_openmpi}) || (%{build_mpich} && %{build_openmpi})
%{error:either MPICH or OpenMPI should be chosen}
exit 1
%endif

%setup -q -n %{name}-ng-%{version}

# The Autoconf ax_mpi.m4 file doesn't detect correct library sets.
%if %{build_mpich}
export MPILIBS="-lfmpich -lpmpich -lmpich"
%endif
%if %{build_openmpi}
export MPILIBS="-lmpi_mpifh"
%endif

# Fix undefined __stack_chk_fail
sed -i Makefile.am -e "s/\$(LAPACK_LIBS)/\$(LAPACK_LIBS) -lc/"

# libtool forgets about MPI libs when linking PARPACK, fix it
# (and __stack_chk_fail too)
sed -i PARPACK/Makefile.am -e "s/\$(LAPACK_LIBS)/\$(LAPACK_LIBS) $MPILIBS -lc/"

autoreconf -iv

%configure2_5x \
%if %{build_parpack}
--enable-mpi \
%endif
--disable-static

%build
%make

%install
%makeinstall_std

%__rm -f %{buildroot}/%{_libdir}/*.la
%__rm -f %{buildroot}/%{_bindir}/p??drv?

%files
%doc README TODO CHANGES COPYING PARPACK_CHANGES EXAMPLES DOCUMENTS
#{_bindir}/dnsimp

%files -n %{libname}
%{_libdir}/lib%{name}.so.*

%files -n %{develname}
%{_libdir}/lib%{name}.so
%{_libdir}/pkgconfig/%{name}.pc

%if %{build_parpack}
%files -n %{plibname}
%{_libdir}/libp%{name}.so.*

%files -n %{pdevelname}
%{_libdir}/libp%{name}.so
%endif


