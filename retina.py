import math
from typing import List


class Vector:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def direction(self):
        if self.x == 0:
            if self.y > 0:
                return math.pi / 2
            else:
                return 3 * math.pi / 2
        return math.atan(self.y / self.x) % (2 * math.pi)

    def __abs__(self):
        return math.sqrt((self.x * self.x) + (self.y * self.y))

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        Vector(self.x + other.x, self.y + other.y)


class Landmark:
    def __init__(self, position: Vector, diameter: float):
        self.position = position
        self.diameter = diameter

    def radius(self):
        return self.diameter / 2


class Feature:
    def __init__(self, start: float, end: float):
        self.start = start
        self.end = end

    @classmethod
    def from_position_and_landmark(cls, postion: Vector, landmark: Landmark):
        vector_to_center_of_landmark = landmark.position - postion
        hypotenuse = abs(landmark.position - postion)
        opposite = landmark.radius()
        angle = math.asin(opposite / hypotenuse)
        start = vector_to_center_of_landmark.direction() - angle
        end = vector_to_center_of_landmark.direction() + angle
        return Feature(start, end)

    def width(self):
        return self.end - self.start

    def center(self):
        return self.start + self.width() / 2


class Snapshot:
    def __init__(self, position: Vector, landmarks: List[Landmark]):
        self.features: List[Feature] = []
        for landmark in landmarks:
            self.features.append(Feature.from_position_and_landmark(position, landmark))

