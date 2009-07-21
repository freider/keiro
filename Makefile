all: physics.py _physics.so

_physics.so: setup.py physics_wrap.cxx physics.cpp
	python setup.py build_ext --inplace
	#g++ -shared physics.o physics_wrap.o -o _physics.so

physics.py physics_wrap.cxx: physics.i physics.h
	swig -python -c++ physics.i	

graphs: graphs.cpp graphs.h
	g++ -o graphs graphs.cpp
	
clean: 
	rm -f *.cxx
	rm -f *~ *.pyc *.pyo
	rm -rf build


