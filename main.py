import math
from typing import List


class Vector:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def direction(self):
        direction = math.atan2(self.y, self.x)
        if direction < 0:
            direction += 2 * math.pi
        return direction

    def __abs__(self):
        return math.sqrt((self.x * self.x) + (self.y * self.y))

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)


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
    def from_position_and_landmark(cls, position: Vector, landmark: Landmark):
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

    def width(self):
        width = self.end - self.start
        if self.start > self.end:
            width += (2 * math.pi)
        return width

    def center(self):
        return (self.start + self.width() / 2) % (2 * math.pi)


class Retina:
    def __init__(self, position: Vector, landmarks: List[Landmark]):
        self.dark_features: List[Feature] = []
        self.white_features: List[Feature] = []

        for landmark in landmarks:
            self.dark_features.append(Feature.from_position_and_landmark(position, landmark))

        self.dark_features.sort(key=lambda f: f.center())

        for i in range(len(self.dark_features)):
            if ((math.sin(abs((self.dark_features[i].center() - self.dark_features[(i + 1) % 3].center()) / 2))) >
                    (math.sin((self.dark_features[i].width() / 2 + self.dark_features[
                        (i + 1) % 3].width() / 2) / 2))):  # absolute distance of centers > sum of angles
                start = self.dark_features[i].end
                end = self.dark_features[(i + 1) % 3].start
            else:
                start = self.dark_features[(i + 1) % 3].start
                end = self.dark_features[i].end
            self.white_features.append(Feature(start, end))


class Pair:
    def __init__(self, snap: Feature, ret: Feature):
        self.snap = snap
        self.ret = ret

    def pos_v(self):
        vec = Vector(0, 0)
        if self.snap.center() == self.ret.center():
            return vec
        else:
            left = (self.snap.center() < self.ret.center())
            if (abs(self.snap.center() - self.ret.center())) > math.pi:
                left = False if (left == True) else True
            if left:
                vec.x = math.cos(self.ret.center() + (math.pi / 2))
                vec.y = math.sin(self.ret.center() + (math.pi / 2))
            else:
                vec.x = math.cos(self.ret.center() - (math.pi / 2))
                vec.y = math.sin(self.ret.center() - (math.pi / 2))

            return vec

    def ang_v(self):
        vec = Vector(0, 0)
        if self.snap.width() == self.ret.width():
            return vec
        else:
            out = (self.snap.width() > self.ret.width())
            if out:
                vec.x = math.cos(self.ret.center())
                vec.y = math.sin(self.ret.center())
            else:
                vec.x = math.cos(self.ret.center() + math.pi)
                vec.y = math.sin(self.ret.center() + math.pi)
            return vec + vec + vec


def mapping(x: Feature, y: List[Feature]):
    buff = math.sin((abs(x.center() - y[0].center())) / 2)
    idx = 0
    for i in range(1, len(y)):
        if buff > math.sin((abs(x.center() - y[i].center()) / 2)):
            buff = math.sin((abs(x.center() - y[i].center())) / 2)
            idx = i
    return idx


def main():
    landmarks: List[Landmark] = [Landmark(Vector(3.5, 2), 1), Landmark(Vector(3.5, -2), 1), Landmark(Vector(0, -4), 1)]
    snapshot = Retina(Vector(0, 0), landmarks)
    homing_vectors: List[Vector] = []

    for x in range(-7, 8):
        for y in range(-7, 8):
            pairs: List[Pair] = []
            retina = Retina(Vector(x, y), landmarks)

            for i in range(3):
                pairs.append(
                    Pair(snapshot.dark_features[i],
                         retina.dark_features[mapping(snapshot.dark_features[i], retina.dark_features)]))
                pairs.append(Pair(snapshot.white_features[i],
                                  retina.white_features[mapping(snapshot.white_features[i], retina.white_features)]))

            vec = Vector(0, 0)
            for pair in pairs:
                vec = vec + pair.pos_v()
                vec = vec + pair.ang_v()
            homing_vectors.append(vec)

    idx = 0
    for vec in homing_vectors:
        print(round(vec.direction() * 57.3, 2), end='\t')
        if (idx % 15) == 14:
            print()
        idx += 1


if __name__ == '__main__':
    main()
