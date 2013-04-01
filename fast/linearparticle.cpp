#include <cmath>

#include "linearparticle.hpp"
#include "vector2d.hpp"
#include "geometry.hpp"

LinearParticle::LinearParticle(float x, float y, float dir) : Particle(x, y, dir) {}

void LinearParticle::update(float dt){
	previous_position = position;
	if(waypoint_len() == 0) {
		velocity = Vec2d(0, 0);
	}
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
		if(std::abs(anglediff) != 0.0){
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

int main(){
    printf("Hej!\n");
    LinearParticle p((float)1.0, (float)2.0, (float)0);
    printf("%f %f\n", p.position.x, p.position.y);
    return 0;
}
