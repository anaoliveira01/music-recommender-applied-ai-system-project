# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**Music Matcher**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

This system recommends up to 5 songs from an 18-song catalog by scoring each song against a user's preferred genre, mood, energy level, and optional numeric targets (tempo, valence, danceability, and more). It is built for classroom exploration — to make the mechanics of a real recommender system tangible and testable — not for production use with real listeners.

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

- What features of each song does it consider?
  - Genre, mood, energy, tempo, valence (how positive or happy the song sounds), danceability, acousticness, liveness, speechiness, and instrumentalness.

- What information about the user does it use?
  - A favorite genre, a favorite mood, a target energy level, whether they prefer acoustic music, and optional targets for any of the numeric song features above.

- How does it turn those into a number?
  - It adds up points: a fixed bonus if the genre matches, a larger fixed bonus if the mood matches, and for each numeric preference the user set, a score between 0 and 1 based on how close the song's value is to the user's target. All those points are summed into one final score, and the five songs with the highest scores are returned.

---

## 4. Data  

Describe the dataset the model uses.  

The catalog contains 18 songs. I added 8 songs to the starter catalog containing only 10 — Golden Hour Strings, Sunset Highway, Dream City, Midnight Ember, Tropical Breeze, Soft Lanterns, Blue Velvet, and Velvet Nights — bringing the total to 18. Three additional audio features were also added to every song: liveness, speechiness, and instrumentalness.
The added songs expanded the genre coverage to include classical, country, hip hop, metal, reggae, folk, blues, and r&b, and introduced new moods like nostalgic, peaceful, confident, rebellious, laid-back, soulful, and romantic that were absent from the starter set. Despite the expansion, the distribution is still uneven — lofi has 3 songs, pop has 2, and every other genre has exactly one. Users who prefer the added genres have a single fixed recommendation with not much variation.
The catalog also skews toward Western, English-language genres and excludes non-Western music entirely, which means the data reflects a narrow slice of global musical taste.

---

## 5. Strengths  

Where does your system seem to work well  

- Profiles with many features set — the chill lofi profile (7 features: genre, mood, energy, tempo, valence, danceability, acousticness) produced the most convincing results. All five recommendations were genuinely low-energy, acoustic, and calm: Midnight Coding, Library Rain, Spacewalk Thoughts, Focus Flow, and Coffee Shop Stories. The extra features gave the scoring enough signal to differentiate songs meaningfully.
- Niche genre users — despite the sparse catalog, users preferring jazz, classical, or reggae always received their single matching song as #1. The system didn't bury it or return something random; it correctly surfaced the best available match every time.
- Explainability — every recommendation comes with a plain-language reason (e.g. "genre match (+2.5); mood match (+4.0); energy similarity (+1.96)"). It is always clear exactly why a song ranked where it did, which is rare in real recommender systems that use black-box models.
- Simplicity — because the scoring is a straightforward weighted sum, it is easy to adjust. Changing a weight or adding a new preference takes one line of code and the effect is immediately traceable in the output.

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

One weakness discovered during experiments for this system is that the new mood weight dominance creates a single-song bias because most of the moods listed are unique and not repeated. This means a user whose favorite_mood matches one of those rare moods will effectively always receive the same song as their top result, because no combination of genre, energy, or other numeric similarities can overcome a 4.0-point head start for the mood. For example, a user preferring "soulful" music will always see "Blue Velvet" ranked first, even if its tempo, valence, and energy are a poor fit.

- Chill lofi had the most dramatic change — 4 out of 5 songs are completely different, and all 5 now fit the genre/mood/acoustic profile.
- Starter and High energy pop share the same top 3, confirming the earlier finding that genre+mood lock in the ranking before numeric features can differentiate.
- Deep intense rock now surfaces Storm Runner (#1) and Midnight Ember (#3) where before it had no genre-relevant songs at all.
- The "before" list (Sunrise City through Gym Hero) was hardcoded CSV insertion order — it was the same for every user, making the system useless for personalization.


- Mood weight dominates: the mood bonus (4.0) is large enough that a song with the right mood but the wrong genre consistently outranks songs with the right genre.
- Single-song genres create filter bubbles — 13 of 15 genres have exactly one song. Users who prefer classical, blues, metal, reggae, jazz, country, folk, or r&b will repeatedly receive the same #1 result
- One genre, one mood — the profile assumes every user has a single favorite genre and mood.
- Unfair at scale — if this were a real product, users whose tastes fall outside pop and lofi would receive noticeably worse recommendations simply because less data exists for their genres.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

- Which user profiles you tested
    - Four user profiles were tested with the 18-song catalog: a minimal "starter" profile with genre, mood, and energy only, a "high energy pop" profile, "chill lofi", and "deep intense rock". The most unexpected result came from the "deep intense rock" profile. Despite preferring rock music, "Gym Hero" - a pop song - ranked in 2nd place, beating out "Midnight Ember" - metal - because both share the "intense" mood tag.

- Two automated tests were written and run with pytest. The first checks that recommend returns songs sorted by score with the best match first — a pop/happy/energy=0.8 user should receive the pop, happy song above all others. The second checks that explain_recommendation returns a non-empty string for any valid song and user pair.
- The most revealing check was running the same profiles before and after implementing Recommender.recommend. Before the fix, every user received the same five songs (the first five rows of the CSV) regardless of their preferences. After the fix, chill lofi users received entirely different results from rock users, confirming personalization was working.
- Weight sensitivity was also checked by rerunning profiles with mood weight reduced (4.0 to 1.5) or genre weight reduced (2.5 to 0.5). This showed that these numeric weights were the biggest influence on the results.

---

## 8. Future Work  

I would improve this recommender by:

- Using negative preferences — the scoring is all positive signals. A user who dislikes metal or pop for example can't express that.
- Multi-genre / multi-mood profiles — Right now UserProfile holds one genre and one mood. Changing favorite_genre to favorite_genres: List[str] with weighted bonuses per match would help users with diverse tastes.
- Listening history / feedback loop — The system has no memory. A good extension would be to track songs the user has already received and filter or penalize repeats so the same catalog doesn't return the same results every session.

---

## 9. Personal Reflection  

What I learned:

- The mood and genre weights dominated far more than expected compared to other features.
- It made clear that a recommender is mostly a scoring formula, and the weights are where all the real decisions live.
- Human judgement still matters where the numbers don't capture context - whether a song fits a funeral or a road trip, whether an artist has said something harmful, whether a user is burned out on a genre they technically still "prefer", etc.
The system also has no concept of enough — it will keep surfacing the same songs because they score well.
