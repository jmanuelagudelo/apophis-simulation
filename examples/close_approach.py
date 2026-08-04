from datetime import datetime
from apophis_sim import ApophisSimulation


def ask_yes_no(prompt: str, *, default: bool) -> bool:
    suffix = "Y/n" if default else "y/N"
    while True:
        answer = input(f"{prompt} [{suffix}]: ").strip().lower()
        if not answer:
            return default
        if answer in {"y", "yes", "s", "si"}:
            return True
        if answer in {"n", "no"}:
            return False
        print("Please answer y or n.")


def ask_center() -> str:
    while True:
        answer = input("Reference center: Earth or Sun [earth]: ").strip().lower()
        if not answer:
            return "earth"
        if answer in {"earth", "tierra"}:
            return "earth"
        if answer in {"sun", "sol"}:
            return "sun"
        print("Please enter earth or sun.")


def choose_plot_options() -> tuple[str, list[str], str | None]:
    center = ask_center()
    close_zoom = center == "earth" and ask_yes_no(
        "Use the close-encounter zoom", default=True
    )
    default_sun = center == "sun" or not close_zoom
    choices = {
        "sun": ask_yes_no("Graph the Sun", default=default_sun),
        "earth": ask_yes_no("Graph Earth", default=True),
        "moon": ask_yes_no("Graph the Moon", default=False),
        "apophis": ask_yes_no("Graph Apophis", default=True),
    }
    bodies = [body for body, selected in choices.items() if selected]
    if not bodies:
        raise ValueError("Select at least one body to create a figure.")
    if close_zoom and choices["sun"]:
        print("The Sun is about 1 AU from Earth; disabling close zoom to show it.")
        close_zoom = False
    return center, bodies, "close" if close_zoom else None


def main() -> None:
    center, bodies, zoom = choose_plot_options()
    sim = ApophisSimulation(
        start_date=datetime(2029, 1, 1),
        end_date=datetime(2029, 6, 1),
        steps=20_000,
    ).run()
    approach = sim.closest_approach()
    print(
        f"Closest approach: {approach.date:%Y-%m-%d %H:%M UTC}; "
        f"{approach.distance_au:.7f} AU"
    )
    sim.plot(
        center=center,
        bodies=bodies,
        show_moon="moon" in bodies,
        zoom=zoom,
        trails=True,
        equal_axes=True,
        theme="dark",
    ).show()


if __name__ == "__main__":
    main()
