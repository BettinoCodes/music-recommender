"""
Command line runner for the Music Recommender Simulation.

Run from the project root:
    python -m src.main
"""

from src.recommender import load_songs, recommend_songs

_W = 100  # total output width


def _divider(char: str = "-") -> None:
    print(char * _W)


def run_profile(label: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    """Print a labelled recommendation block for one user profile."""
    _divider("=")
    print(f"PROFILE: {label}")
    _divider()
    for key, val in user_prefs.items():
        print(f"  {key:<16} {val}")
    _divider()

    results = recommend_songs(user_prefs, songs, k=k)
    print(f"{'#':<3} {'Title':<26} {'Artist':<22} {'Score':>5}  Reasons")
    _divider()
    for rank, (song, score, explanation) in enumerate(results, start=1):
        print(f"{rank:<3} {song['title']:<26} {song['artist']:<22} {score:>5.2f}  {explanation}")
    _divider("=")
    print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"\nLoaded {len(songs)} songs from catalog.\n")

    # -----------------------------------------------------------------------
    # Standard profiles
    # -----------------------------------------------------------------------
    run_profile(
        "1 — High-Energy Pop",
        {"genre": "pop", "mood": "happy", "energy": 0.8},
        songs,
    )

    run_profile(
        "2 — Chill Lofi (acoustic preferred)",
        {"genre": "lofi", "mood": "chill", "energy": 0.38, "likes_acoustic": True},
        songs,
    )

    run_profile(
        "3 — Deep Intense Rock",
        {"genre": "rock", "mood": "intense", "energy": 0.90},
        songs,
    )

    # -----------------------------------------------------------------------
    # Adversarial / edge-case profiles
    # -----------------------------------------------------------------------
    run_profile(
        "4 — ADVERSARIAL: High-Energy Sad (conflicting preferences)",
        {"genre": "r&b", "mood": "sad", "energy": 0.90},
        songs,
    )

    run_profile(
        "5 — ADVERSARIAL: Genre not in catalog (bossa nova / chill)",
        {"genre": "bossa nova", "mood": "chill", "energy": 0.40},
        songs,
    )

    run_profile(
        "6 — ADVERSARIAL: Perfect-middle everything (energy 0.5, jazz/relaxed)",
        {"genre": "jazz", "mood": "relaxed", "energy": 0.50},
        songs,
    )


if __name__ == "__main__":
    main()
