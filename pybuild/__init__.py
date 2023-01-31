"""
pybuild

A module to bind Fortran with Python
"""

__version__ = "0.1.0"
__author__ = 'Guillaume Roullet'
__credits__ = 'University of Brest'

from .build import ptr, import_from_library, build, localpath
from .build import c_char, c_double, c_float, c_int32, c_int8, c_int, c_bool
