#!/usr/bin/env python

"""
setup.py file for graph modules
"""

from distutils.core import setup, Extension

graphutils_module = Extension('_graphutils',
                           sources=['graphutils_wrap.cxx', 'graphutils.cpp'],
                           )
                           
setup (name = 'graphutils',
       version = '0.1',
       author      = "Elias Freider",
       description = """Graph Utilities""",
       ext_modules = [graphutils_module],
       py_modules = ["graphutils"],
       )
