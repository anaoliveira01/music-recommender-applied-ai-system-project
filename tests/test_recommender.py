import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.recommender import Song, UserProfile, Recommender
from src.recommender import recommend_songs

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


# --- RAG layer tests ---

def test_recommend_songs_returns_required_keys():
    """Recommender output always has keys the UI expects."""
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    songs = [
        {"id": 1, "title": "Test", "artist": "A", "genre": "pop",
         "mood": "happy", "energy": 0.8, "tempo_bpm": 120.0,
         "valence": 0.9, "danceability": 0.8, "acousticness": 0.2},
    ]
    results = recommend_songs(prefs, songs, k=1)
    assert len(results) == 1
    song, score, reasons = results[0]
    assert isinstance(score, float)
    assert isinstance(reasons, str)


def test_recommend_songs_consistent():
    """Same input always produces the same top result."""
    prefs = {"genre": "lofi", "mood": "chill", "energy": 0.4}
    songs = [
        {"id": 1, "title": "Chill A", "artist": "X", "genre": "lofi",
         "mood": "chill", "energy": 0.4, "tempo_bpm": 80.0,
         "valence": 0.6, "danceability": 0.5, "acousticness": 0.8},
        {"id": 2, "title": "Pop B", "artist": "Y", "genre": "pop",
         "mood": "happy", "energy": 0.9, "tempo_bpm": 120.0,
         "valence": 0.9, "danceability": 0.8, "acousticness": 0.2},
    ]
    first = recommend_songs(prefs, songs, k=1)[0][0]["title"]
    second = recommend_songs(prefs, songs, k=1)[0][0]["title"]
    assert first == second


def test_parse_preferences_returns_required_keys():
    """parse_preferences output always has the keys recommend_songs needs."""
    from unittest.mock import patch, MagicMock
    import src.ai_assistant as ai_mod

    mock_response = MagicMock()
    mock_response.text = '{"genre": "pop", "mood": "happy", "energy": 0.8}'
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response

    with patch("src.ai_assistant._get_client", return_value=mock_client):
        prefs = ai_mod.parse_preferences("something upbeat and fun")

    required = {"genre", "mood", "energy"}
    assert required.issubset(prefs.keys())


def test_parse_preferences_falls_back_without_api():
    """Local fallback should keep the app usable if the model call fails."""
    import src.ai_assistant as ai_mod
    from unittest.mock import patch

    with patch("src.ai_assistant._get_client", side_effect=ValueError("No API key")):
        prefs = ai_mod.parse_preferences("something chill for studying")

    assert prefs["mood"] == "chill"
    assert prefs["genre"] in {"pop", "lofi"}
    assert isinstance(prefs["energy"], float)
