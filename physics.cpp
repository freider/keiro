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
	position = vec;
	angle = dir;
}

Particle::~Particle(){
	if(world != NULL)
		world->unbind(this);
}
void Particle::waypoint_clear(){
	path.clear();
}

void Particle::waypoint_push(const Vec2d &v){
	//default angle = angle from last waypoint to this waypoint
	Vec2d last_waypoint = path.size()==0?position:path.back().position;
	if( !(v == last_waypoint) )
		waypoint_push(v, (v-last_waypoint).angle());
}

void Particle::waypoint_push(const Vec2d &v, float angle){
	ParticleState st = {v, angle};
	path.push_back(st);
}

void Particle::waypoint_pop(){
	path.pop_back();
}

void Particle::waypoint_pop_first(){
	path.pop_front();
}

int Particle::waypoint_len() const{
	return path.size();
}
const ParticleState& Particle::waypoint(int i) const{
	return path[i];
}

void Particle::update(float dt){
	while(dt>0 && waypoint_len() > 0){
		float anglediff;
		float waypoint_direction;
		Vec2d diff = waypoint().position-position;
		if(position == waypoint().position){
			waypoint_direction = waypoint().angle;
			anglediff = angle_diff(waypoint_direction, angle);
		}
		else{
			waypoint_direction = diff.angle();
			anglediff = angle_diff(waypoint_direction, angle);
		}
		if(std::abs(anglediff) != 0){
			if(turningspeed == 0)
				break;
			float timeneeded = std::abs(anglediff/turningspeed);
			if(timeneeded <= dt){
				angle = waypoint_direction;
				dt -= timeneeded;
			}
			else {
				angle += dt*turningspeed*anglediff/std::abs(anglediff);
				dt = 0;
			}
		}
		else if(!(position == waypoint().position)){
			//positioning
			if(speed == 0) break;
			float dd = diff.length();
			float timeneeded = dd/speed;
			if(timeneeded <= dt){
				position = waypoint().position;
				dt -= timeneeded;
			}
			else {
				position = position + diff.norm()*dt*speed;
				dt = 0;
			}
		}
		if(std::abs(angle_diff(angle, waypoint().angle)) == 0 && position == waypoint().position){
			waypoint_pop_first(); //we're there
		}
	}
}


void Particle::set_state(const Vec2d &v, float angle){
	position = v;
	angle = angle;
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
			float dist2 = particles[i]->position.distance_to2(particles[j]->position);
			float safe_dist = particles[i]->radius + particles[j]->radius;
			float safe_dist2 = safe_dist*safe_dist;
			if(dist2 < safe_dist2){
				//collision
				particles[i]->collisions++;
				particles[j]->collisions++;
				float diff = sqrt(dist2) - sqrt(safe_dist2);
				Vec2d dirv(1,0);
				if(dist2 != 0)
				 	dirv = (particles[i]->position - particles[j]->position).norm();
				particles[j]->set_state(particles[j]->position + dirv*diff, particles[j]->angle);
				particles[i]->set_state(particles[i]->position - dirv*diff, particles[i]->angle);
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
