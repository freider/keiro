%module particle
%include "std_vector.i"
%{
    #include "particle.hpp"
%}
%template(pvector) std::vector<Particle*>; 
%template(ovector) std::vector<Obstacle*>; 

class ParticleState {
public:
    Vec2d position;
    float angle;
};

class Particle : public ParticleState {
    friend class World;
    World *world;
    std::deque<ParticleState> path;
public:
    Particle(float x=0, float y=0, float dir=1);
    ~Particle();
    float radius;
    float speed;
    float turningspeed;
    int collisions;
    Vec2d previous_position;
    Vec2d velocity;

    void waypoint_clear();
    void waypoint_push(const Vec2d &v);
    void waypoint_push(const Vec2d &v, float angle);
    void waypoint_pop();
    void waypoint_pop_first();
    int waypoint_len() const;
    const ParticleState &waypoint(int i=0) const;
    void update(float dt);
    void set_state(const Vec2d &v, float angle);
};