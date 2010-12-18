#include "physics.h"
#include <vector>
#include <cmath>
#include <cstdio>
#include <cassert>
#include <algorithm>

Vec2d::Vec2d():x(0),y(0){
}
Vec2d::Vec2d(float _x, float _y):x(_x),y(_y){
}
float Vec2d::length2() const{
	return x*x + y*y;
}
float Vec2d::length() const{
	return sqrt(length2());
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
float Vec2d::cross(const Vec2d &v) const{
	return x*v.y - v.x*y;
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

int _sign(float f) {
	if (f == 0)
		return 0;
	else if (f < 0)
		return -1;
	else
		return 1;
}

float line_distance2(Vec2d l11, Vec2d l12, Vec2d l21, Vec2d l22){
	if (_sign((l21 - l11).cross(l22 - l11)) != _sign((l21 - l12).cross(l22 - l12)) &&
		_sign((l11 - l21).cross(l12 - l21)) != _sign((l11 - l22).cross(l12 - l22)))
		return 0;
	float dists[] = {linesegdist2(l11, l12, l21), linesegdist2(l11, l12, l22),
		linesegdist2(l21, l22, l11), linesegdist2(l21, l22, l12)};
	return *std::min_element(dists, dists+4);
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
	velocity(0,0),
	world(NULL)
{
	Vec2d vec(x, y);
	previous_position = position = vec;
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
	Vec2d last_waypoint = path.size()==0 ? position : path.back().position;
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
	int FORCEFACTOR = 2; // LOWER for larger force

	previous_position = position;
	if(!waypoint_len()) return;
	
	Vec2d diff = waypoint().position-position;
	Vec2d force = diff.norm() * (speed/(FORCEFACTOR*dt));
	velocity = velocity + force * dt;
	angle = velocity.angle();

	if(velocity.length() > speed) velocity = velocity.norm() * speed; //velocity limiting
	position = position + velocity * dt;

	diff = waypoint().position-position;
	if(diff.length() < radius) waypoint_pop_first(); //we're there
}

/*
void Particle::update(float dt){
	previous_position = position;
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
			velocity = Vec2d(0,0);
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
			velocity = diff.norm()*speed;
			if(timeneeded <= dt){
				position = waypoint().position;
				dt -= timeneeded;
			}
			else {
				position = position + velocity*dt;
				dt = 0;
			}
		}
		if(std::abs(angle_diff(angle, waypoint().angle)) == 0 && position == waypoint().position){
			waypoint_pop_first(); //we're there
			velocity = Vec2d(0,0); //stop
		}
	}
}
*/

void Particle::set_state(const Vec2d &v, float angle){
	position = v;
	angle = angle;
}


Obstacle::Obstacle(const Vec2d &p1, const Vec2d &p2) : p1(p1), p2(p2), world(NULL) { }
Obstacle::~Obstacle(){
	if(world != NULL)
		world->unbind(this);
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

void World::unbind(Obstacle *l){
	for(size_t i = 0; i<obstacles.size(); ++i){
		if(obstacles[i] == l){
			obstacles.erase(obstacles.begin() + i);
			--i;
		}
	}
	l->world = NULL;
}

void World::bind(Particle *p) {
	particles.push_back(p);
	p->world = this;
}

void World::bind(Obstacle *l) {
	obstacles.push_back(l);
	l->world = this;
}

void World::update(float dt){
	//update all particles
	for(size_t i = 0, sz = particles.size(); i<sz; ++i){
		particles[i]->update(dt);
	}
	//collision detection between all pairs of particles
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
	
	//collision detection between particles and obstacles
	for (size_t i = 0, sz = particles.size(); i<sz; ++i) {
		for(size_t j = 0, oz = obstacles.size(); j<oz; ++j) {
			float dist2 = linesegdist2(obstacles[j]->p1, obstacles[j]->p2, particles[i]->position);
			float safe_dist = particles[i]->radius;
			float safe_dist2 = safe_dist*safe_dist;
			if(dist2 < safe_dist2){
				//collision
				particles[i]->collisions++;
//				float diff = sqrt(dist2) - sqrt(safe_dist2);
				Vec2d dirv(1,0);
				Vec2d movement = particles[i]->position - particles[i]->previous_position;
				particles[i]->set_state(particles[i]->previous_position, particles[j]->angle); //TODO: remove
//				if(movement.length2() != 0)
//				 	dirv = (particles[i]->position - particles[j]->position).norm();
				//particles[j]->set_state(particles[j]->position + dirv*diff, particles[j]->angle);
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

std::vector<Particle*> World::particles_in_view_range(const Particle *from, float range) const{
	float range2 = range*range;
	std::vector<Particle*> in_range;
	std::vector<Particle*> res;
	for(size_t i = 0, sz = particles.size(); i<sz; ++i){
		if(particles[i] != from && particles[i]->position.distance_to2(from->position) <= range2)
			in_range.push_back(particles[i]);
	}

	bool occluded;
	for(size_t i = 0, sz = in_range.size(); i<sz; ++i){ // go through pedestrians in range
		occluded = false;
		for(size_t j = 0; j<sz; ++j){ // go through all other pedestrians in range
			if(i == j)
				continue;
			else if(linesegdist2(from->position, in_range[i]->position, in_range[j]->position) <= (in_range[j]->radius)*(in_range[j]->radius)){							occluded = true;
				break;
			}
		}
		if(!occluded){
			for(size_t j = 0, oz = obstacles.size(); j<oz; ++j) {
				if((from->position.distance_to(obstacles[j]->p1) <= range) || (from->position.distance_to(obstacles[j]->p2) <= range)) // obstacle in range
				if(line_distance2(from->position, in_range[i]->position, obstacles[j]->p1, obstacles[j]->p2) == 0){ // behind an obstacle
					occluded = true;
					break;
				}
			}
		}
		if(!occluded)
			res.push_back(in_range[i]);
	}
	return res;
}

std::vector<Obstacle*> World::get_obstacles() const {
	return obstacles;
}
/*
TODO: prototype in python first
float freepath_probability(std::vector<Particle*> particles, Vec2d l1, Vec2d l2, float start_time, float speed){
	
}*/
