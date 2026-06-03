import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


def draw_dish_mesh_on_axis(
    ax,
    vertices,
    faces,
    title=None,
    elev=47,
    azim=-13,
    roll=-23,
    edge_linewidth=0.25,
    alpha=0.45,
):
    triangles = vertices[faces]

    mesh = Poly3DCollection(
        triangles,
        alpha=alpha,
        edgecolor="k",
        linewidth=edge_linewidth,
    )
    ax.add_collection3d(mesh)

    x = vertices[:, 0]
    y = vertices[:, 1]
    z = vertices[:, 2]

    x_min, x_max = x.min(), x.max()
    y_min, y_max = y.min(), y.max()
    z_min, z_max = z.min(), z.max()

    x_mid = 0.5 * (x_min + x_max)
    y_mid = 0.5 * (y_min + y_max)
    z_mid = 0.5 * (z_min + z_max)

    max_range = max(
        x_max - x_min,
        y_max - y_min,
        z_max - z_min,
    )

    zoom = 0.72
    half_range = 0.5 * max_range * zoom

    ax.set_xlim(x_mid - half_range, x_mid + half_range)
    ax.set_ylim(y_mid - half_range, y_mid + half_range)
    ax.set_zlim(z_mid - half_range, z_mid + half_range)

    ax.set_box_aspect((1, 1, 0.25))

    ax.view_init(elev=elev, azim=azim, roll=roll)
    ax.set_axis_off()
    ax.grid(False)

    if title is not None:
        ax.set_title(title)


def make_metrics_text(mesh_metrics):
    return (
        f"num. triangles:\n"
        f"{mesh_metrics['num_triangles']}\n\n"
        f"normal error mean (deg):\n"
        f"{mesh_metrics['normal_error_mean_deg']:.4f}\n\n"
        f"normal error max (deg):\n"
        f"{mesh_metrics['normal_error_max_deg']:.4f}\n"
    )


def plot_summary_column(
    ax_mesh,
    ax_text,
    ax_field,
    result: dict,
    case_name: str,
    db_floor: float = -80.0,
):
    vertices = result["mesh"]["vertices"]
    faces = result["mesh"]["faces"]

    theta_deg = result["far_field"]["theta_deg"]
    power_db = result["far_field"]["power_db"]

    mesh_metrics = result["mesh_metrics"]

    # Row 1: 3D mesh plot
    draw_dish_mesh_on_axis(
        ax_mesh,
        vertices=vertices,
        faces=faces,
        title=case_name,
        elev=47,
        azim=-13,
        roll=-23,
        edge_linewidth=0.25,
        alpha=0.45,
    )

    # Row 2: metrics text
    ax_text.axis("off")

    metrics_text = make_metrics_text(mesh_metrics)

    ax_text.text(
        0.05,
        1.2,
        metrics_text,
        transform=ax_text.transAxes,
        va="top",
        ha="left",
        fontsize=11,
        family="monospace",
    )

    # Row 3: far-field pattern
    ax_field.plot(theta_deg, power_db)
    ax_field.set_ylim(db_floor, 0)
    ax_field.grid(True)
    ax_field.set_xlabel("Theta, degrees")
    ax_field.set_title("Far-field")
    ax_field.set_box_aspect(0.75)


def plot_mesh_farfield_summary(
    results: dict,
    case_names=("coarse", "medium", "fine"),
    db_floor: float = -80.0,
    title: str = "Polar Mesh Refinement",
):
    n_cols = len(case_names)

    fig = plt.figure(figsize=(5 * n_cols, 9.0))

    gs = GridSpec(
        3,
        n_cols,
        figure=fig,
        height_ratios=[1.25, 0.55, 1.10],
        hspace=0.15,
        wspace=0.25,
    )

    for col, case_name in enumerate(case_names):
        ax_mesh = fig.add_subplot(gs[0, col], projection="3d")
        ax_text = fig.add_subplot(gs[1, col])
        ax_field = fig.add_subplot(gs[2, col])

        plot_summary_column(
            ax_mesh=ax_mesh,
            ax_text=ax_text,
            ax_field=ax_field,
            result=results[case_name],
            case_name=case_name,
            db_floor=db_floor,
        )

        if col == 0:
            ax_field.set_ylabel("Normalized power, dB")

    fig.suptitle(title, fontsize=16)
    plt.subplots_adjust(top=0.90, bottom=0.04)
    plt.savefig("figures/polar_refinement.png", dpi=300, bbox_inches="tight")
    plt.show()


