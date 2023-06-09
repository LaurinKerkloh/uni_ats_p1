"""
Implementation of the algorythm described in the Paper
"How honey bees use landmarks to guide their return to a food source"
Autonome Systeme Praktikum 1
Laurin Kerkloh und André Dolata
"""
from __future__ import annotations

import math
from typing import List


class Vector:
    """
    This class represents a 2d Vector
    Attributes:
         x-coordinate : float
         y-coordinate : float
    """

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def direction(self) -> float:
        """
        :return: the direction of the Vector
        """
        direction = math.atan2(self.y, self.x)
        if direction < 0:
            direction += 2 * math.pi
        return direction

    def normalize(self) -> Vector:
        """
        :return: a normalized version of the Vector
        """
        length = abs(self)
        if length == 0:
            return Vector(0, 0)
        return Vector(self.x / length, self.y / length)

    def change_length(self, length: float) -> Vector:
        """
        :param length:
        :return: a copy of the Vector with the provided length
        """
        normalized = self.normalize()
        return Vector(normalized.x * length, normalized.y * length)

    def __abs__(self) -> float:
        """
        Overloads the absolute operator
        :return: The absolute value of the Vector
        """
        return math.sqrt((self.x * self.x) + (self.y * self.y))

    def __sub__(self, other) -> Vector:
        """
        Overloads the subtraction operator -
        :param other:
        :return: The result of the subtraction of this vector minus the other
        """
        return Vector(self.x - other.x, self.y - other.y)

    def __add__(self, other) -> Vector:
        """
        Overloads the addition operator +
        :param other:
        :return: The result of the addition of this vector plus the other
        """
        return Vector(self.x + other.x, self.y + other.y)


class Landmark:
    """
    This class represents a Landmark.

    Attributes:
        position: Vector
        diameter: float
    """
    def __init__(self, position: Vector, diameter: float):
        self.position = position
        self.diameter = diameter

    def radius(self) -> float:
        """
        :return: the radius of the Landmark
        """
        return self.diameter / 2


class Feature:
    """
    This class represents a feature on a circular retina.
    Described by the angular position of the start and end in radians.
    Attributes:
        start: float
        end: float

    """
    def __init__(self, start: float, end: float):
        self.start = start
        self.end = end

    @classmethod
    def from_position_and_landmark(cls, position: Vector, landmark: Landmark) -> Feature:
        """
        This class method returns a new Feature based on the position of the retina and a given landmark.
        :param position:
        :param landmark:
        :return:
        """
        vector_to_center_of_landmark = landmark.position - position
        hypotenuse_length = abs(landmark.position - position)
        opposite_length = landmark.radius()
        if hypotenuse_length != 0:
            angle = math.asin(opposite_length / hypotenuse_length)
        else:
            angle = 0
        start = vector_to_center_of_landmark.direction() - angle
        if start < 0:
            start += (2 * math.pi)
        end = (vector_to_center_of_landmark.direction() + angle) % (2 * math.pi)
        return Feature(start, end)

    def across_zero(self) -> bool:
        """
        :return: True if the feature extends over the 0 degree point
        """
        return self.start > self.end

    def width(self) -> float:
        """
        :return: the angular extent of the feature
        """
        width = self.end - self.start
        if self.across_zero():
            width += (2 * math.pi)
        return width

    def center(self) -> float:
        """
        :return: the center point of the feature
        """
        return (self.start + self.width() / 2) % (2 * math.pi)

    def find_closest(self, features: List[Feature]) -> Feature:
        """
        Finds the feature from a list with the center point,
        which is located nearest to the center point of this feature.
        :param features: list of features
        :return: the closest feature
        """
        closest_feature = features[0]
        shortest_distance = math.sin((abs(self.center() - closest_feature.center())) / 2)
        for feature in features[1:]:
            distance = math.sin((abs(self.center() - feature.center()) / 2))
            if shortest_distance > distance:
                shortest_distance = distance
                closest_feature = feature
        return closest_feature

    def overlaps(self, other: Feature) -> bool:
        """
        :param other:
        :return: True if this feature overlaps with the other
        """
        f1 = self if self.center() < other.center() else other
        f2 = other if self.center() < other.center() else self

        if f1.across_zero() and f2.across_zero():
            return True
        if (f1.across_zero() or f2.across_zero()) and f1.start < f2.end:
            return True
        if f1.end > f2.start:
            return True
        return False

    @classmethod
    def test_overlap(cls):
        """
        a test function for the overlap function;
        only needed for testing
        """
        assert Feature(math.radians(50), math.radians(100)).overlaps(
            Feature(math.radians(20), math.radians(55))) is True, f"t1 failed"
        assert Feature(math.radians(50), math.radians(100)).overlaps(
            Feature(math.radians(50), math.radians(100))) is True, f"t2 failed"
        assert Feature(math.radians(50), math.radians(100)).overlaps(
            Feature(math.radians(60), math.radians(90))) is True, f"t3 failed"
        assert Feature(math.radians(50), math.radians(100)).overlaps(
            Feature(math.radians(90), math.radians(110))) is True, f"t4 failed"
        assert Feature(math.radians(50), math.radians(100)).overlaps(
            Feature(math.radians(60), math.radians(90))) is True, f"t5 failed"
        assert Feature(math.radians(50), math.radians(100)).overlaps(
            Feature(math.radians(20), math.radians(30))) is False, f"t6 failed"
        assert Feature(math.radians(50), math.radians(100)).overlaps(
            Feature(math.radians(110), math.radians(150))) is False, f"t7 failed"

        assert Feature(math.radians(350), math.radians(10)).overlaps(
            Feature(math.radians(5), math.radians(15))) is True, f"t8 failed"
        assert Feature(math.radians(350), math.radians(10)).overlaps(
            Feature(math.radians(345), math.radians(355))) is True, f"t9 failed"
        assert Feature(math.radians(350), math.radians(10)).overlaps(
            Feature(math.radians(355), math.radians(359))) is True, f"t10 failed"
        assert Feature(math.radians(350), math.radians(10)).overlaps(
            Feature(math.radians(1), math.radians(9))) is True, f"t11 failed"
        assert Feature(math.radians(350), math.radians(10)).overlaps(
            Feature(math.radians(5), math.radians(355))) is True, f"t12 failed"
        assert Feature(math.radians(350), math.radians(10)).overlaps(
            Feature(math.radians(15), math.radians(20))) is False, f"t13 failed"
        assert Feature(math.radians(350), math.radians(10)).overlaps(
            Feature(math.radians(340), math.radians(345))) is False, f"t14 failed"

        assert Feature(math.radians(350), math.radians(10)).overlaps(
            Feature(math.radians(340), math.radians(5))) is True, f"t15 failed"
        assert Feature(math.radians(350), math.radians(10)).overlaps(
            Feature(math.radians(355), math.radians(15))) is True, f"t16 failed"
        assert Feature(math.radians(350), math.radians(10)).overlaps(
            Feature(math.radians(340), math.radians(15))) is True, f"t17 failed"
        assert Feature(math.radians(350), math.radians(10)).overlaps(
            Feature(math.radians(355), math.radians(5))) is True, f"t18 failed"

    def turn_vector(self, snapshot_feature: Feature) -> Vector:
        """
        Calculates a turn vector based on this feature and the provided feature from the snapshot.
        :param snapshot_feature:
        :return:
        """
        if snapshot_feature.center() == self.center():
            return Vector(0, 0)

        left = (snapshot_feature.center() < self.center())
        if (abs(snapshot_feature.center() - self.center())) > math.pi:
            left = not left

        if self.width() > math.pi:
            left = not left

        if left:
            return Vector(math.cos(self.center() + (math.pi / 2)), math.sin(self.center() + (math.pi / 2)))
        else:
            return Vector(math.cos(self.center() - (math.pi / 2)), math.sin(self.center() - (math.pi / 2)))

    def approach_vector(self, snapshot_feature: Feature) -> Vector:
        """

        :param snapshot_feature:
        :return:
        """
        if snapshot_feature.width() == self.width():
            return Vector(0, 0)

        out = (snapshot_feature.width() > self.width())
        if out:
            vec = Vector(math.cos(self.center()), math.sin(self.center()))
            return vec + vec + vec
        else:
            vec = Vector(math.cos(self.center() + math.pi), math.sin(self.center() + math.pi))
            return vec + vec + vec


