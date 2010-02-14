#include <vector>
#include <deque>
#include <cstdio>

class Vec2d{
public:
	float x, y;
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
	float length2() const;
	Vec2d norm() const;
	float dot(const Vec2d &v) const;
	float cross(const Vec2d &v) const;
	float angle(const Vec2d &v) const;
	float angle() const;
};

float linesegdist2(Vec2d l1, Vec2d l2, Vec2d p);
float angle_diff(float a1, float a2);

struct ParticleState{
	Vec2d position;
	float angle;
};

class World;
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
	Vec2d previous_position;
	Vec2d velocity;
	float angle;

	void waypoint_clear();
	void waypoint_push(const Vec2d &v);
	void waypoint_push(const Vec2d &v, float angle);
	void waypoint_pop();
	void waypoint_pop_first();
	int waypoint_len() const;
	const ParticleState &waypoint(int i = 0) const;
	void update(float dt);
	void set_state(const Vec2d &v, float angle);
private:
	World *world;
	std::deque<ParticleState> path;
};

class LineSegment {
	friend class World;
public:
	LineSegment(const Vec2d &p1, const Vec2d &p2);
	Vec2d p1, p2;
	
private:
	World *world;
};

class World{
public:
	World(){}
	~World();
	void bind(Particle *p);
	void unbind(Particle *p);
	void bind(LineSegment *l);
	void unbind(LineSegment *l);
	void update(float dt);
	int num_particles();
	std::vector<Particle*> particles_in_range(const Particle *from, float range) const;
private:
	std::vector<Particle*> particles;
	std::vector<LineSegment*> obstacles;
};
