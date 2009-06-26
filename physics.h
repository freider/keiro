#include <vector>

struct Vec2d{
	float x, y;
	Vec2d();
	Vec2d(float _x, float _y);
	Vec2d operator/(float f) const;
	Vec2d operator*(float f) const;
	Vec2d operator-(const Vec2d &v) const;
	Vec2d operator+(const Vec2d &v) const;
	bool operator==(const Vec2d &v) const;
	float length() const;
	Vec2d norm() const;
};

class Particle{
friend class World;
public:
	Vec2d position;
	Vec2d target;
	float radius;
	float speed;
private:
	Particle(float x, float y, float _speed, float _radius);
	void update(float dt);
};

class World{
	std::vector<Particle*> particles;
public:
	~World();
	void clear();
	Particle* create_particle(float x, float y, float speed = 0, float radius = 0);
	void update(float dt);
};
