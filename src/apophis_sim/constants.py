AU_KM = 149_597_870.7
SECONDS_PER_DAY = 86_400.0
DAYS_PER_JULIAN_YEAR = 365.25
EARTH_MU_KM3_S2 = 398_600.435436
EARTH_MU_AU3_DAY2 = EARTH_MU_KM3_S2 * SECONDS_PER_DAY**2 / AU_KM**3
EARTH_SOI_AU = 0.006
DEFAULT_BODIES = ("Sun", "Mercury", "Venus", "Earth", "Moon", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune")

# Numeric Horizons identifiers avoid ambiguous name resolution.  In particular,
# the query "Earth" may resolve to the Earth-Moon barycenter, while the model
# needs distinct Earth (399) and Moon (301) particles.
HORIZONS_IDS = {
    "Sun": "10",
    "Mercury": "199",
    "Venus": "299",
    "Earth": "399",
    "Moon": "301",
    "Mars": "499",
    "Jupiter": "599",
    "Saturn": "699",
    "Uranus": "799",
    "Neptune": "899",
}
