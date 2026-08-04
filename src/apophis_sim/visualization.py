"""Solver-independent interactive Plotly visualizations."""

from collections.abc import Mapping, Sequence

import numpy as np
import plotly.graph_objects as go

from .bodies import BODY_STYLES
from .utils import as_xyz


def trajectory_figure(
    trajectories: Mapping[str, np.ndarray],
    *,
    center: str = "sun",
    bodies: Sequence[str] | None = None,
    trails: bool = True,
    equal_axes: bool = True,
    theme: str = "dark",
    zoom: str | None = None,
    show_moon: bool = False,
    closest_index: int | None = None,
) -> go.Figure:
    """Build an interactive 3D trajectory figure in a physical reference frame.

    Parameters
    ----------
    trajectories
        Barycentric or heliocentric AU positions, each shaped
        ``(n_samples, 3)``. All arrays must use the same sample times.
    center
        Reference body. ``"sun"`` and ``"earth"`` are supported.
    bodies
        Bodies to display. Explicitly listing ``"moon"`` always displays the
        Moon. If omitted, ``show_moon`` controls whether it is added.
    zoom
        ``"close"`` uses a +/- 0.03 AU Earth-centered encounter view. The Sun
        is intentionally omitted in this view because it is about 1 AU away.

    Notes
    -----
    Coordinates are translated by the *sampled position of the requested
    centre*, rather than assuming that the central body is at the origin. This
    makes the function correct for barycentric REBOUND output as well as for
    externally supplied heliocentric trajectories.
    """
    center_key = center.lower()
    if center_key not in {"sun", "earth"}:
        raise ValueError("center must be 'sun' or 'earth'")
    if zoom not in {None, "close"}:
        raise ValueError("zoom must be None or 'close'")

    available = {name.lower(): as_xyz(values) for name, values in trajectories.items()}
    if center_key not in available:
        raise ValueError(f"{center.title()}-centered plots require a '{center_key}' trajectory")
    sample_count = len(available[center_key])
    if any(len(values) != sample_count for values in available.values()):
        raise ValueError("all trajectories must contain the same number of samples")

    selected = _selected_bodies(bodies, show_moon)
    if center_key == "earth" and zoom == "close":
        # A physical Sun would be outside the close-encounter scale. Omitting it
        # is preferable to drawing an unphysical Sun at Earth's location.
        selected = [name for name in selected if name != "sun"]

    origin = available[center_key]
    figure = go.Figure()
    for key in selected:
        if key not in available or key not in BODY_STYLES:
            continue
        style = BODY_STYLES[key]
        points = available[key] - origin
        is_central_body = key == center_key
        if trails and not is_central_body:
            figure.add_trace(
                go.Scatter3d(
                    x=points[:, 0],
                    y=points[:, 1],
                    z=points[:, 2],
                    mode="lines",
                    name=style.label,
                    legendgroup=key,
                    line={"color": style.color, "width": 3},
                )
            )
        figure.add_trace(
            go.Scatter3d(
                x=[points[-1, 0]],
                y=[points[-1, 1]],
                z=[points[-1, 2]],
                mode="markers",
                name=f"{style.label} position" if not is_central_body else style.label,
                legendgroup=key,
                showlegend=not trails or is_central_body,
                marker={"color": style.color, "size": style.size},
            )
        )

    if closest_index is not None and "apophis" in available:
        if not 0 <= closest_index < sample_count:
            raise IndexError("closest_index is outside the trajectory range")
        point = available["apophis"][closest_index] - origin[closest_index]
        figure.add_trace(
            go.Scatter3d(
                x=[point[0]],
                y=[point[1]],
                z=[point[2]],
                mode="markers",
                name="Closest approach",
                marker={"color": "#FFFFFF", "size": 5, "symbol": "diamond"},
            )
        )

    figure.update_layout(
        template="plotly_dark" if theme == "dark" else "plotly_white",
        title=f"Apophis trajectories ({center_key}-centered)",
        scene={
            **_scene_axes(zoom),
            "aspectmode": "data" if equal_axes else "auto",
            "camera": {"eye": {"x": 1.5, "y": 1.5, "z": 0.8}},
        },
        legend={"orientation": "h", "y": 1.02},
        margin={"l": 0, "r": 0, "b": 0, "t": 45},
    )
    return figure


def _selected_bodies(bodies: Sequence[str] | None, show_moon: bool) -> list[str]:
    """Resolve default and explicitly requested body names."""
    if bodies is None:
        selected = ["sun", "earth", "apophis"]
    else:
        selected = [body.lower() for body in bodies]
    if show_moon and "moon" not in selected:
        selected.append("moon")
    return list(dict.fromkeys(selected))


def _scene_axes(zoom: str | None) -> dict[str, dict[str, object]]:
    """Return consistently labelled 3D Plotly axes."""
    if zoom == "close":
        return {
            f"{axis}axis": {"range": [-0.03, 0.03], "title": f"{axis.upper()} (AU)"}
            for axis in "xyz"
        }
    return {f"{axis}axis": {"title": f"{axis.upper()} (AU)"} for axis in "xyz"}
