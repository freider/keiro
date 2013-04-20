#ifndef _VECTOR2D_HPP
#define _VECTOR2D_HPP

class Vec2d{
public:
    float x, y;
    Vec2d();
    Vec2d(float _x, float _y);
    Vec2d operator/(float f) const;
    Vec2d operator*(float f) const;
    Vec2d operator-(const Vec2d &v) const;
    Vec2d operator+(const Vec2d &v) const;
    bool operator==(const Vec2d &v) const;
    float distance_to(const Vec2d &v) const;
    float distance_to2(const Vec2d &v) const;
    float length() const;
    float length2() const;
    Vec2d norm() const;
    float dot(const Vec2d &v) const;
    float cross(const Vec2d &v) const;
    float angle(const Vec2d &v) const;
    float angle() const;
};

#endif