import numpy as np

def compute_mesh_metrics(centers, normals, focal_length):

    num_triangles = len(centers)

    x = centers[:, 0]
    y = centers[:, 1]

    exact_normals = np.column_stack([
        -x / (2.0 * focal_length),
        -y / (2.0 * focal_length),
        np.ones_like(x),
    ])

    exact_normals /= np.linalg.norm(exact_normals, axis=1)[:, None]
    alignment = np.sum(normals * exact_normals, axis=1)
    exact_normals[alignment < 0.0] *= -1.0

    normal_dots = np.sum(normals * exact_normals, axis=1)
    normal_dots = np.clip(normal_dots, -1.0, 1.0)

    normal_error_deg = np.rad2deg(np.arccos(normal_dots))

    return {
        "num_triangles": int(num_triangles),
        "normal_error_mean_deg": float(np.mean(normal_error_deg)),
        "normal_error_max_deg": float(np.max(normal_error_deg)),
    }

def compute_far_field_metrics(power, reference_power):

    power_norm = power / np.max(power)
    reference_norm = reference_power / np.max(reference_power)
    rms_error = np.sqrt(np.mean((power_norm - reference_norm) ** 2))

    return {
        "rms_pattern_error": float(rms_error),
    }