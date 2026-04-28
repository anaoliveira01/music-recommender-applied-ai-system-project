import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from recommender import load_songs, recommend_songs
from ai_assistant import parse_preferences, explain_recommendations
from logger import logger

SONGS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "songs.csv")

@st.cache_data
def get_songs():
    return load_songs(SONGS_PATH)

st.title("Music Recommender")
st.caption("Describe what you're in the mood for and get personalized song recommendations.")

user_input = st.text_input("What are you in the mood for?",
                           placeholder="e.g. something chill for a late night study session")

if st.button("Find Songs") and user_input.strip():
    with st.spinner("Finding songs for you..."):
        try:
            logger.info(f"New request: {user_input!r}")

            prefs = parse_preferences(user_input)
            st.caption(f"Interpreted as: {prefs}")

            songs = get_songs()
            results = recommend_songs(prefs, songs, k=5)

            top_songs = [song for song, _, _ in results]
            explanation = explain_recommendations(user_input, top_songs)

            st.markdown(f"**Why these songs:** {explanation}")
            st.divider()

            for i, (song, score, reasons) in enumerate(results, start=1):
                st.markdown(f"**{i}. {song['title']}** — {song['artist']}")
                st.caption(f"{song['genre']} · {song['mood']} · energy {song['energy']} · score {score:.2f}")
                st.caption(f"Reasons: {reasons}")

        except ValueError as e:
            logger.error(f"Preference parsing failed: {e}")
            st.error(f"Could not understand your request. Try describing the mood or genre more clearly.")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            st.error("Something went wrong while generating recommendations. Check logs/app.log for details.")
