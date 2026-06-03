import numpy as np
from pathlib import Path

from src.mesher import *
from src.mesh_cases import MESH_CASES
from src.physics import *
from src.metrics import *
from src.plots import *

d_dish = 1.0 
f_dish = 0.4
wavelength = 0.03

feed_position = np.array([0.0, 0.0, f_dish])
theta_deg = np.linspace(-90.0, 90.0, 721)
r_hat = observation_directions_theta_cut(theta_deg)

def run_mesh_case(case, name, results, is_reference):

    print(f"Running for mesh: {name}")

    if case["mesh_type"] == "polar":
        vertices, faces = generate_parabolic_dish_mesh(d_dish, f_dish, case["n_radial"], case["n_angular"])
    elif case["mesh_type"] == "variable":
        vertices, faces = generate_delaunay_parabolic_dish_mesh(d_dish, f_dish, case["n_radial"], case["h_center"], case["h_rim"])

    centers, areas, normals = triangle_geometry(vertices, faces)
    faces, centers, areas, normals = flip_normals_toward_feed(vertices, faces, normals, centers, feed_position)

    H_inc, R_hat, R_abs, h_hat = compute_incident_magnetic_field(centers, feed_position, wavelength,)
    J_s = compute_surface_current(normals, H_inc)
    F, E_pattern, power, power_db = compute_far_field_pattern(centers, areas, J_s, wavelength, r_hat,)

    results[name] = {
        "mesh": {
            "vertices": vertices, "faces": faces, "centers": centers, "areas": areas, "normals": normals,
        },  
        "far_field": {
            "F": F, "E_pattern": E_pattern, "power": power, "power_db": power_db, "theta_deg": theta_deg,
        },
    }
    results[name]["mesh_metrics"] = compute_mesh_metrics(centers,normals,f_dish)
    if not is_reference:
        results[name]["far_field_metrics"] = compute_far_field_metrics(power, results["reference"]["far_field"]["power"])

results = {}
run_mesh_case(MESH_CASES["reference"], "reference", results, True)
for name, case in MESH_CASES.items():
    if name != "reference":
        run_mesh_case(case, name, results, False)

Path("figures").mkdir(exist_ok=True)

plot_reference_summary(results["reference"])
plot_mesh_farfield_summary(results, case_names=("coarse", "medium", "fine"),)
plot_medium_vs_variable_summary(results,case_names=("medium", "variable"),)