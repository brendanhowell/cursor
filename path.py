import numpy as np
import math

class TimedPosition:
    def __init__(self, x=0.0, y=0.0, timestamp=0):
        self.x = x
        self.y = y
        self.timestamp = timestamp

    def pos(self):
        return self.x, self.y

    def arr(self):
        return np.array(self.pos(), dtype=float)

    def time(self):
        return self.timestamp

    def copy(self):
        return type(self)(self.x, self.y, self.timestamp)

    def scale(self, _x, _y):
        self.x *= _x
        self.y *= _y

    def rot(self, delta):
        co = np.cos(delta)
        si = np.sin(delta)
        xx = co * self.x - si * self.y
        yy = si * self.x + co * self.y
        self.x = xx
        self.y = yy

    def translate(self, x, y):
        self.x += x
        self.y += y

    def __repr__(self):
        return f"({self.x:.2f}, {self.y:.2f}, {self.timestamp})"


class Path:
    def __init__(self, vertices=None):
        if vertices:
            self.vertices = list(vertices)
        else:
            self.vertices = []

    def add(self, x, y, timestamp):
        self.vertices.append(TimedPosition(x, y, timestamp))

    def clear(self):
        self.vertices.clear()

    def copy(self):
        return type(self)(self.vertices.copy())

    def start_pos(self):
        if len(self.vertices) == 0:
            raise IndexError
        return self.vertices[0]

    def end_pos(self):
        if len(self.vertices) == 0:
            raise IndexError

        return self.vertices[-1]

    def bb(self):
        minx = min(self.vertices, key=lambda pos: pos.x).x
        miny = min(self.vertices, key=lambda pos: pos.y).y
        maxx = max(self.vertices, key=lambda pos: pos.x).x
        maxy = max(self.vertices, key=lambda pos: pos.y).y

        return minx, miny, maxx, maxy

    def morph(self, start, end):
        path = Path()
        end_np = self.end_pos().arr()
        start_np = self.start_pos().arr()
        new_end_np = np.array(end, dtype=float)
        new_start_np = np.array(start, dtype=float)

        for point in self.vertices:
            nparr = point.arr()

            dir_old = np.subtract(end_np, start_np)
            dir_new = np.subtract(new_end_np, new_start_np)
            mag_diff = np.linalg.norm(dir_new) / np.linalg.norm(dir_old)
            nparr = nparr * mag_diff
            path.add(nparr[0], nparr[1], point.timestamp)

        current_end = path.end_pos().arr()
        current_start = path.start_pos().arr()
        current_start_to_end = np.subtract(current_end, current_start)

        new_start_to_end = np.subtract(new_end_np, new_start_np)

        current_start_to_end = current_start_to_end / np.linalg.norm(current_start_to_end)
        new_start_to_end = new_start_to_end / np.linalg.norm(new_start_to_end)

        angle = np.arccos(np.clip(np.dot(current_start_to_end, new_start_to_end), -math.pi, math.pi))

        for p in path.vertices:
            p.rot(angle)

        translation = np.subtract(new_start_np, path.start_pos().arr())
        for p in path.vertices:
            p.translate(translation[0], translation[1])

        return path

    def __repr__(self):
        return f"Path({self.vertices})"

    def __len__(self):
        return len(self.vertices)


class PathCollection:
    def __init__(self, resolution):
        self.paths = []
        self.resolution = resolution

    def add(self, path, resolution):
        if resolution.width != self.resolution.width or resolution.height != self.resolution.height:
            raise Exception('New resolution is different to current. This should be handled somehow ..')
        self.paths.append(path)

    def get(self, index):
        if len(self.paths) < index:
            raise IndexError('Index too high')
        return self.paths[index]

    def __len__(self):
        return len(self.paths)

    def __repr__(self):
        return f"PathCollection({self.resolution}, {self.paths})"

    def bb(self):
        mi = self.min()
        ma = self.max()
        return mi[0], mi[1], ma[0], ma[1]

    def min(self):
        all_chained = [point for path in self.paths for point in path.vertices]
        minx = min(all_chained, key = lambda pos: pos.x).x
        miny = min(all_chained, key = lambda pos: pos.y).y
        return minx, miny

    def max(self):
        all_chained = [point for path in self.paths for point in path.vertices]
        maxx = max(all_chained, key=lambda pos: pos.x).x
        maxy = max(all_chained, key=lambda pos: pos.y).y
        return maxx, maxy