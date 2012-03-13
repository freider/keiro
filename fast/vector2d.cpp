#include <cmath>
#include "vector2d.hpp"

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
