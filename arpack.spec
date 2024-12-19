%global major		2

%define libname		%mklibname %{name}
%define devname		%mklibname %{name} -d
%define oldlibname	%mklibname %{name} 2

%define plibname	%mklibname p%{name}
%define pdevname	%mklibname p%{name} -d
%define oldplibname	%mklibname p%{name} 2

%bcond eigen		1
%bcond icb		1
%bcond mpich		0
%bcond openmpi		0
%bcond tests		1

# blas
%global blaslib flexiblas

%if %{?__isa_bits:%{__isa_bits}}%{!?__isa_bits:32} == 64
%global arch64 1
%else
%global arch64 0
%endif

%if 0%{?arch64}
%bcond interface64	1
%else
%bcond interface64	0
%endif

%if (%{with mpich} || %{with openmpi})
%bcond mpi	1
%else
%bcond mpi	0
%endif

Summary:	Fortran 77 subroutines for solving large scale eigenvalue problems
Name:		arpack
Version:	3.9.1
Release:	1
Group:		Sciences/Mathematics
License:	BSD
URL:		https://github.com/opencollab/arpack-ng
Source0:	https://github.com/opencollab/arpack-ng/archive/%{version}/%{name}-%{version}.tar.gz
BuildRequires:	cmake ninja
BuildRequires:	gcc-gfortran
BuildRequires:	pkgconfig(flexiblas)
BuildRequires:	cmake(eigen3)
%if %{with openmpi}
BuildRequires:	cmake(MPI)
BuildRequires:	openmpi
BuildRequires:	pkgconfig(ompi)
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
%license COPYING
%doc README.md TODO CHANGES PARPACK_CHANGES
%doc EXAMPLES DOCUMENTS

#----------------------------------------------------------------------

%package -n %{libname}
Summary:	Runtime libraries for ARPACK
Group:		Sciences/Mathematics
Provides:	%{name}-devel
Obsoletes:      %{oldlibname} < %{EVRD}

%description -n %{libname}
ARPACK is a collection of Fortran 77 subroutines designed to solve
large scale eigenvalue problems. This package contains runtime
libraries needed to run arpack based applications.

%files -n %{libname}
%license COPYING
%{_libdir}/lib%{name}.so.*
%if 0%{?arch64}
%{_libdir}/lib%{name}64.so.*
%endif

#----------------------------------------------------------------------

%package -n %{devname}
Summary:	Files needed for developing ARPACK based applications
Group:		Development/C
Requires:	%{libname} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Provides:	%{name}-ng-devel = %{version}-%{release}

%description -n %{devname}
ARPACK is a collection of Fortran 77 subroutines designed to solve
large scale eigenvalue problems. This package contains the .so
library links used for building ARPACK based applications.

%files -n %{devname}
%license COPYING

%dir %{_includedir}/%{name}

%{_includedir}/%{name}/*.h
%{_includedir}/%{name}/*.hpp
%{_libdir}/lib%{name}.so
%{_libdir}/pkgconfig/%{name}.pc
%dir %{_libdir}/cmake/%{name}ng
%{_libdir}/cmake/%{name}ng/*cmake

%if 0%{?arch64}
%dir %{_includedir}/%{name}64/
%{_includedir}/%{name}64/*.h
%{_includedir}/%{name}64/*.hpp
%{_libdir}/lib%{name}64.so
%{_libdir}/pkgconfig/%{name}64.pc
%dir %{_libdir}/cmake/%{name}ng64
%{_libdir}/cmake/%{name}ng64/*cmake
%endif

#----------------------------------------------------------------------

%if %{with mpi}
%package -n %{plibname}
Summary:	Runtime libraries for PARPACK
Group:		Sciences/Mathematics
Obsoletes:      %{oldplibname} < %{EVRD}

%description -n %{plibname}
ARPACK is a collection of Fortran 77 subroutines designed to solve
large scale eigenvalue problems. This package contains runtime
libraries needed to run arpack based applications.

PARPACK is a parallel version of ARPACK that utilizes MPI.

%files -n %{plibname}
%license COPYING
%{_libdir}/libp%{name}.so.*
%if 0%{?arch64}
%{_libdir}/libp%{name}64.so.*
%endif
%endif

#----------------------------------------------------------------------

%if %{with mpi}
%package -n %{pdevname}
Summary:	Files needed for developing ARPACK based applications
Group:		Development/C
Requires:	%{libname} = %{version}-%{release}
Provides:	p%{name}-devel = %{version}-%{release}

%description -n %{pdevname}
ARPACK is a collection of Fortran 77 subroutines designed to solve
large scale eigenvalue problems. PARPACK is a parallel version of
ARPACK that utilizes MPI. This package contains the .so library
links used for building PARPACK based applications.

%files -n %{pdevname}
%license COPYING
%if 0%{?arch64}
%{_libdir}/libp%{name}64.so
%endif
%endif

#----------------------------------------------------------------------

%prep
%autosetup -n %{name}-ng-%{version}

#FIXME: cmake fails to detect openmpi
# Whoa, a logical XOR implementation for RPM!
#%%if (%{without mpich} && %{without openmpi}) || (%{with mpich} && %{with openmpi})
#%%{error:either MPICH or OpenMPI should be chosen}
#exit 1
#%%endif

%build
export CC=gcc
export CXX=g++
export FC=gfortran

for d in build%{?arch64:{64,}}
do
	mkdir %_vpath_builddir-$d
	ln -s %_vpath_builddir-$d build

	if [[ "$d" =~ "64" ]]; then
		INTERFACE64="ON"
		ITF64SUFFIX="64"
		BLAS="%{_libdir}/lib%{blaslib}64.so"
		LAPACK="%{_libdir}/lib%{blaslib}64.so"
	else
		INTERFACE64="OFF"
		ITF64SUFFIX=
		BLAS="%{_libdir}/lib%{blaslib}.so"
		LAPACK="%{_libdir}/lib%{blaslib}.so"
	fi

	%cmake \
		-DBLAS_LIBRARIES:FILEPATH=$BLAS \
		-DEIGEN:BOOL=%{?with_eigen:ON}%{?!with_eigen:OFF} \
		-DICB:BOOL=%{?with_icb:ON}%{?!with_icb:OFF} \
		-DLAPACK_LIBRARIES:FILEPATH=$LAPACK \
		-DMPI:BOOL=%{?with_openmpi:ON}%{?!with_openmpi:OFF} \
%if %{with mpich}
		-DMPIEXEC:FILEPATH=%{_libdir}/mpich/bin/mpiexec \
%endif
%if %{with openmpi}
		-DMPIEXEC:FILEPATH=%{_libdir}/openmpi/bin/mpiexec \
		-DMPI_C_HEADER_DIR:DIRPATH=%{_libdir}/openmpi/lib/ \
		-DMPI_FORTRAN=%{_libdir}/openmpi/bin/mpifort \
%endif
		-DINTERFACE64:BOOL=$INTERFACE64 \
		-DITF64SUFFIX:STRING=$ITF64SUFFIX \
		-DTESTS:BOOL=%{?with_tests:ON}%{?!with_tests:OFF} \
		-G Ninja
	%ninja_build

	cd ..
	rm build
done

%install
for d in build%{?arch64:{,64}}
do
	ln -fs %_vpath_builddir-$d build
	%ninja_install -C build
	rm build
done

%check
%if %{with tests}
for d in build%{?arch64:{64,}}
do
	ln -fs %_vpath_builddir-$d build
	pushd build
	ctest
	popd 1>/dev/null
	rm build
done
%endif

