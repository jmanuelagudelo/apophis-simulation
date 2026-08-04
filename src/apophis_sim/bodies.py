from dataclasses import dataclass

@dataclass(frozen=True)
class BodyStyle:
    """Display properties for a named Solar-System body."""
    color: str
    size: float
    label: str

BODY_STYLES = {
    "sun": BodyStyle("#FDB813", 10, "Sun"),
    "earth": BodyStyle("#4C9AFF", 7, "Earth"),
    "moon": BodyStyle("#D7D7D7", 4, "Moon"),
    "apophis": BodyStyle("#EF553B", 5, "(99942) Apophis"),
}
