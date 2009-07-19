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

struct State{
	Vec2d position;
	float angle;
};

class Path{
private:
	std::deque<State> path;
public:
	Path(const Vec2d &v, float angle);
	void target_clear();
	void progress(float distance);
	void target_push(const Vec2d &v);
	void target_push(const Vec2d &v, float angle);
	void target_pop();
	Vec2d position() const{
		return path.front().position;
	}
	float angle() const{
		return path.front().angle;
	}
};

class World;
class Particle{
friend class World;
public:
	Particle(float x = 0, float y = 0, float dir = 1);
	~Particle();
	Vec2d position;
	Vec2d target;
	float radius;
	float speed;
	float direction;
	float turningspeed;
private:
	World *world;
	void update(float dt);
};

class World{
public:
	~World();
	void bind(Particle *p);
	void unbind(Particle *p);
	void update(float dt);
	int num_particles();
	std::vector<Particle*> particles_in_range(const Particle *from, float range) const;
private:
	std::vector<Particle*> particles;
};
