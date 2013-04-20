modules = vector2d particle geometry

all:
	python setup.py build_ext -b ../keiro

clean:
	python setup.py clean

clean_all: clean
	echo "WARNING: clean all not cleaning files in keiro catalog"
	for mod in $(modules); do \
		rm -f $${mod}.py $${mod}_wrap.cpp; \
	done
	rm -f *~ *.pyc *.pyo
	rm -f *.so
	rm -f *.o

test:
