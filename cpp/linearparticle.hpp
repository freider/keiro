#include "particle.hpp"

class LinearParticle : public Particle {
public:
    LinearParticle(float x=0, float y=0, float dir=1);
    void update(float dt);
};
