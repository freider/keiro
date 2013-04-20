/* physics.i */
%module vector2d
%{
#include "vector2d.hpp"
%}

class Vec2d{
public:
    %immutable;
    float x, y;
    %mutable;
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

%extend Vec2d {
    char* __str__() {
        static char tmp[1024];
        sprintf(tmp,"Vec2d(%f,%f)", $self->x,$self->y);
        return tmp;
    }
%pythoncode%{
    def __len__(self):
        return 2

    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        else:
            raise IndexError("Invalid subscript "+str(key)+" to Vec2d")

    def __setitem__(self, key, value):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        else:
            raise IndexError("Invalid subscript "+str(key)+" to Vec2d")

%}
};