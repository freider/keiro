#!/usr/bin/env python
from distutils.core import setup, Extension

vector2d_module = Extension('_vector2d',
    sources=['vector2d.i', 'vector2d.cpp'],
    swig_opts=["-c++"])

particle_module = Extension('_particle',
    sources=['particle.i', 'linearparticle.cpp', 'particle.cpp', 'geometry.cpp', 'vector2d.cpp'],
    swig_opts=["-c++"])

geometry_module = Extension('_geometry',
    sources=['geometry.i', 'geometry.cpp', 'vector2d.cpp'],
    swig_opts=["-c++"])

astar_module = Extension('_astar',
    sources=['astar.i', 'astar.cpp'],
    swig_opts=['-c++'])

setup(name='keiro.fast',
    version='0.1',
    author="Elias Freider",
    author_email="freider@kth.se",
    url="https://bitbucket.org/fishmoose/keiro",
    description="""Fast and leightweight helper classes""",
    ext_modules=[vector2d_module, particle_module, geometry_module, astar_module],
    #py_modules=["vector2d"],
    )
