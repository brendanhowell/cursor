import svgwrite
import os
from PIL import Image, ImageDraw


class PathIterator:
    def __init__(self, paths):
        self.paths = paths

    def points(self):
        for collection in self.paths:
            for path in collection:
                for point in path.vertices:
                    yield point, collection.resolution

    def connections(self, scaled=False):
        prev = None

        for collection in self.paths:
            for path in collection:
                is_first_vertex = True
                for point in path:
                    if is_first_vertex:
                        prev = point.copy()
                        is_first_vertex = False

                        continue

                    start = prev
                    end = point.copy()
                    prev = point.copy()

                    if scaled:
                        start.scale(collection.resolution.width, collection.resolution.height)
                        end.scale(collection.resolution.width, collection.resolution.height)

                    yield start, end


class CursorSVGRenderer:
    def __init__(self):
        self.save_path = 'data/svgs/'

    def render(self, paths, resolution, filename):
        dwg = svgwrite.Drawing(self.save_path + filename + '.svg', profile='tiny', size=(resolution.width, resolution.height))

        it = PathIterator(paths)
        for conn in it.connections(scaled=False):
            start = conn[0]
            end = conn[1]

            dwg.add(dwg.line(start.pos(), end.pos(), stroke=svgwrite.rgb(0, 0, 0, '%')))

        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        dwg.save()


class CursorGCodeRenderer:
    def __init__(self, feedrate_xy=2000, feedrate_z=1000, z_down=3.5, z_up=0.0, invert_y=True):
        self.save_path = 'data/gcode/'
        self.z_down = z_down
        self.z_up = z_up
        self.feedrate_xy = feedrate_xy
        self.feedrate_z = feedrate_z
        self.invert_y = invert_y

    def render(self, paths, filename):
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        filepath = os.path.abspath(self.save_path + filename + '.nc')
        print(F"Saving to {filepath}")
        with open(filepath, 'w') as file:
            file.write(F'G01 Z0.0 F{self.feedrate_z}\n')
            file.write(F'G01 X0.0 Y0.0 F{self.feedrate_xy}\n')
            for collection in paths:
                min = collection.min()
                max = collection.max()
                for path in collection:
                    x = path.start_pos().x
                    y = path.start_pos().y
                    if self.invert_y:
                        y = -y
                    file.write(F'G01 X{x:.2f} Y{y:.2f} F{self.feedrate_xy}\n')
                    file.write(F'G01 Z{self.z_down} F{self.feedrate_z}\n')
                    for line in path.vertices:
                        x = line.x
                        y = line.y
                        if self.invert_y:
                            y = -y
                        file.write(F'G01 X{x:.2f} Y{y:.2f} F{self.feedrate_xy}\n')
                    file.write(F'G01 Z{self.z_up} F{self.feedrate_z}\n')


class JpegRenderer:
    def __init__(self):
        self.save_path = 'data/jpgs/'

    def render(self, paths, filename, scale=1.0):
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        if len(paths) == 0:
            return

        bb = paths[0].bb()

        abs_scaled_bb = (abs(bb[0] * scale), abs(bb[1] * scale), abs(bb[2] * scale), abs(bb[3] * scale))

        img = Image.new('RGB', (int(abs_scaled_bb[0] + abs_scaled_bb[2]), int(abs_scaled_bb[1] + abs_scaled_bb[3])), 'white')
        img_draw = ImageDraw.ImageDraw(img)

        it = PathIterator(paths)

        for conn in it.connections(scaled=False):
            start = conn[0]
            end = conn[1]

            # offset paths when passed bb starts in negative space
            if bb[0] * scale < 0:
                start.x += abs_scaled_bb[0]
                end.x += abs_scaled_bb[0]

            if bb[1] < 0:
                start.y += abs_scaled_bb[1]
                end.y += abs_scaled_bb[1]

            img_draw.line(xy=(start.x * scale, start.y * scale, end.x * scale, end.y * scale), fill='black', width=1)

        filepath = os.path.abspath(self.save_path + filename + '.jpg')
        print(F"Saving to {filepath}")
        img.save(filepath, 'JPEG')