def plot_medium_vs_variable_summary(
    results: dict,
    case_names=("medium", "variable_quality"),
    db_floor: float = -80.0,
    title: str = "Polar Mesh vs Rim-Refined Delauney",
):
    n_cols = len(case_names)

    fig = plt.figure(figsize=(5 * n_cols, 9.0))

    gs = GridSpec(
        3,
        n_cols,
        figure=fig,
        height_ratios=[1.25, 0.55, 1.10],
        hspace=0.15,
        wspace=0.25,
    )

    for col, case_name in enumerate(case_names):
        ax_mesh = fig.add_subplot(gs[0, col], projection="3d")
        ax_text = fig.add_subplot(gs[1, col])
        ax_field = fig.add_subplot(gs[2, col])

        plot_summary_column(
            ax_mesh=ax_mesh,
            ax_text=ax_text,
            ax_field=ax_field,
            result=results[case_name],
            case_name=case_name,
            db_floor=db_floor,
        )

        if col == 0:
            ax_field.set_ylabel("Normalized power, dB")

    fig.suptitle(title, fontsize=16)
    plt.subplots_adjust(top=0.90, bottom=0.04)
    plt.savefig("figures/variable_delauney.png", dpi=300, bbox_inches="tight")
    plt.show()


def plot_reference_summary(
    result: dict,
    case_name: str = "reference",
    db_floor: float = -80.0,
    title: str = "Reference mesh summary",
):
    fig = plt.figure(figsize=(14, 4.2))

    gs = GridSpec(
        1,
        3,
        figure=fig,
        width_ratios=[1.0, 0.8, 1.15],
        wspace=0.25,
    )

    ax_mesh = fig.add_subplot(gs[0, 0], projection="3d")
    ax_text = fig.add_subplot(gs[0, 1])
    ax_field = fig.add_subplot(gs[0, 2])

    vertices = result["mesh"]["vertices"]
    faces = result["mesh"]["faces"]

    theta_deg = result["far_field"]["theta_deg"]
    power_db = result["far_field"]["power_db"]

    mesh_metrics = result["mesh_metrics"]

    draw_dish_mesh_on_axis(
        ax_mesh,
        vertices=vertices,
        faces=faces,
        title=case_name,
        elev=47,
        azim=-13,
        roll=-23,
        edge_linewidth=0.15,
        alpha=0.45,
    )

    ax_text.axis("off")

    metrics_text = make_metrics_text(mesh_metrics)

    ax_text.text(
        0.05,
        0.85,
        metrics_text,
        transform=ax_text.transAxes,
        va="top",
        ha="left",
        fontsize=11,
        family="monospace",
    )

    ax_field.plot(theta_deg, power_db)
    ax_field.set_ylim(db_floor, 0)
    ax_field.grid(True)
    ax_field.set_xlabel("Theta, degrees")
    ax_field.set_ylabel("Normalized power, dB")
    ax_field.set_title("Far-field")
    ax_field.set_box_aspect(0.75)

    fig.suptitle(title, fontsize=16)
    plt.subplots_adjust(top=0.82, bottom=0.08)
    plt.savefig("figures/reference.png", dpi=300, bbox_inches="tight")
    plt.show()


def plot_dish_mesh_3d(
    result: dict,
    case_name: str = "mesh",
    title: str | None = None,
):
    fig = plt.figure(figsize=(8, 7))
    ax = fig.add_subplot(111, projection="3d")

    draw_dish_mesh_on_axis(
        ax,
        vertices=result["mesh"]["vertices"],
        faces=result["mesh"]["faces"],
        title=title or case_name,
        elev=47,
        azim=-13,
        roll=-23,
        edge_linewidth=0.25,
        alpha=0.45,
    )

    plt.tight_layout(pad=0)
    plt.show()