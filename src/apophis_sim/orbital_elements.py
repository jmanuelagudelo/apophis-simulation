"""Orbital-element calculations and coordinate transformations."""
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class OrbitalElements:
    """Classical osculating orbital elements (angles in degrees)."""
    semi_major_axis_au: float
    eccentricity: float
    inclination_deg: float
    longitude_ascending_node_deg: float
    argument_periapsis_deg: float
    true_anomaly_deg: float
    mean_anomaly_deg: float

@dataclass(frozen=True)
class EquatorialCoordinates:
    """Equatorial sky coordinates in degrees."""
    right_ascension_deg: float
    declination_deg: float

def ecliptic_to_equatorial(position_au: np.ndarray, obliquity_deg: float = 23.4392911) -> EquatorialCoordinates:
    """Convert an ecliptic Cartesian vector to right ascension and declination."""
    vector = np.asarray(position_au, dtype=float)
    if vector.shape != (3,) or np.allclose(vector, 0):
        raise ValueError("position_au must be a non-zero three-vector")
    eps = np.deg2rad(obliquity_deg)
    rotated = np.array([vector[0], np.cos(eps)*vector[1]-np.sin(eps)*vector[2], np.sin(eps)*vector[1]+np.cos(eps)*vector[2]])
    radius = np.linalg.norm(rotated)
    return EquatorialCoordinates(float(np.degrees(np.arctan2(rotated[1], rotated[0])) % 360), float(np.degrees(np.arcsin(rotated[2] / radius))))

def from_rebound_orbit(orbit: object) -> OrbitalElements:
    """Create :class:`OrbitalElements` from a REBOUND orbit object."""
    deg = np.degrees
    return OrbitalElements(orbit.a, orbit.e, float(deg(orbit.inc)), float(deg(orbit.Omega) % 360), float(deg(orbit.omega) % 360), float(deg(orbit.f) % 360), float(deg(orbit.M) % 360))
