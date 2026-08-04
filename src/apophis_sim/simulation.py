"""REBOUND-backed N-body simulation of asteroid (99942) Apophis."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import numpy as np
from .constants import DEFAULT_BODIES, HORIZONS_IDS
from .orbital_elements import OrbitalElements, from_rebound_orbit
from .utils import date_at_year_offset, years_between
from .visualization import trajectory_figure

@dataclass(frozen=True)
class ClosestApproach:
    """Minimum Earth-Apophis separation found in sampled integration output."""
    date: datetime
    distance_au: float
    index: int

@dataclass
class SimulationResult:
    """In-memory barycentric trajectory output in AU coordinates."""
    times_years: np.ndarray
    trajectories: dict[str, np.ndarray]
    earth_apophis_distance_au: np.ndarray

@dataclass
class ApophisSimulation:
    """Configure and run an IAS15 N-body integration for Apophis.

    REBOUND's Horizons particle lookup is used at runtime; install with
    ``pip install apophis-sim[rebound]``. Times are UTC datetimes and positions
    are returned in astronomical units.
    """
    start_date: datetime = field(default_factory=lambda: datetime(2029, 1, 1))
    end_date: datetime = field(default_factory=lambda: datetime(2029, 6, 1))
    steps: int = 20_000
    bodies: tuple[str, ...] = DEFAULT_BODIES
    asteroid_id: str = "99942"
    integrator: str = "ias15"
    result: SimulationResult | None = field(init=False, default=None)
    _simulation: Any = field(init=False, default=None, repr=False)
    _initial_simulation: Any = field(init=False, default=None, repr=False)

    def run(self) -> "ApophisSimulation":
        """Integrate the configured system and store sampled trajectories."""
        if self.steps < 2:
            raise ValueError("steps must be at least 2")
        try:
            import rebound
        except ImportError as exc:
            raise ImportError("REBOUND is required to run an N-body simulation; install apophis-sim[rebound].") from exc
        body_keys = [body.lower() for body in self.bodies]
        if len(set(body_keys)) != len(body_keys):
            raise ValueError("bodies cannot contain duplicate names")
        missing = {"sun", "earth"} - set(body_keys)
        if missing:
            raise ValueError(f"bodies must include: {', '.join(sorted(missing))}")

        sim = rebound.Simulation()
        sim.units = ("AU", "yr", "Msun")
        sim.integrator = self.integrator
        for body in self.bodies:
            sim.add(HORIZONS_IDS.get(body, body), date=self.start_date)
        sim.add(self.asteroid_id, date=self.start_date); sim.move_to_com()
        self._initial_simulation = sim.copy()
        names = {"sun": body_keys.index("sun"), "earth": body_keys.index("earth"), "apophis": sim.N - 1}
        if "moon" in body_keys:
            names["moon"] = body_keys.index("moon")
        times = np.linspace(0, years_between(self.start_date, self.end_date), self.steps)
        paths = {name: np.empty((self.steps, 3)) for name in names}
        for index, time in enumerate(times):
            sim.integrate(time)
            for name, particle_index in names.items():
                p = sim.particles[particle_index]; paths[name][index] = (p.x, p.y, p.z)
        distances = np.linalg.norm(paths["apophis"] - paths["earth"], axis=1)
        if not np.isfinite(distances).all():
            raise RuntimeError(
                "Integration produced non-finite positions. Check the initial "
                "conditions and selected bodies."
            )
        self._simulation, self.result = sim, SimulationResult(times, paths, distances)
        return self

    def closest_approach(self) -> ClosestApproach:
        """Return the closest sampled Earth-Apophis approach."""
        result = self._require_result(); index = int(np.argmin(result.earth_apophis_distance_au))
        return ClosestApproach(date_at_year_offset(self.start_date, float(result.times_years[index])), float(result.earth_apophis_distance_au[index]), index)

    def compute_orbital_elements(self) -> tuple[OrbitalElements, OrbitalElements]:
        """Return osculating Apophis elements at integration start and end."""
        sim = self._initial_simulation.copy(); asteroid = sim.N - 1
        initial = from_rebound_orbit(sim.particles[asteroid].orbit())
        sim.integrate(years_between(self.start_date, self.end_date)); final = from_rebound_orbit(sim.particles[asteroid].orbit())
        return initial, final

    def compare_methods(self) -> dict[str, object]:
        """Return an extensible summary of numerical-method results.

        Two-body and patched-conics inputs are intentionally explicit: they use
        user-supplied ephemerides rather than silently mixing reference frames.
        """
        return {"n_body": self.closest_approach()}

    def plot(self, **kwargs: object):
        """Return a publication-ready interactive Plotly trajectory figure."""
        result = self._require_result(); return trajectory_figure(result.trajectories, closest_index=self.closest_approach().index, **kwargs)

    def animate(self, **kwargs: object):
        """Return a Plotly figure with animation frames over integration time."""
        figure = self.plot(**kwargs); result = self._require_result(); frames = []
        for index in range(0, len(result.times_years), max(1, len(result.times_years)//100)):
            frames.append({"name": str(index), "data": [{"x": path[:index+1, 0], "y": path[:index+1, 1], "z": path[:index+1, 2]} for path in result.trajectories.values()]})
        figure.frames = frames; figure.update_layout(updatemenus=[{"type": "buttons", "buttons": [{"label": "Play", "method": "animate", "args": [None, {"frame": {"duration": 50}, "fromcurrent": True}]}]}]); return figure

    def _require_result(self) -> SimulationResult:
        if self.result is None: raise RuntimeError("Run the simulation first with sim.run().")
        return self.result
    def _require_simulation(self) -> Any:
        self._require_result()
        return self._simulation
