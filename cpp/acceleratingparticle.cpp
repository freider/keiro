#include "acceleratingparticle.hpp"

void AcceleratingParticle::update(float dt) {
    int FORCEFACTOR = 2; // LOWER for larger force

    previous_position = position;
    if(!waypoint_len())
        return;
    
    Vec2d diff = waypoint().position-position;
    Vec2d force = diff.norm() * (speed/(FORCEFACTOR*dt));
    velocity = velocity + force * dt;
    angle = velocity.angle();

    if(velocity.length() > speed){
        velocity = velocity.norm() * speed; //velocity limiting
    }
    position = position + velocity * dt;

    diff = waypoint().position-position;
    if(diff.length() < radius){
        waypoint_pop_first(); //we're there
    }
}