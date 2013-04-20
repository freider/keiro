#!/usr/bin/env python

from distutils.core import Extension, setup

swig_opts = ["-c++", "-outdir", "../keiro"]

#TODO: used shared libraries instead of multi-compiling same sources if possible...
vector2d_module = Extension(
    '_vector2d',
    sources=[
        'vector2d.i',
        'vector2d.cpp',
    ],
    swig_opts=swig_opts
)

particle_module = Extension(
    '_particle',
    sources=[
        'particle.i',
        'linearparticle.cpp',
        'particle.cpp',
        'geometry.cpp',
        'vector2d.cpp',
    ],
    swig_opts=swig_opts
)

geometry_module = Extension(
    '_geometry',
    sources=[
        'geometry.i',
        'geometry.cpp',
        'vector2d.cpp',
    ],
    swig_opts=swig_opts
)

astar_module = Extension(
    '_astar',
    sources=[
        'astar.i',
        'astar.cpp',
    ],
    swig_opts=swig_opts
)

setup(
    ext_modules=[
        vector2d_module,
        particle_module,
        geometry_module,
        astar_module,
    ],
)
# setup(
#     name='keiro.cpp',
#     version='0.1',
#     author="Elias Freider",
#     author_email="elias@freider.se",
#     url="https://github.com/freider/keiro",
#     description="""Fast and leightweight helper classes""",
#     ext_modules=[
#         vector2d_module,
#         particle_module,
#         geometry_module,
#         astar_module,
#     ],
#     #py_modules=["vector2d"],
# )
