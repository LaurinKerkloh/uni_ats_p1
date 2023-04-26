from __future__ import annotations

import math
from typing import List


class Vector:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def direction(self) -> float:
        direction = math.atan2(self.y, self.x)
        if direction < 0:
            direction += 2 * math.pi
        return direction

    def normalize(self) -> Vector:
        length = abs(self)
        if length == 0:
            return Vector(0, 0)
        return Vector(self.x / length, self.y / length)

    def change_length(self, length: float) -> Vector:
        normalized = self.normalize()
        return Vector(normalized.x * length, normalized.y * length)

    def __abs__(self) -> float:
        return math.sqrt((self.x * self.x) + (self.y * self.y))

    def __sub__(self, other) -> Vector:
        return Vector(self.x - other.x, self.y - other.y)

    def __add__(self, other) -> Vector:
        return Vector(self.x + other.x, self.y + other.y)


class Landmark:
    def __init__(self, position: Vector, diameter: float):
        self.position = position
        self.diameter = diameter

    def radius(self) -> float:
        return self.diameter / 2


class Feature:
    def __init__(self, start: float, end: float):
        self.start = start
        self.end = end

    @classmethod
    def from_position_and_landmark(cls, position: Vector, landmark: Landmark) -> Feature:
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
        return self.start > self.end

    def width(self) -> float:
        width = self.end - self.start
        if self.across_zero():
            width += (2 * math.pi)
        return width

    def center(self) -> float:
        return (self.start + self.width() / 2) % (2 * math.pi)

    def mapping(self, features: List[Feature]) -> Feature:

        closest_feature = features[0]
        shortest_distance = math.sin((abs(self.center() - closest_feature.center())) / 2)
        for feature in features[1:]:
            distance = math.sin((abs(self.center() - feature.center()) / 2))
            if shortest_distance > distance:
                shortest_distance = distance
                closest_feature = feature
        return closest_feature

    def overlaps(self, other: Feature) -> bool:
        a_start = self.start
        a_end = self.end
        b_start = other.start
        b_end = other.end
        if self.across_zero():
            a_end += 2 * math.pi
            b_start += 2 * math.pi
            b_end += 2 * math.pi
        if other.across_zero():
            b_end += 2 * math.pi

        return a_start < b_end and b_start < a_end

    def join(self, other: Feature) -> Feature:
        return Feature(min(self.start, other.start), max(self.end, other.end))

    def pos_v(self, snapshot_feature: Feature) -> Vector:
        vec = Vector(0, 0)
        if snapshot_feature.center() == self.center():
            return vec
        else:
            left = (snapshot_feature.center() < self.center())
            if (abs(snapshot_feature.center() - self.center())) > math.pi:
                left = not left
            if left:
                vec.x = math.cos(self.center() + (math.pi / 2))
                vec.y = math.sin(self.center() + (math.pi / 2))
            else:
                vec.x = math.cos(self.center() - (math.pi / 2))
                vec.y = math.sin(self.center() - (math.pi / 2))

            return vec

    def ang_v(self, snapshot_feature: Feature) -> Vector:
        vec = Vector(0, 0)
        if snapshot_feature.width() == self.width():
            return vec
        else:
            out = (snapshot_feature.width() > self.width())
            if out:
                vec.x = math.cos(self.center())
                vec.y = math.sin(self.center())
            else:
                vec.x = math.cos(self.center() + math.pi)
                vec.y = math.sin(self.center() + math.pi)
            return vec + vec + vec


class Retina:
    def __init__(self, position: Vector, landmarks: List[Landmark]):
        self.position: Vector = position
        self.dark_features: List[Feature] = []
        self.white_features: List[Feature] = []

        for landmark in landmarks:
            # dark_feature = Feature.from_position_and_landmark(position, landmark)

            self.dark_features.append(Feature.from_position_and_landmark(position, landmark))

        self.dark_features.sort(key=lambda f: f.center())

        for i in range(len(self.dark_features)):
            start = self.dark_features[i].end
            end = self.dark_features[(i + 1) % len(self.dark_features)].start
            self.white_features.append(Feature(start, end))

    def homing_vector(self, snapshot: Retina):
        vector = Vector(0, 0)
        for dark_feature in snapshot.dark_features:
            mapped_feature = dark_feature.mapping(self.dark_features)
            dark_feature.pos_v(mapped_feature)
            vector += mapped_feature.pos_v(dark_feature)
            vector += mapped_feature.ang_v(dark_feature)

        for white_feature in snapshot.white_features:
            mapped_feature = white_feature.mapping(self.white_features)
            white_feature.pos_v(mapped_feature)
            vector += mapped_feature.pos_v(white_feature)
            vector += mapped_feature.ang_v(white_feature)

        return vector.normalize()


def main():
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
