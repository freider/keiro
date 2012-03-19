vector2d.py vector2d_wrap.cxx: vector2d.cpp vector2d.hpp vector2d.i
	swig -python -c++ vector2d.i

_vector2d.so: vector2d_wrap.cxx vector2d.cpp setup_physics.py
	python setup_physics.py build_ext --inplace

particle.o: particle.cpp particle.hpp
	g++ -c particle.cpp

geometry.o: geometry.cpp geometry.hpp
	g++ -c geometry.cpp

acceleratingparticle.o: acceleratingparticle.cpp acceleratingparticle.hpp particle.o
	g++ -c acceleratingparticle.cpp

linearparticle.o: linearparticle.cpp linearparticle.hpp particle.o
	g++ -c linearparticle.cpp


all: physics.py _physics.so graphutils.py _graphutils.so

_physics.so: setup_physics.py physics_wrap.cxx physics.cpp
	python setup_physics.py build_ext --inplace  -I/opt/local/include/

_graphutils.so: setup_graphutils.py graphutils_wrap.cxx graphutils.cpp
	python setup_graphutils.py build_ext --inplace -I/opt/local/include/

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

cleancpp:
	rm -f *.o
