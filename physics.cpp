#include "physics.h"
#include <vector>
#include <cmath>
#include <cstdio>

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
bool Vec2d::operator==(const Vec2d &v) const{
	return x==v.x && y==v.y;
}
float Vec2d::distance_to(const Vec2d &v) const{
	return sqrt(distance_to2(v));
}
float Vec2d::distance_to2(const Vec2d &v) const{
	return (x-v.x)*(x-v.x)+(y-v.y)*(y-v.y);
}
float Vec2d::dot(const Vec2d &v) const{
	return x*v.x + y*v.y;
}
float Vec2d::angle(const Vec2d &v) const{
	return acos(this->norm().dot(v.norm()));
}

/************
**Particle**
************/
Particle::Particle(float x, float y, float dir)
	:radius(0),
	speed(0),
	world(NULL)
{
	position = Vec2d(x, y);
	target = position; //not moving
}
Particle::~Particle(){
	if(world != NULL)
		world->unbind(this);
}
void Particle::update(float dt){
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
World::~World(){
	for(size_t i = 0; i<particles.size(); ++i){
		particles[i]->world = NULL;
	}
}
void World::unbind(Particle *p){
	for(size_t i = 0; i<particles.size(); ++i){
		if(particles[i] == p){
			particles.erase(particles.begin() + i);
			--i;
		}
	}
	p->world = NULL;
}

void World::bind(Particle *p){
	particles.push_back(p);
	p->world = this;
}

void World::update(float dt){
	for(size_t i = 0, sz = particles.size(); i<sz; ++i){
		particles[i]->update(dt);
	}
	//collision detection
	for(size_t i = 0, sz = particles.size(); i<sz; ++i){
		for(size_t j = i+1; j<sz; ++j){
			float dist2 = particles[i]->position.distance_to2(particles[j]->position);
			float safe_dist = particles[i]->radius + particles[j]->radius;
			float safe_dist2 = safe_dist*safe_dist;
			if(dist2 < safe_dist2){
				//collision
				float diff = sqrt(dist2) - sqrt(safe_dist2);
				Vec2d dirv(1,0);
				if(dist2 != 0)
				 	dirv = (particles[i]->position - particles[j]->position).norm();
				particles[j]->position = particles[j]->position + dirv*diff;
				particles[i]->position = particles[i]->position - dirv*diff;
			}
		}
	}
}
int World::num_particles(){
	return particles.size();
}
std::vector<Particle*> World::particles_in_range(const Particle *from, float range) const{
	float range2 = range*range;
	std::vector<Particle*> res;
	for(size_t i = 0, sz = particles.size(); i<sz; ++i){
		if(particles[i] != from && particles[i]->position.distance_to2(from->position) <= range2)
			res.push_back(particles[i]);
	}
	return res;
}

int main(void){
	Particle *p = new Particle(0,0);
	World w;
	w.bind(p);
	printf("%f %f\n", p->position.x, p->position.y);
	delete p;
}
