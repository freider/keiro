#include <cmath>
#include "geometry.hpp"
#include "particle.hpp"

Particle::Particle(float x, float y, float dir)
    :world(NULL),
    radius(0),
    speed(0),
    collisions(0),
    velocity(0,0)
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
    return (int)path.size();
}
const ParticleState& Particle::waypoint(int i) const{
    return path[i];
}

void Particle::set_state(const Vec2d &v, float angle_){
    position = v;
    angle = angle_;
}

Obstacle::Obstacle(const Vec2d &p1, const Vec2d &p2) :
    world(NULL),
    p1(p1),
    p2(p2)
{
}

Obstacle::~Obstacle(){
    if(world != NULL)
        world->unbind(this);
}


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
                float diff = (float)sqrt(dist2) - (float)sqrt(safe_dist2);
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
//              float diff = sqrt(dist2) - sqrt(safe_dist2);
                Vec2d dirv(1,0);
                Vec2d movement = particles[i]->position - particles[i]->previous_position;
                particles[i]->set_state(particles[i]->previous_position, particles[j]->angle); //TODO: remove
//              if(movement.length2() != 0)
//                  dirv = (particles[i]->position - particles[j]->position).norm();
                //particles[j]->set_state(particles[j]->position + dirv*diff, particles[j]->angle);
            }
        }
    }
}

int World::num_particles(){
    return (int)particles.size();
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
            else if(linesegdist2(from->position, in_range[i]->position, in_range[j]->position) <= (in_range[j]->radius)*(in_range[j]->radius)){
                occluded = true;
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
