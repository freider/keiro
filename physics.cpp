#include "physics.h"
#include <vector>
#include <cmath>

Vec2d::Vec2d():x(0),y(0){
}
Vec2d::Vec2d(float _x, float _y):x(_x),y(_y){
}
float Vec2d::length() const{
	return sqrt(x*x + y*y);
}
Vec2d Vec2d::norm() const{
	return operator/(length());
}
Vec2d Vec2d::operator/(float f) const{
	return Vec2d(x/f, y/f);
}
Vec2d Vec2d::operator*(float f) const{
	return Vec2d(x*f, y*f);
}
Vec2d Vec2d::operator+(const Vec2d &v) const{
	return Vec2d(x+v.x, y+v.y);
}
Vec2d Vec2d::operator-(const Vec2d &v) const{
	return Vec2d(x-v.x, y-v.y);
}
/************
**_particle**
************/
_particle::_particle(float x, float y, float _speed, float _radius):radius(_radius),speed(_speed){
	position.x = x;
	position.y = y;
	target = position;
}

void _particle::update(float dt){
	Vec2d diff = target - position;
	float dist = diff.length();
	float maxstep = dt*speed;
	if(dist <= maxstep)
		position = target;
	else
		position = position + diff.norm()*maxstep;
}


/********
**WORLD**
********/
void World::clear(){
	for(size_t i = 0, sz = particles.size(); i<sz; ++i){
		delete particles[i];
	}
	particles.clear();
}

World::~World(){
	clear();
}

_particle* World::Particle(float x, float y, float speed, float radius){
	_particle *p = new _particle(x,y,speed,radius);
	particles.push_back(p);
	return p;
}
void World::update(float dt){
	for(size_t i = 0, sz = particles.size(); i<sz; ++i){
		particles[i]->update(dt);
	}
}

