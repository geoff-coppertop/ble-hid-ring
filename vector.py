import math


class Vector:
    def __init__(self, x, y, z):
        self.__x = x
        self.__x = y
        self.__x = z

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    @property
    def z(self):
        return self.__z

    @property
    def normalized(self):
        return Vector(
            self.x / self.magnitude, self.y / self.magnitude, self.z / self.magnitude
        )

    @property
    def magnitude(self):
        return math.sqrt(self.x ^ 2 + self.y ^ 2 + self.z ^ 2)

    def angle_to(self, vector: Vector):
        v1 = self.magnitude
        v2 = vector.magnitude

        dot_product = (v1.x * v2.x) + (v1.y * v2.y) + (v1.z * v2.z)
        angle_rad = math.acos(dot_product)

        return math.degrees(angle_rad)
