#include "physics.h"
#include <vector>
#include <cmath>
#include <cstdio>
#include <cassert>

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
float Vec2d::angle() const{
	return atan2(y,x);
}

float linesegdist2(Vec2d l1, Vec2d l2, Vec2d p){
	Vec2d diff = l2-l1;
	Vec2d unit = diff.norm();
	float seglen = diff.length();
	if(std::abs((p-l1).dot(unit)) >= seglen or std::abs((p-l2).dot(unit)) >= seglen)
		return std::min(l1.distance_to2(p), l2.distance_to2(p));
	else{
		float dist = Vec2d(-unit.y, unit.x).dot(p-l1);
		return dist*dist;
	}
}

float angle_diff(float a1, float a2){
	float anglediff = fmod(a1 - a2, 2*M_PI);
	if(anglediff > M_PI)
		anglediff -= 2*M_PI;
	else if (anglediff < -M_PI)
		anglediff += 2*M_PI;
	return anglediff;
}
/************
**Particle**
************/
Particle::Particle(float x, float y, float dir)
	:radius(0),
	speed(0),
	collisions(0),
	world(NULL)
{
	Vec2d vec(x, y);
	ParticleState st;
	st.position = vec;
	st.angle = dir;
	path.push_back(st);
}

Particle::~Particle(){
	if(world != NULL)
		world->unbind(this);
}
void Particle::target_clear(){
	if(path.size() > 1)
		path.erase(path.begin()+1, path.end());
}

void Particle::target_push(const Vec2d &v){
	//default angle = angle from last target to this target
	if( !(v == path.back().position) )
		target_push(v, (v-path.back().position).angle());
}

void Particle::target_push(const Vec2d &v, float angle){
	ParticleState st = {v, angle};
	path.push_back(st);
}

void Particle::target_pop(){
	if(path.size() > 1)
		path.pop_back();
}

void Particle::update(float dt){
	while(dt>0 && path.size() > 1){
		if(path[0].position == path[1].position){
			float target_direction = path[1].angle;
			float anglediff = angle_diff(target_direction, angle());
			if(std::abs(anglediff) == 0){
				path.pop_front();
			} else{
				if(turningspeed == 0)
					break;
				float timeneeded = std::abs(anglediff/turningspeed);
				if(timeneeded <= dt){
					path[0].angle = target_direction;
					dt -= timeneeded;
				} else {
					path[0].angle += dt*turningspeed*anglediff/std::abs(anglediff);
					dt = 0;
				}
			}
		}
		else{
			Vec2d diff = path[1].position-path[0].position;
			float target_direction = diff.angle();
			float anglediff = angle_diff(target_direction, angle());
			if(std::abs(anglediff) != 0){
			//rotation
				if(turningspeed == 0)
					break;
				float timeneeded = std::abs(anglediff/turningspeed);
				if(timeneeded <= dt){
					path[0].angle = target_direction;
					dt -= timeneeded;
				} else {
					path[0].angle += dt*turningspeed*anglediff/std::abs(anglediff);
					dt = 0;
				}
			}
			else {
			//positioning
				if(speed == 0) break;
				float dd = diff.length();
				float timeneeded = dd/speed;
				if(timeneeded <= dt){
					path.pop_front();
					dt -= timeneeded;
				} else {
					path[0].position = path[0].position + diff.norm()*dt*speed;
					dt = 0;
				}
			}
		}
	}
}

int Particle::target_len() const{
	return path.size()-1;
}
const ParticleState& Particle::target(int i = 0) const{
	return path[i+1];
}

void Particle::set_state(const Vec2d &v, float angle){
	path[0].position = v;
	path[0].angle = angle;
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
	//update all particles
	for(size_t i = 0, sz = particles.size(); i<sz; ++i){
		particles[i]->update(dt);
	}
	//collision detection
	for(size_t i = 0, sz = particles.size(); i<sz; ++i){
		for(size_t j = i+1; j<sz; ++j){
			float dist2 = particles[i]->position().distance_to2(particles[j]->position());
			float safe_dist = particles[i]->radius + particles[j]->radius;
			float safe_dist2 = safe_dist*safe_dist;
			if(dist2 < safe_dist2){
				//collision
				particles[i]->collisions++;
				particles[j]->collisions++;
				float diff = sqrt(dist2) - sqrt(safe_dist2);
				Vec2d dirv(1,0);
				if(dist2 != 0)
				 	dirv = (particles[i]->position() - particles[j]->position()).norm();
				particles[j]->set_state(particles[j]->position() + dirv*diff, particles[j]->angle());
				particles[i]->set_state(particles[i]->position() - dirv*diff, particles[i]->angle());
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
		if(particles[i] != from && particles[i]->position().distance_to2(from->position()) <= range2)
			res.push_back(particles[i]);
	}
	return res;
}

int main(void){
	Particle *p = new Particle(0,0);
	World w;
	w.bind(p);
	printf("%f %f\n", p->position().x, p->position().y);
	delete p;
}
