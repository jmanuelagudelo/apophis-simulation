from datetime import datetime, timedelta
import numpy as np
from .constants import DAYS_PER_JULIAN_YEAR

def years_between(start: datetime, end: datetime) -> float:
    """Return elapsed Julian years between two dates."""
    if end <= start:
        raise ValueError("end must be after start")
    return (end - start).total_seconds() / (DAYS_PER_JULIAN_YEAR * 86400)

def date_at_year_offset(start: datetime, years: float) -> datetime:
    """Convert a REBOUND time in Julian years to a UTC datetime."""
    return start + timedelta(days=years * DAYS_PER_JULIAN_YEAR)

def as_xyz(values: object) -> np.ndarray:
    """Return a validated position array with shape ``(n, 3)``."""
    array = np.asarray(values, dtype=float)
    if array.ndim != 2 or array.shape[1] != 3:
        raise ValueError("positions must have shape (n_samples, 3)")
    return array
