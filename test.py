from homing_bees import *
import tkinter as tk


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
