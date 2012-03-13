#ifndef _GEOMETRY_HPP
#define _GEOMETRY_HPP

#include "vector2d.hpp"

float linesegdist2(Vec2d l1, Vec2d l2, Vec2d p);
float line_distance2(Vec2d l11, Vec2d l12, Vec2d l21, Vec2d l22);
float angle_diff(float a1, float a2);

#endif