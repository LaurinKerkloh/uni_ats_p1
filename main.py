from __future__ import annotations

import math
import tkinter as tk
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
        hypotenuse = abs(landmark.position - position)
        opposite = landmark.radius()
        if hypotenuse != 0:
            angle = math.asin(opposite / hypotenuse)
        else:
            angle = 0
        start = vector_to_center_of_landmark.direction() - angle
        if start < 0:
            start += (2 * math.pi)
        end = (vector_to_center_of_landmark.direction() + angle) % (2 * math.pi)
        return Feature(start, end)

    def width(self) -> float:
        width = self.end - self.start
        if self.start > self.end:
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
    landmarks: List[Landmark] = [Landmark(Vector(3.5, 2), 1), Landmark(Vector(3.5, -2), 1), Landmark(Vector(0, -4), 1)]
    snapshot = Retina(Vector(0, 0), landmarks)

    homing_vectors_2d: List[List[Vector]] = []
    errors = []
    for y in range(-7, 8):
        homing_vectors_2d.append([])
        for x in range(-7, 8):
            retina = Retina(Vector(x, y), landmarks)
            homing_vector = retina.homing_vector(snapshot)
            homing_vectors_2d[-1].append(retina.homing_vector(snapshot))
            errors.append(abs(homing_vector.direction() - Vector(-x, -y).direction()))

    average_error = sum(errors) / len(errors)

    window = tk.Tk()
    grid_step = 50
    width = len(homing_vectors_2d[0]) * grid_step
    height = len(homing_vectors_2d) * grid_step
    canvas = tk.Canvas(window, width=width, height=height)
    canvas.pack()
    for landmark in landmarks:
        center_x = width / 2
        center_y = height / 2
        landmark_x = center_x + landmark.position.x * grid_step
        landmark_y = center_y - landmark.position.y * grid_step
        canvas.create_oval(landmark_x - 25, landmark_y + 25, landmark_x + 25, landmark_y - 25)

    for y, homing_vectors in enumerate(homing_vectors_2d):
        for x, homing_vector in enumerate(homing_vectors):
            grid_center = Vector(grid_step / 2 + x * grid_step, grid_step / 2 + y * grid_step)
            start = grid_center - homing_vector.change_length(25)
            end = grid_center + homing_vector.change_length(25)
            canvas.create_line(start.x, height - start.y, end.x, height - end.y, arrow=tk.LAST)
            # print(round(math.degrees(homing_vector.direction()), 2), end='\t')
        # print()
    print(f"average error: {math.degrees(average_error)}°")
    window.mainloop()


if __name__ == '__main__':
    main()
