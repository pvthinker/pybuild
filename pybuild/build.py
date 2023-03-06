"""
Why use Makefiles when Python does it so easily?

Compile the Fortran subroutines and generate the dynamic libraries

"""
import os
import time
import numpy as np
import subprocess
from ctypes import POINTER, c_char, c_double, c_float, c_int32, c_int8, byref, cdll, c_int, c_bool, c_wchar_p, create_string_buffer, c_char_p
#from mpi4py import MPI
#import mpi4py

def bold(string):
    return f"\033[1m{string}\033[0m"


MAP_TYPES = {
    "float64": c_double,
    "float32": c_float,
    "int8": c_int8,
    "int32": c_int32,
    "bool": c_bool
}


def localpath(pathtofile):
    return os.path.abspath(os.path.dirname(pathtofile))


def setup_fortran_func(fortranfunc, common_args):
    tags = {}
    com_args = ptr(common_args)

    def func(*args, tag=None):
        if tag not in tags:
            tags[tag] = ptr(args)
        local_args = tags[tag]
        fortranfunc(*local_args, *com_args)
    return func


def ptr(thing):
    """ return pointer(s)"""
    if isinstance(thing, tuple) or isinstance(thing, list):
        args = [ptr(t) for t in thing]
        return tuple(args)

    elif isinstance(thing, np.ndarray):
        return thing.ctypes.data_as(POINTER(MAP_TYPES[str(thing.dtype)]))

    elif isinstance(thing, int):
        return byref(c_int32(thing))

    elif isinstance(thing, np.float32):
        return byref(c_float(thing))

    elif isinstance(thing, float):
        return byref(c_double(thing))

    elif isinstance(thing, bool):
        return byref(c_bool(thing))

    elif isinstance(thing, bytes):
        return byref(c_char(thing))

    elif isinstance(thing, str):
        # return byref(c_wchar_p(thing))
        # return byref(c_char_p(bytes(thing, "utf-8")))
        return byref(create_string_buffer(bytes(thing, "utf-8")))

    else:
        raise ValueError(
            f"problem with argument {thing} of type {type(thing)}")


def isfile1newerthanfile2(file1, file2, path):
    t1 = os.path.getmtime(f"{path}/{file1}")
    if os.path.isfile(f"{path}/{file2}"):
        t2 = os.path.getmtime(f"{path}/{file2}")
        return t1 > t2
    else:
        return True


def srcs_newer_than_lib(srcs, lib, path):
    if isinstance(srcs, list):
        return any([isfile1newerthanfile2(src, lib, path) for src in srcs])
    elif isinstance(srcs, str):
        return isfile1newerthanfile2(srcs, lib, path)
    else:
        raise ValueError


def load(library):
    return cdll.LoadLibrary(library)


def import_from_library(library, function, path="."):
    lines = subprocess.check_output(
        ["nm", f"{path}/{library}"]).decode().split("\n")
    line = [l for l in lines if function in l]
    if len(line) >= 1:
        name = line[0].split()[-1]
        lib = load(f"{path}/{library}")
        return getattr(lib, name)

    elif len(line) > 1:
        msg = f"found multiple occurences of {function} in {library}"
        print(line)
    else:
        msg = f"did not found {function} in {library}"
    raise ValueError(msg)


def compile_fortran(compiler, flags, srcs, library, path):
    #currentpath = os.path.abspath(os.path.curdir)
    command = f"cd {path};{compiler} {flags} -fPIC -shared {srcs} -o {library}"
    tic = time.time()
    os.system(command)
    toc = time.time()
    elapsed = toc-tic
    #print(f"{elapsed:8.3}s : {command}")
    return elapsed, command

def get_compiler():
    nodename = os.uname().nodename
    if "irene" in nodename:
        compiler = "ifort"
        flags = "-r8 -O3 -mavx2 -axCORE-AVX512,MIC-AVX512 -cpp"

    else:
        compiler = "gfortran"
        #compiler = "mpif90.mpich"
        flags = " -cpp -freal-4-real-8 -Ofast -march=x86-64 -mtune=native -ffast-math -ffree-line-length-none"
        #flags = "-cpp  -Ofast -march=native -ffast-math  -ffree-line-length-none"

    return compiler, flags


def build(modules, path=None):
    """Build dynamic libraries from Fortran files

    Parameters
    ----------

    modules: dict

    whose keys are the library name (without lib and .so), and values
    are, either the name of the Fortran filename, or the list of
    Fortran filenames

    """
    assert isinstance(modules, dict)

    assert path is not None, "path is required when calling build"

    #    MPI = mpi4py.MPI

    #    if MPI.COMM_WORLD.Get_rank() == 0:

    compiler, flags = get_compiler()

    for library, srcs in modules.items():
        if srcs_newer_than_lib(srcs, library, path):
            elapsed, command = compile_fortran(compiler, flags, srcs, library, path)
            print(bold(f"{library:>20}: [compiled in {elapsed:4.2} s]"))
            for line in command.split(";"):
                print(" "*4, line)
        else:
            print(bold(f"{library:>20}: [ok]"))

    #MPI.COMM_WORLD.Barrier()
