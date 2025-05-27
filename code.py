import math
import itertools
from matplotlib import pyplot as plt
from matplotlib.patches import Polygon

# Генераторы полигонов
def gen_rectangle(start_x=0, step=2):
    x = start_x
    while True:
        yield (
            (x, 0),
            (x, 1),
            (x + 1, 1),
            (x + 1, 0)
        )
        x += step

def gen_triangle(start_x=0, step=2):
    x = start_x
    h = math.sqrt(3) / 2  # высота равностороннего треугольника
    while True:
        yield (
            (x, 0),
            (x + 0.5, h),
            (x + 1, 0)
        )
        x += step

def gen_hexagon(start_x=0, step=3, radius=1):
    x = start_x
    while True:
        angles = [math.radians(60 * i) for i in range(6)]
        vertices = [(x + radius * math.cos(angle), radius * math.sin(angle)) for angle in angles]
        yield tuple(vertices)
        x += step

# Преобразования
def tr_translate(dx, dy):
    def translate(polygon):
        return tuple((x + dx, y + dy) for (x, y) in polygon)
    return translate

def tr_rotate(angle_deg, center=(0, 0)):
    angle = math.radians(angle_deg)
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    cx, cy = center
    def rotate(polygon):
        rotated = []
        for x, y in polygon:
            x_rel, y_rel = x - cx, y - cy
            x_new = x_rel * cos_a - y_rel * sin_a + cx
            y_new = x_rel * sin_a + y_rel * cos_a + cy
            rotated.append((x_new, y_new))
        return tuple(rotated)
    return rotate

def tr_symmetry(axis='x'):
    def reflect(polygon):
        if axis == 'x':
            return tuple((x, -y) for (x, y) in polygon)
        elif axis == 'y':
            return tuple((-x, y) for (x, y) in polygon)
        else:
            raise ValueError("Axis must be 'x' or 'y'")
    return reflect

def tr_homothety(k, center=(0, 0)):
    cx, cy = center
    def scale(polygon):
        return tuple((cx + (x - cx) * k, cy + (y - cy) * k) for (x, y) in polygon)
    return scale

# Фильтры
def flt_convex_polygon(polygon):
    n = len(polygon)
    if n < 3:
        return False
    sign = None
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i+1) % n]
        x3, y3 = polygon[(i+2) % n]
        dx1, dy1 = x2 - x1, y2 - y1
        dx2, dy2 = x3 - x2, y3 - y2
        cross = dx1 * dy2 - dx2 * dy1
        if cross == 0:
            continue
        curr_sign = 1 if cross > 0 else -1
        if sign is None:
            sign = curr_sign
        elif curr_sign != sign:
            return False
    return True

def flt_angle_point(point):
    def check(polygon):
        return any(math.isclose(x, point[0], abs_tol=1e-6) and math.isclose(y, point[1], abs_tol=1e-6) for (x, y) in polygon)
    return check

def flt_square(max_area):
    def check(polygon):
        area = 0.0
        n = len(polygon)
        for i in range(n):
            x1, y1 = polygon[i]
            x2, y2 = polygon[(i+1) % n]
            area += (x1 * y2 - x2 * y1)
        return abs(area) / 2.0 < max_area
    return check

def flt_short_side(max_length):
    def check(polygon):
        min_length = float('inf')
        n = len(polygon)
        for i in range(n):
            x1, y1 = polygon[i]
            x2, y2 = polygon[(i+1) % n]
            dx, dy = x2 - x1, y2 - y1
            length = math.hypot(dx, dy)
            if length < min_length:
                min_length = length
        return min_length < max_length
    return check

def flt_point_inside(point):
    def check(polygon):
        if not flt_convex_polygon(polygon):
            return False
        x_p, y_p = point
        n = len(polygon)
        sign = None
        for i in range(n):
            x1, y1 = polygon[i]
            x2, y2 = polygon[(i+1) % n]
            cross = (x2 - x1) * (y_p - y1) - (y2 - y1) * (x_p - x1)
            if cross == 0:
                continue
            curr_sign = 1 if cross > 0 else -1
            if sign is None:
                sign = curr_sign
            elif curr_sign != sign:
                return False
        return True
    return check

def flt_polygon_angles_inside(target_polygon):
    def check(polygon):
        if not flt_convex_polygon(polygon):
            return False
        for point in target_polygon:
            if flt_point_inside(point)(polygon):
                return True
        return False
    return check

# Визуализация
def visualize(polygons, limit=10):
    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    count = 0
    for polygon in polygons:
        if count >= limit:
            break
        patch = Polygon(polygon, closed=True, fill=None, edgecolor='blue')
        ax.add_patch(patch)
        count += 1
    ax.autoscale_view()
    plt.show()

# Примеры использования

# Обязательная часть: 7 фигур
print("Визуализация 7 фигур:")
rects = itertools.islice(gen_rectangle(), 2)
triangles = itertools.islice(gen_triangle(), 2)
hexagons = itertools.islice(gen_hexagon(), 3)
combined = itertools.chain(rects, triangles, hexagons)
visualize(combined, 7)

# Три параллельных ленты под углом
print("Три параллельных ленты под углом 45 градусов:")
original = gen_rectangle()
rotated = map(tr_rotate(45), original)
trans1 = map(tr_translate(0, 3), rotated)
trans2 = map(tr_translate(0, -3), rotated)
combined = itertools.chain(itertools.islice(rotated, 3), itertools.islice(trans1, 3), itertools.islice(trans2, 3))
visualize(combined, 9)

# Две пересекающиеся ленты
print("Две пересекающиеся ленты:")
original1 = gen_rectangle(step=3)
original2 = gen_rectangle(start_x=1.5, step=3)
rotated1 = map(tr_rotate(30), original1)
rotated2 = map(tr_rotate(30), original2)
combined = itertools.chain(itertools.islice(rotated1, 5), itertools.islice(rotated2, 5))
visualize(combined, 10)

# Две симметричные ленты треугольников
print("Две симметричные ленты треугольников:")
triangles = gen_triangle()
reflected = map(tr_symmetry('x'), triangles)
translated = map(tr_translate(0, 3), reflected)
combined = itertools.chain(itertools.islice(triangles, 5), itertools.islice(translated, 5))
visualize(combined, 10)

# Масштабированные четырехугольники
print("Масштабированные четырехугольники:")
original = gen_rectangle(step=4)
scaled = (tr_homothety(0.5 * k)(poly) for k, poly in enumerate(original, 1))
rotated = map(tr_rotate(45), scaled)
visualize(itertools.islice(rotated, 5), 5)
