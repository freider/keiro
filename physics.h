#include <vector>

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
};

class World;
class Particle{
friend class World;
public:
	Particle(float x, float y);
	~Particle();
	Vec2d position;
	Vec2d target;
	float radius;
	float speed;
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
