#!/usr/bin/env python

from distutils.core import setup, Extension

vector2d_module = Extension('_vector2d',
    sources=['vector2d.i', 'vector2d.cpp'],
    swig_opts=["-c++"])

particle_module = Extension('_particle',
    sources=['particle.i', 'particle.cpp'],
    swig_opts=["-c++"])

setup(name='keiro.fast',
       version='0.1',
       author="Elias Freider",
       description="""Fast and leightweight helper classes""",
       ext_modules=[vector2d_module, particle_module],
       #py_modules=["vector2d"],
       )
