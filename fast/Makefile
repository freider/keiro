all: physics.py _physics.so graphutils.py _graphutils.so

_physics.so: setup_physics.py physics_wrap.cxx physics.cpp
	python setup_physics.py build_ext --inplace

_graphutils.so: setup_graphutils.py graphutils_wrap.cxx graphutils.cpp
	python setup_graphutils.py build_ext --inplace

physics.py physics_wrap.cxx: physics.i physics.h
	swig -python -c++ physics.i	

graphutils.py graphutils_wrap.cxx: graphutils.i graphutils.h
	swig -python -c++ graphutils.i	

clean:
	rm -f physics.py
	rm -f graphutils.py
	rm -f *.cxx
	rm -f *~ *.pyc *.pyo
	rm -f *.so
	rm -rf build
	

