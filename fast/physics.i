/* physics.i */
%module physics
%include "std_vector.i"
%{
#include "physics.h"
%}
%template(pvector) std::vector<Particle*>; 
%template(ovector) std::vector<Obstacle*>; 

class Vec2d{
public:
	%immutable;
	float x, y;
	%mutable;
	Vec2d();
	Vec2d(float _x, float _y);
	Vec2d operator/(float f) const;
	Vec2d operator*(float f) const;
	Vec2d operator-(const Vec2d &v) const;
	Vec2d operator+(const Vec2d &v) const;
	bool operator==(const Vec2d &v) const;
	float distance_to(const Vec2d &v) const;
	float distance_to2(const Vec2d &v) const;
	float length() const;
	Vec2d norm() const;
	float dot(const Vec2d &v) const;
	float cross(const Vec2d &v) const;
	float angle(const Vec2d &v) const;
	float angle() const;
};

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

float linesegdist2(Vec2d l1, Vec2d l2, Vec2d p);
float line_distance2(Vec2d l11, Vec2d l12, Vec2d l21, Vec2d l22);
float angle_diff(float a1, float a2);

struct ParticleState{
%immutable;
	Vec2d position;
	float angle;
%mutable;
};

class Particle{
	friend class World;
public:
	Particle(float x = 0, float y = 0, float dir = 1);
	~Particle();
	float radius;
	float speed;
	float turningspeed;
	int collisions;
	Vec2d position;
	Vec2d velocity;
	float angle;
	
	void update(float dt);
	void waypoint_clear();
	void waypoint_push(const Vec2d &v);
	void waypoint_push(const Vec2d &v, float angle);
	void waypoint_pop();
	int waypoint_len() const;
	const ParticleState &waypoint(int i = 0) const;
};

class Obstacle {
	friend class World;
public:
	Obstacle(const Vec2d &p1, const Vec2d &p2);
	~Obstacle();
	Vec2d p1, p2;
	
private:
	World *world;
};

class World{
public:
	World();
	~World();
	void bind(Particle *p);
	void unbind(Particle *p);
	void bind(Obstacle *l);
	void unbind(Obstacle *l);
	void update(float dt);
	int num_particles();
	std::vector<Particle*> particles_in_range(const Particle *from, float range) const;
	std::vector<Obstacle*> get_obstacles() const;
};
