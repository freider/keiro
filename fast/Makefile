modules = vector2d particle geometry

all:
	python setup.py build_ext -i

clean:
	python setup.py clean

clean_all: clean
	for mod in $(modules); do \
		rm -f $${mod}.py $${mod}_wrap.cpp; \
	done
	rm -f *~ *.pyc *.pyo
	rm -f *.so
	rm -f *.o

test:
