import numpy as np
from scipy.spatial import Delaunay

def generate_parabolic_dish_mesh(
    diameter: float,
    focal_length: float,
    n_radial: int,
    n_angular: int,
):

    radius = diameter / 2.0

    vertices = []
    vertices.append([0.0, 0.0, 0.0])

    for i in range(1, n_radial + 1):
        rho = radius * i / n_radial
        for j in range(n_angular):
            phi = 2.0 * np.pi * j / n_angular
            x = rho * np.cos(phi)
            y = rho * np.sin(phi)
            z = rho**2 / (4.0 * focal_length)
            vertices.append([x, y, z])

    def vertex_id(i, j):
        return 1 + (i - 1) * n_angular + (j % n_angular)

    faces = []

    # center fan
    center = 0
    for j in range(n_angular):
        faces.append([center, vertex_id(1, j), vertex_id(1, j + 1)])

    # two triangles per quad
    for i in range(1, n_radial):
        for j in range(n_angular):
            p00 = vertex_id(i, j)
            p01 = vertex_id(i, j + 1)
            p10 = vertex_id(i + 1, j)
            p11 = vertex_id(i + 1, j + 1)
            faces.append([p00, p10, p11])
            faces.append([p00, p11, p01])

    return np.array(vertices, dtype=float), np.array(faces, dtype=int)


def triangle_geometry(vertices, faces):

    v0 = vertices[faces[:, 0]]
    v1 = vertices[faces[:, 1]]
    v2 = vertices[faces[:, 2]]
    centers = (v0 + v1 + v2) / 3.0
    cross = np.cross(v1 - v0, v2 - v0)
    double_areas = np.linalg.norm(cross, axis=1)
    areas = 0.5 * double_areas
    normals = cross / double_areas[:, None]

    return centers, areas, normals


def flip_normals_toward_feed(vertices, faces, normals, centers, feed_position):

    to_feed = feed_position[None, :] - centers
    dot = np.sum(normals * to_feed, axis=1)
    flipped_faces = faces.copy()
    needs_flip = dot < 0
    flipped_faces[needs_flip] = flipped_faces[needs_flip][:, [0, 2, 1]]
    centers, areas, normals = triangle_geometry(vertices, flipped_faces)

    return flipped_faces, centers, areas, normals


def generate_variable_polar_points(
    diameter: float,
    n_radial: int,
    h_center: float,
    h_rim: float,
    refinement_power: float = 2.0,
):

    radius = diameter / 2.0
    points = []
    points.append([0.0, 0.0])

    # increase angular refinement with radius
    for i in range(1, n_radial + 1):

        u = i / n_radial
        rho = radius * u
        h = h_center - (h_center - h_rim) * (u ** refinement_power)
        n_phi = max(8, int(np.ceil(2.0 * np.pi * rho / h)))

        for j in range(n_phi):
            phi = 2.0 * np.pi * j / n_phi
            x = rho * np.cos(phi)
            y = rho * np.sin(phi)
            points.append([x, y])

    return np.array(points, dtype=float)


def generate_delaunay_parabolic_dish_mesh(
    diameter,
    focal_length: float,
    n_radial: int,
    h_center: float,
    h_rim: float,
    refinement_power: float = 2.0,
):

    radius = diameter / 2.0

    points_2d = generate_variable_polar_points(diameter, n_radial, h_center, h_rim, refinement_power)

    tri = Delaunay(points_2d)
    faces = tri.simplices.copy()

    x = points_2d[:, 0]
    y = points_2d[:, 1]
    z = (x**2 + y**2) / (4.0 * focal_length)

    vertices = np.column_stack([x, y, z])

    return vertices, faces