/* physics.i */
%module physics
%{
#include "physics.h"
%}

%immutable Vec2d::x;
%immutable Vec2d::y;
%immutable Particle::position;

%include "physics.h"
%extend Vec2d {
	char* __str__() {
		static char tmp[1024];
		sprintf(tmp,"Vec2d(%f,%f)", $self->x,$self->y);
		return tmp;
	}
%pythoncode%{
	def __len__(self):
		return 2

	def __getitem__(self, key):
		if key == 0:
			return self.x
		elif key == 1:
			return self.y
		else:
			raise IndexError("Invalid subscript "+str(key)+" to Vec2d")

	def __setitem__(self, key, value):
		if key == 0:
			self.x = value
		elif key == 1:
			self.y = value
		else:
			raise IndexError("Invalid subscript "+str(key)+" to Vec2d")
			
	
%}
};

