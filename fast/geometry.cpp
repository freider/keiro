#include "geometry.hpp"
#include "vector2d.hpp"
#include <algorithm>
#include <cmath>

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