class Retina:
    """
    This class represents a Retina. It stores a collection of dark and white features.
    Attributes:
        position: Vector
        dark_features: List[Feature]
        white_features: List[Feature]
    """
    def __init__(self, position: Vector, landmarks: List[Landmark]):
        """
        This constructs and stores the retina features for a given position and a given list of landmarks.
        :param position: The position where the Retina is located
        :param landmarks: a list of landmarks
        """
        self.position: Vector = position
        self.dark_features: List[Feature] = []
        self.white_features: List[Feature] = []

        for landmark in landmarks:
            self.dark_features.append(Feature.from_position_and_landmark(position, landmark))

        self.dark_features.sort(key=lambda f: f.center())

        for i in range(len(self.dark_features)):
            f1 = self.dark_features[i]
            f2 = self.dark_features[(i + 1) % len(self.dark_features)]
            if f1.overlaps(f2):
                continue
            self.white_features.append(Feature(f1.end, f2.start))

    def homing_vector(self, snapshot: Retina):
        """
        Calculates the homing vector for the current retina based on a given snapshot.
        :param snapshot: A retina to which we want to return
        :return: the homing vector
        """
        vector = Vector(0, 0)
        for dark_feature in snapshot.dark_features:
            mapped_feature = dark_feature.find_closest(self.dark_features)
            dark_feature.turn_vector(mapped_feature)
            vector += mapped_feature.turn_vector(dark_feature)
            vector += mapped_feature.approach_vector(dark_feature)

        for white_feature in snapshot.white_features:
            mapped_feature = white_feature.find_closest(self.white_features)
            white_feature.turn_vector(mapped_feature)
            vector += mapped_feature.turn_vector(white_feature)
            vector += mapped_feature.approach_vector(white_feature)

        return vector.normalize()


def main():
    """
    A CLI for manual usage.
    """
    landmarks: List[Landmark] = []
    print("No input validation implemented, so be careful!")
    print("Setup:")
    while True:
        print("Initialising landmark...")
        print("Input the x coordinate of the landmark:")
        x = float(input())
        print("Input the y coordinate of the landmark:")
        y = float(input())
        print("Input the diameter of the landmark:")
        diameter = float(input())

        landmarks.append(Landmark(Vector(x, y), diameter))
        print("Do you want to add another landmark [y/n]?")
        another = input()
        if another.lower() != "y":
            break

    snapshot = Retina(Vector(0, 0), landmarks)

    while True:
        print("Find homing vector...")
        print("Input the x coordinate:")
        x = float(input())
        print("Input the y coordinate:")
        y = float(input())

        retina = Retina(Vector(x, y), landmarks)
        homing_vector = retina.homing_vector(snapshot)
        print(f"Direction of the homing vector in degrees: {math.degrees(homing_vector.direction())}")
        print("Do you want to calculate another homing vector [y/n]?")
        another = input()
        if another.lower() != "y":
            break


if __name__ == '__main__':
    main()
