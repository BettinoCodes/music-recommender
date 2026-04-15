import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Song:
    """Represents a song and its measurable audio attributes."""

    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """Represents a user's music taste preferences used to score songs."""

    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


class Recommender:
    """Content-based recommender that ranks Song objects against a UserProfile."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> float:
        """Compute a numeric compatibility score between a UserProfile and a Song."""
        score = 0.0
        if song.genre == user.favorite_genre:
            score += 2.0
        if song.mood == user.favorite_mood:
            score += 1.0
        score += 1.0 - abs(song.energy - user.target_energy)
        if user.likes_acoustic and song.acousticness > 0.7:
            score += 0.5
        return score

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k Song objects ranked by compatibility score for the given user."""
        return sorted(self.songs, key=lambda s: self._score(user, s), reverse=True)[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable explanation of why a Song was recommended to a user."""
        reasons = []
        if song.genre == user.favorite_genre:
            reasons.append(f"genre match '{song.genre}' (+2.0)")
        if song.mood == user.favorite_mood:
            reasons.append(f"mood match '{song.mood}' (+1.0)")
        proximity = 1.0 - abs(song.energy - user.target_energy)
        reasons.append(f"energy proximity {proximity:.2f} (+{proximity:.2f})")
        if user.likes_acoustic and song.acousticness > 0.7:
            reasons.append(f"acoustic bonus (acousticness={song.acousticness:.2f}, +0.5)")
        return "; ".join(reasons)


# ---------------------------------------------------------------------------
# Functional API  (used by src/main.py)
# ---------------------------------------------------------------------------

def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv and return a list of dicts with numeric fields cast to float/int."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":           int(row["id"]),
                "title":        row["title"],
                "artist":       row["artist"],
                "genre":        row["genre"],
                "mood":         row["mood"],
                "energy":       float(row["energy"]),
                "tempo_bpm":    float(row["tempo_bpm"]),
                "valence":      float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song dict against user_prefs; return (total_score, list_of_reasons).

    Algorithm recipe
    ----------------
    +2.0   exact genre match          — broadest taste boundary
    +1.0   exact mood match           — emotional context
    +0–1.0 energy proximity           — 1.0 - |song.energy - user.energy|
    +0.5   acoustic bonus             — only when user prefers acoustic
                                        and song.acousticness > 0.7
    Max possible score: 4.5
    """
    score = 0.0
    reasons = []

    # --- categorical signals ---
    if song["genre"] == user_prefs.get("genre", ""):
        score += 2.0
        reasons.append(f"genre match '{song['genre']}' (+2.0)")

    if song["mood"] == user_prefs.get("mood", ""):
        score += 1.0
        reasons.append(f"mood match '{song['mood']}' (+1.0)")

    # --- numerical proximity (rewards closeness, not just high/low) ---
    target_energy = user_prefs.get("energy", 0.5)
    proximity = 1.0 - abs(song["energy"] - target_energy)
    score += proximity
    reasons.append(f"energy proximity {proximity:.2f} (+{proximity:.2f})")

    # --- optional acoustic style preference ---
    if user_prefs.get("likes_acoustic", False) and song["acousticness"] > 0.7:
        score += 0.5
        reasons.append(f"acoustic bonus (acousticness={song['acousticness']:.2f}, +0.5)")

    return score, reasons


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
) -> List[Tuple[Dict, float, str]]:
    """Score every song, sort by score descending, and return the top-k with explanations.

    Uses sorted() (returns a new list) rather than list.sort() (mutates in place)
    so the original catalog order is preserved for subsequent calls.

    Returns a list of (song_dict, score, explanation_string) tuples.
    """
    scored = []
    for song in songs:
        song_score, reasons = score_song(user_prefs, song)
        scored.append((song, song_score, "; ".join(reasons)))

    # sorted() never mutates `scored`; it returns a brand-new sorted list.
    ranked = sorted(scored, key=lambda item: item[1], reverse=True)
    return ranked[:k]
