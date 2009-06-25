struct Vec2d{
	double x, y;
};

class Particle{
public:
	Vec2d position;
	Vec2d target;
	double radius;
	double maxspeed;
};
