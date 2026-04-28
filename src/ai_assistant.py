import json
import os
import re
from dotenv import load_dotenv
from google import genai
from google.genai import types
from logger import logger

ENV_PATH = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=ENV_PATH)

MODEL = "gemini-2.0-flash-lite"
_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "No GEMINI_API_KEY found in the project .env file."
            )
        _client = genai.Client(api_key=api_key)
    return _client

VALID_GENRES = ["pop", "lofi", "rock", "jazz", "classical", "country", "hip hop",
                "metal", "reggae", "folk", "blues", "r&b", "indie", "electronic", "soul"]
VALID_MOODS = ["happy", "chill", "intense", "nostalgic", "peaceful", "confident",
               "rebellious", "laid-back", "soulful", "romantic", "sad", "energetic"]

PARSE_SYSTEM_PROMPT = f"""You are a music preference parser. Given a natural language description,
extract structured music preferences and return ONLY valid JSON with no extra text.

Return a JSON object with these keys (include only what you can infer):
- genre: one of {VALID_GENRES}
- mood: one of {VALID_MOODS}
- energy: float 0.0 to 1.0 (low energy = 0.0, high energy = 1.0)
- tempo: float in BPM (slow ~70, medium ~110, fast ~140+)
- valence: float 0.0 to 1.0 (sad/dark = 0.0, happy/bright = 1.0)
- danceability: float 0.0 to 1.0
- acousticness: float 0.0 to 1.0

Always include at least genre, mood, and energy. Return only the JSON object."""

EXPLAIN_SYSTEM_PROMPT = """You are a music recommendation assistant.
Given a user's request and a list of recommended songs, write a short friendly explanation
(2-4 sentences) of why these songs match what they were looking for.
Be specific — mention song titles and connect them to what the user described."""


GENRE_ALIASES = {
    "hip-hop": "hip hop",
    "hiphop": "hip hop",
    "rap": "hip hop",
    "rnb": "r&b",
    "rhythm and blues": "r&b",
}

MOOD_KEYWORDS = {
    "chill": "chill",
    "study": "chill",
    "focus": "chill",
    "calm": "peaceful",
    "peaceful": "peaceful",
    "happy": "happy",
    "upbeat": "happy",
    "fun": "happy",
    "intense": "intense",
    "aggressive": "intense",
    "nostalgic": "nostalgic",
    "throwback": "nostalgic",
    "confident": "confident",
    "bold": "confident",
    "rebellious": "rebellious",
    "laid back": "laid-back",
    "laid-back": "laid-back",
    "soulful": "soulful",
    "romantic": "romantic",
    "sad": "sad",
    "melancholic": "sad",
    "energetic": "energetic",
    "party": "energetic",
    "dance": "energetic",
}


def _extract_genre(text: str) -> str:
    normalized = text.lower()
    for alias, genre in GENRE_ALIASES.items():
        if alias in normalized:
            return genre
    for genre in VALID_GENRES:
        if genre in normalized:
            return genre
    return "pop"


def _extract_mood(text: str) -> str:
    normalized = text.lower()
    for keyword, mood in MOOD_KEYWORDS.items():
        if keyword in normalized:
            return mood
    return "chill"


def _extract_energy(text: str, mood: str) -> float:
    normalized = text.lower()
    if any(word in normalized for word in ["calm", "soft", "gentle", "quiet", "sleep"]):
        return 0.25
    if any(word in normalized for word in ["study", "focus", "late night", "late-night", "chill"]):
        return 0.4
    if any(word in normalized for word in ["upbeat", "party", "dance", "workout", "hype"]):
        return 0.85
    if mood in {"energetic", "intense", "confident", "rebellious"}:
        return 0.8
    if mood in {"happy", "nostalgic", "romantic", "soulful"}:
        return 0.6
    return 0.45


def _extract_numeric_hint(text: str, label: str) -> float | None:
    pattern = rf"{label}\s*(?:of|around|near|about|=)?\s*(\d+(?:\.\d+)?)"
    match = re.search(pattern, text.lower())
    if not match:
        return None
    return float(match.group(1))


def _fallback_parse_preferences(user_message: str) -> dict:
    mood = _extract_mood(user_message)
    prefs = {
        "genre": _extract_genre(user_message),
        "mood": mood,
        "energy": _extract_energy(user_message, mood),
    }

    bpm = _extract_numeric_hint(user_message, "bpm|tempo")
    if bpm is not None:
        prefs["tempo"] = bpm

    if any(word in user_message.lower() for word in ["dance", "club", "party"]):
        prefs["danceability"] = 0.85
    if any(word in user_message.lower() for word in ["acoustic", "unplugged"]):
        prefs["acousticness"] = 0.85
    if any(word in user_message.lower() for word in ["sad", "melancholic"]):
        prefs["valence"] = 0.25
    if any(word in user_message.lower() for word in ["happy", "bright", "sunny"]):
        prefs["valence"] = 0.8

    return prefs


def _fallback_explanation(user_message: str, songs: list) -> str:
    if not songs:
        return "I could not find any strong matches for that request."

    top_titles = [song.get("title", "Unknown") for song in songs[:2]]
    titles = " and ".join(top_titles)
    primary = songs[0]
    return (
        f"I matched your request for '{user_message}' using the song catalog's genre, mood, "
        f"and audio features. {titles} rise to the top because they align most closely with "
        f"a {primary.get('mood', 'matching')} mood and {primary.get('genre', 'similar')} sound."
    )


def parse_preferences(user_message: str) -> dict:
    """Parse natural language into structured preferences for the recommender."""
    logger.info(f"Parsing preferences for: {user_message!r}")
    try:
        response = _get_client().models.generate_content(
            model=MODEL,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=PARSE_SYSTEM_PROMPT,
                max_output_tokens=256,
            ),
        )

        raw = response.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        logger.info(f"Parsed preferences raw response: {raw}")

        prefs = json.loads(raw)
        required = {"genre", "mood", "energy"}
        missing = required - prefs.keys()
        if missing:
            raise ValueError(f"Parsed preferences missing required keys: {missing}")
        return prefs
    except Exception as exc:
        logger.warning(f"Falling back to local preference parsing: {exc}")
        return _fallback_parse_preferences(user_message)


def explain_recommendations(user_message: str, songs: list) -> str:
    """Generate a natural language explanation for why the recommended songs fit."""
    song_list = "\n".join(
        f"- {s.get('title', 'Unknown')} by {s.get('artist', 'Unknown')} "
        f"(genre: {s.get('genre')}, mood: {s.get('mood')}, energy: {s.get('energy')})"
        for s in songs
    )

    prompt = f"User request: {user_message}\n\nRecommended songs:\n{song_list}"
    logger.info(f"Generating explanation for {len(songs)} songs")

    try:
        response = _get_client().models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=EXPLAIN_SYSTEM_PROMPT,
                max_output_tokens=256,
            ),
        )

        explanation = response.text.strip()
        logger.info(f"Explanation generated: {explanation[:80]}...")
        return explanation
    except Exception as exc:
        logger.warning(f"Falling back to local explanation generation: {exc}")
        return _fallback_explanation(user_message, songs)
