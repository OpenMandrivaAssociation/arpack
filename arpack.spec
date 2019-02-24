%define major		2
%define libname		%mklibname %{name} %{major}
%define develname	%mklibname %{name} -d
%define plibname	%mklibname p%{name} %{major}
%define pdevelname	%mklibname p%{name} -d

%bcond_with	interface64
%bcond_with	mpich
%bcond_without	openmpi

%if %{with mpich} || %{with openmpi}
%bcond_without	mpi
%else
%bcond_with	mpi
%endif

Name:		arpack
Version:	3.7.0
Release:	1
Group:		Sciences/Mathematics
License:	BSD
Summary:	Fortran 77 subroutines for solving large scale eigenvalue problems
URL:		https://github.com/opencollab/arpack-ng
Source0:	https://github.com/opencollab/arpack-ng/archive/%{version}/%{name}-%{version}.tar.gz
BuildRequires:	cmake
BuildRequires:	cmake(lapack)
BuildRequires:	gcc-gfortran
BuildRequires:	blas-devel
%if %{with openmpi}
BuildRequires:	cmake(MPI)
BuildRequires:	openmpi-devel
%endif
%if %{with mpich}
BuildRequires:	mpi2f77
BuildRequires:	mpich-devel
%endif

Provides:	%{name}-ng = %{version}-%{release}

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

%files
%doc README TODO CHANGES COPYING PARPACK_CHANGES EXAMPLES DOCUMENTS

#---------------------------------------------------------------------------

%package -n %{libname}
Summary:	Runtime libraries for ARPACK

Group:		Sciences/Mathematics

%description -n %{libname}
ARPACK is a collection of Fortran 77 subroutines designed to solve
large scale eigenvalue problems. This package contains runtime
libraries needed to run arpack based applications.

%files -n %{libname}
%{_libdir}/lib%{name}.so.*
%doc COPYING

#---------------------------------------------------------------------------

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

%files -n %{develname}
%{_libdir}/lib%{name}.so
%{_libdir}/pkgconfig/%{name}.pc
%doc COPYING

#---------------------------------------------------------------------------

%if %{with mpi}
%package -n %{plibname}
Summary:	Runtime libraries for PARPACK

Group:		Sciences/Mathematics

%description -n %{plibname}
ARPACK is a collection of Fortran 77 subroutines designed to solve
large scale eigenvalue problems. This package contains runtime
libraries needed to run arpack based applications.

PARPACK is a parallel version of ARPACK that utilizes MPI.

%files -n %{plibname}
%{_libdir}/libp%{name}.so.*
%doc COPYING
%endif

#---------------------------------------------------------------------------

%if %{with mpi}
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

%files -n %{pdevelname}
%{_libdir}/libp%{name}.so
%doc COPYING
%endif

#---------------------------------------------------------------------------

%prep
%setup -q -n %{name}-ng-%{version}

# Whoa, a logical XOR implementation for RPM!
%if (%{without mpich} && %{without openmpi}) || (%{with mpich} && %{with openmpi})
%{error:either MPICH or OpenMPI should be chosen}
exit 1
%endif

%build
#export CC=gcc
#export CXX=g++

%cmake \
	-DBUILD_SHARED_LIBS:BOOL=ON \
	-DEXAMPLES:BOOL=OFF \
%if %{with interface64}
	-DINTERFACE64:BOOL=ON \
%endif
%if %{without interface64}
	-DINTERFACE64:BOOL=OFF \
%endif
%if %{with mpi}
	-DMPI:BOOL=ON \
%if %{with openmpi}
	-DMPIEXEC:FILEPATH=%{_libdir}/openmpi/bin/mpiexec \
%endif
%if %{with mpich}
	-DMPIEXEC:FILEPATH=%{_libdir}/mpich/bin/mpiexec \
%endif
%endif
%if %{without mpi}
	-DMPI:BOOL=OFF \
%endif
	%{nil}
%make

%install
%makeinstall_std -C build

# pkgconfig
install -dm 0755 %{buildroot}/%{_libdir}/pkgconfig/
install -pm 0644 build/%{name}.pc %{buildroot}/%{_libdir}/pkgconfig/

