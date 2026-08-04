"""Two-body and patched-conics approximations for close encounters."""
from dataclasses import dataclass
import numpy as np
from .constants import EARTH_MU_AU3_DAY2

@dataclass(frozen=True)
class HyperbolicEncounter:
    """Earth-relative hyperbolic trajectory derived from a state vector."""
    semi_major_axis_au: float
    eccentricity: float
    periapsis_au: float

def solve_kepler(mean_anomaly_rad: np.ndarray, eccentricity: float, tolerance: float = 1e-12, max_iterations: int = 100) -> np.ndarray:
    """Solve elliptic Kepler's equation with Newton iteration."""
    if not 0 <= eccentricity < 1:
        raise ValueError("eccentricity must be in [0, 1) for an elliptic orbit")
    anomaly = np.asarray(mean_anomaly_rad, dtype=float)
    eccentric = anomaly.copy()
    for _ in range(max_iterations):
        delta = (eccentric - eccentricity*np.sin(eccentric) - anomaly) / (1 - eccentricity*np.cos(eccentric))
        eccentric -= delta
        if np.max(np.abs(delta)) < tolerance:
            return eccentric
    raise RuntimeError("Kepler solver did not converge")

def rotate_orbit(positions_au: np.ndarray, longitude_node_deg: float, inclination_deg: float, argument_periapsis_deg: float) -> np.ndarray:
    """Rotate perifocal positions into the ecliptic frame."""
    om, inc, arg = np.deg2rad([longitude_node_deg, inclination_deg, argument_periapsis_deg])
    rz1 = np.array([[np.cos(om), -np.sin(om), 0], [np.sin(om), np.cos(om), 0], [0, 0, 1]])
    rx = np.array([[1, 0, 0], [0, np.cos(inc), -np.sin(inc)], [0, np.sin(inc), np.cos(inc)]])
    rz2 = np.array([[np.cos(arg), -np.sin(arg), 0], [np.sin(arg), np.cos(arg), 0], [0, 0, 1]])
    return (rz1 @ rx @ rz2 @ np.asarray(positions_au).T).T

def hyperbolic_encounter(relative_position_au: np.ndarray, relative_velocity_au_day: np.ndarray, mu_au3_day2: float = EARTH_MU_AU3_DAY2) -> HyperbolicEncounter:
    """Compute a patched-conics Earth encounter from an incoming relative state."""
    r_vec, v_vec = np.asarray(relative_position_au, dtype=float), np.asarray(relative_velocity_au_day, dtype=float)
    r, v = np.linalg.norm(r_vec), np.linalg.norm(v_vec)
    if r == 0 or mu_au3_day2 <= 0:
        raise ValueError("state position and gravitational parameter must be non-zero")
    h_vec = np.cross(r_vec, v_vec)
    e_vec = np.cross(v_vec, h_vec) / mu_au3_day2 - r_vec / r
    eccentricity = float(np.linalg.norm(e_vec))
    semi_major_axis = float(1 / (2/r - v**2/mu_au3_day2))
    if eccentricity <= 1:
        raise ValueError("state is not hyperbolic")
    return HyperbolicEncounter(semi_major_axis, eccentricity, abs(semi_major_axis) * (eccentricity - 1))
