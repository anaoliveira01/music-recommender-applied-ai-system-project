import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
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
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Load song data from the specified CSV file."""
    print(f"Loading songs from {csv_path}...")
    songs: List[Dict] = []
    numeric_fields = {
        "id": int,
        "energy": float,
        "tempo_bpm": float,
        "valence": float,
        "danceability": float,
        "acousticness": float,
        "liveness": float,
        "speechiness": float,
        "instrumentalness": float,
    }

    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            parsed_row: Dict = {}
            for key, value in row.items():
                if value is None:
                    parsed_row[key] = value
                    continue
                value = value.strip()
                if key in numeric_fields and value != "":
                    parsed_row[key] = numeric_fields[key](value)
                else:
                    parsed_row[key] = value
            songs.append(parsed_row)

    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score a single song against user preferences, returning its score and reasons."""
    score = 0.0
    reasons: List[str] = []

    if user_prefs.get("genre") and song.get("genre"):
        if user_prefs["genre"].strip().lower() == song["genre"].strip().lower():
            score += 5.0
            reasons.append("genre match (+5.0)")

    if user_prefs.get("mood") and song.get("mood"):
        if user_prefs["mood"].strip().lower() == song["mood"].strip().lower():
            score += 4.0
            reasons.append("mood match (+4.0)")

    numeric_keys = {
        "energy": "energy",
        "tempo": "tempo_bpm",
        "tempo_bpm": "tempo_bpm",
        "valence": "valence",
        "danceability": "danceability",
        "acousticness": "acousticness",
        "liveness": "liveness",
        "speechiness": "speechiness",
        "instrumentalness": "instrumentalness",
    }

    for pref_key, song_key in numeric_keys.items():
        if pref_key in user_prefs and song_key in song:
            try:
                user_value = float(user_prefs[pref_key])
                song_value = float(song[song_key])
            except (TypeError, ValueError):
                continue

            diff = abs(user_value - song_value)
            similarity = max(0.0, 1.0 - diff)
            if similarity > 0:
                score += similarity
                reasons.append(f"{song_key} similarity (+{similarity:.2f})")

    if not reasons:
        reasons.append("no strong match")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Rank songs by score and return the top k recommendations."""
    scored_songs: List[Tuple[Dict, float, str]] = []

    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = "; ".join(reasons)
        scored_songs.append((song, score, explanation))

    scored_songs.sort(key=lambda item: item[1], reverse=True)
    return scored_songs[:k]
