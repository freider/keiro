#!/usr/bin/env python

"""
setup.py file for physics module
"""

from distutils.core import setup, Extension


physics_module = Extension('_physics',
                           sources=['physics_wrap.cxx', 'physics.cpp'],
                           )

setup (name = 'physics',
       version = '0.1',
       author      = "Elias Freider",
       description = """Particle engine.
       Each Particle """,
       ext_modules = [physics_module],
       py_modules = ["physics"],
       )

