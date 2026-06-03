import numpy as np

def compute_incident_magnetic_field(centers, feed_position, wavelength):

    # feed to triangle
    R_vec = centers - feed_position
    R_abs = np.linalg.norm(R_vec, axis=1)
    R_hat = R_vec / R_abs[:, None]

    # get magnetic-field direction using chosen polarization axis
    p = np.array([0.0, 1.0, 0.0])
    h_raw = p[None, :] - np.sum(p[None, :] * R_hat, axis=1)[:, None] * R_hat
    h_norm = np.linalg.norm(h_raw, axis=1)
    h_hat = h_raw / h_norm[:, None]

    # reference amplitude * phase and spreading * direction
    k = 2.0 * np.pi / wavelength
    H0 = 1.0
    phase_and_spreading = H0 * np.exp(-1j * k * R_abs) / R_abs
    H_inc = phase_and_spreading[:, None] * h_hat

    return H_inc, R_hat, R_abs, h_hat

def compute_surface_current(normals, H_inc):

    return 2.0 * np.cross(normals, H_inc)


def compute_far_field_pattern(centers, areas, J_s, wavelength, r_hat,):

    k = 2.0 * np.pi / wavelength

    # phased integration of surface current
    phase = np.exp(1j * k * (r_hat @ centers.T))
    source = J_s * areas[:, None]
    F = phase @ source

    # far E-field is proportional to transverse projection of current
    F_dot_r = np.sum(F * r_hat, axis=1)
    E_pattern = F - F_dot_r[:, None] * r_hat

    # power pattern proportional to |E|^2
    power = np.sum(np.abs(E_pattern) ** 2, axis=1)

    # normalize to max = 0 dB
    eps = 1e-30
    power_norm = power / np.max(power)
    power_db = 10.0 * np.log10(power_norm + eps)

    return F, E_pattern, power, power_db


def observation_directions_theta_cut(theta_deg: np.ndarray):

    theta = np.deg2rad(theta_deg)
    r_hat = np.column_stack([
        np.sin(theta),
        np.zeros_like(theta),
        np.cos(theta),
    ])

    return r_hat