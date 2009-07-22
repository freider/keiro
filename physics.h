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
	Vec2d norm() const;
	float dot(const Vec2d &v) const;
	float angle(const Vec2d &v) const;
	float angle() const;
};

float linesegdist2(Vec2d l1, Vec2d l2, Vec2d p) {
	Vec2d diff = l2-l1;
	Vec2d unit = diff.norm();
	float seglen = diff.length();
	if(abs((p-l1).dot(unit)) >= seglen or abs((p-l2).dot(unit)) >= seglen)
		return std::min(l1.distance_to2(p), l2.distance_to2(p));
	else{
		float dist = Vec2d(-unit.y, unit.x).dot(p-l1);
		return dist*dist;
	}
}

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
	Vec2d position() const{
		return path.front().position;
	}
	float angle() const{
		return path.front().angle;
	}
	void target_clear();
	void target_push(const Vec2d &v);
	void target_push(const Vec2d &v, float angle);
	void target_pop();
	int target_len() const;
	const ParticleState &target(int i) const;
	void update(float dt);
	void set_state(const Vec2d &v, float angle);
private:
	World *world;
	std::deque<ParticleState> path;
};

class World{
public:
	World(){}
	~World();
	void bind(Particle *p);
	void unbind(Particle *p);
	void update(float dt);
	int num_particles();
	std::vector<Particle*> particles_in_range(const Particle *from, float range) const;
private:
	std::vector<Particle*> particles;
};
