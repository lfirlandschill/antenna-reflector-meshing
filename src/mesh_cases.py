MESH_CASES = {
    "coarse": {
        "mesh_type": "polar",
        "n_radial": 8,
        "n_angular": 16,
    },
    "medium": {
        "mesh_type": "polar",
        "n_radial": 16,
        "n_angular": 32,
    },
    "fine": {
        "mesh_type": "polar",
        "n_radial": 32,
        "n_angular": 64,
    },
    "variable": {
        "mesh_type": "variable",
        "n_radial": 16,
        "h_center": 0.085,
        "h_rim": 0.03,
        "refinement_power": 2.0,
    },
    "reference": {
        "mesh_type": "polar",
        "n_radial": 64,
        "n_angular": 128,
    },
}