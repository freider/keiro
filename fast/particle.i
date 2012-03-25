%module particle
%include vector2d.i
%{
    #include "particle.hpp"
    #include "linearparticle.hpp"
%}

class ParticleState {
public:
    Vec2d position;
    float angle;
};

class Particle : public ParticleState {
public:
    float radius;
    float speed;
    float turningspeed;
    int collisions;
    Vec2d previous_position;
    Vec2d velocity;

    Particle(float x=0, float y=0, float dir=1);
    virtual ~Particle();
    
    void waypoint_clear();
    void waypoint_push(const Vec2d &v);
    void waypoint_push(const Vec2d &v, float angle);
    void waypoint_pop();
    void waypoint_pop_first();
    int waypoint_len() const;
    const ParticleState &waypoint(int i=0) const;
    void set_state(const Vec2d &v, float angle);
    virtual void update(float dt)=0;
};


class LinearParticle : public Particle {
public:
    LinearParticle(float x=0, float y=0, float dir=1);
    void update(float dt);
};
