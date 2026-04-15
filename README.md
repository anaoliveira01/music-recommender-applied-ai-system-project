# 🎵 Music Recommender Simulation

## Project Summary

This project is a music recommender system that uses weighted scoring to rank 18 songs based on users with UserProfile, which is a structured taste profile that includes optional numerical targets for tempo, valence, danceability, liveness, speechiness, instrumentalness, preferred, genre, mood, energy, level, and acoustic preference. Each song is given a score by adding continuous similarity scores for any numerical preferences specified by the user and rewarding genre and mood matches with fixed bonuses (2.5 and 4.0 respectively). The system provides two interfaces: an object-oriented Recommender class that takes UserProfile objects, converts them internally, and returns ranked Song objects with human-readable explanations, and a dictionary-based recommend_songs function for flexible scripting. Through testing, the system discovered that mood weight predominates scoring heavily enough to elevate off-genre songs above on-genre ones and that sparse genre coverage (13 out of 15 genres have only one song) creates filter bubbles where most users receive the same top result regardless of their other preferences. These patterns are similar to those found in real-world recommender systems which likewise amplify popularity bias and lock users into narrow taste clusters when training data is uneven.

---

## How The System Works

Explain your design in plain language.
- Real-world recommendation systems combine user preferences with item characteristics, then score each candidate for how well it matches those preferences.
- This system reads every song from `data/songs.csv`, compares each song to the user profile, and assigns a score based on how well the song matches the preferred genre, mood, and energy shape.
- Genre and mood matches are the strongest signals, while numeric audio features like tempo, valence, and danceability refine the score.
- The ranked output is the top songs sorted from best match to worst match.
- Algorithm recipe: score each song by genre/mood match and feature similarity, then sort the catalog by score and return the top results.
- Potential bias: the small catalog can favor more common genres and moods, so less frequent styles may be under-represented.

Some prompts to answer:

- What features does each `Song` use in your system
  - For example: genre, mood, energy, tempo
    - Each song includes: id, title, artist, genre, mood, energy, tempo_bpm, valence, danceability, acousticness, liveness, speechiness, and instrumentalness.

- What information does your `UserProfile` store
  - Each UserProfile includes favorite_genre, favorite_mood, target_energy, and preferences for acoustic or instrumental qualities.

- How does your `Recommender` compute a score for each song
  - It computes a score by comparing each song's attributes to the user's preferences.
    - Exact genre match gets a high weight.
    - Exact mood match gets a slightly lower (but still strong) weight.
    - Numeric feature differences are converted into smaller similarity scores.

- How do you choose which songs to recommend
  - The recommender scores every song, sorts them by descending score, and returns the top k songs as the final recommendation list.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
  - Rooftop Lights (indie pop, happy mood) outranked Gym Hero (pop, intense mood) because the mood bonus alone outweighed the genre bonus.
- What happened when you added tempo or valence to the score
  - On a pop/happy profile: the top 3 (Sunrise City, Rooftop Lights, Gym Hero) were identical. Only positions 4 and 5 changed — Storm Runner and Dream City swapped, because Dream City's danceability (0.80) was a closer match to the target (0.8) than Storm Runner's (0.66).
- How did your system behave for different types of users
  - For niche genre users (jazz, classical, reggae), the single matching song always ranked #1. The remaining slots filled in reasonably with acoustically similar songs from other genres.

---

## Limitations and Risks

- The catalog has only 18 songs, and 13 of 15 genres have exactly one entry — most users receive the same #1 result every time with no variation.
- Mood weight (4.0) after adjusting dominates scoring so heavily that a pop song (Gym Hero) consistently outranks metal songs for a user asking for rock due to a shared mood tag.
- The system has no memory — it never learns from what a user has already heard, skipped, or liked, so recommendations never improve over time.
- All preferences are positive signals only; there is no way to say "no metal" or "nothing above 150 BPM," so disliked songs can still rank highly if their numeric attributes happen to match.
- A user can only express one genre and one mood, so someone who listens to both jazz and lofi gets no credit for their second preference.
- Features like artist, release year, lyrics language, and listening context (workout, sleep, commute) are not represented in the dataset.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

How recommenders turn data into predictions:
- Building this system made it clear that a recommender is mostly a scoring formula, and the weights are what makes a real difference. Every time the mood weight of 4.0 pushed a pop song above a metal song for a rock user, it was exactly what the numbers were meant to do. The "intelligence" of the system lives entirely in how the weights are set, and those choices are made by a person before any user opens the app.

Where bias or unfairness could show up in systems like this:
- The bias that stood out most was how catalog size silently shapes results. Thirteen of fifteen genres had only one song, so users preferring jazz or classical had no choice but to get the same result every session — no weight tuning could fix that. Real systems like Spotify face the same issue at scale: popular content gets recommended more, which makes it more popular, which gets it recommended more, all before any individual user has any influence.


- Demo:

![Screenshot 1](imgs/2026-04-14(1).png)
![Screenshot 2](imgs/2026-04-14(2).png)
![Screenshot 3](imgs/2026-04-14(3).png)

---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

> Music Matcher

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

This system recommends up to 5 songs from an 18-song catalog by scoring each song against a user's preferred genre, mood, energy level, and optional numeric targets (tempo, valence, danceability, and more). It is built for classroom exploration — to make the mechanics of a real recommender system tangible and testable — not for production use with real listeners.

---

## 3. How It Works (Short Explanation)

Description of the scoring logic in plain language:

- What features of each song does it consider?
  - Genre, mood, energy, tempo, valence (how positive or happy the song sounds), danceability, acousticness, liveness, speechiness, and instrumentalness.

- What information about the user does it use?
  - A favorite genre, a favorite mood, a target energy level, whether they prefer acoustic music, and optional targets for any of the numeric song features above.

- How does it turn those into a number?
  - It adds up points: a fixed bonus if the genre matches, a larger fixed bonus if the mood matches, and for each numeric preference the user set, a score between 0 and 1 based on how close the song's value is to the user's target. All those points are summed into one final score, and the five songs with the highest scores are returned.



---

## 4. Data

The catalog contains 18 songs. I added 8 songs to the starter catalog containing only 10 — Golden Hour Strings, Sunset Highway, Dream City, Midnight Ember, Tropical Breeze, Soft Lanterns, Blue Velvet, and Velvet Nights — bringing the total to 18. Three additional audio features were also added to every song: liveness, speechiness, and instrumentalness.
The added songs expanded the genre coverage to include classical, country, hip hop, metal, reggae, folk, blues, and r&b, and introduced new moods like nostalgic, peaceful, confident, rebellious, laid-back, soulful, and romantic that were absent from the starter set. Despite the expansion, the distribution is still uneven — lofi has 3 songs, pop has 2, and every other genre has exactly one. Users who prefer the added genres have a single fixed recommendation with not much variation.
The catalog also skews toward Western, English-language genres and excludes non-Western music entirely, which means the data reflects a narrow slice of global musical taste.

---

## 5. Strengths

Where the recommender works well:

- Profiles with many features set — the chill lofi profile (7 features: genre, mood, energy, tempo, valence, danceability, acousticness) produced the most convincing results. All five recommendations were genuinely low-energy, acoustic, and calm: Midnight Coding, Library Rain, Spacewalk Thoughts, Focus Flow, and Coffee Shop Stories. The extra features gave the scoring enough signal to differentiate songs meaningfully.
- Niche genre users — despite the sparse catalog, users preferring jazz, classical, or reggae always received their single matching song as #1. The system didn't bury it or return something random; it correctly surfaced the best available match every time.
- Explainability — every recommendation comes with a plain-language reason (e.g. "genre match (+2.5); mood match (+4.0); energy similarity (+1.96)"). It is always clear exactly why a song ranked where it did, which is rare in real recommender systems that use black-box models.
- Simplicity — because the scoring is a straightforward weighted sum, it is easy to adjust. Changing a weight or adding a new preference takes one line of code and the effect is immediately traceable in the output.

---

## 6. Limitations and Bias

Where the recommender struggles:

- Mood weight dominates: the mood bonus (4.0) is large enough that a song with the right mood but the wrong genre consistently outranks songs with the right genre.
- Single-song genres create filter bubbles — 13 of 15 genres have exactly one song. Users who prefer classical, blues, metal, reggae, jazz, country, folk, or r&b will repeatedly receive the same #1 result
- One genre, one mood — the profile assumes every user has a single favorite genre and mood.
- Unfair at scale — if this were a real product, users whose tastes fall outside pop and lofi would receive noticeably worse recommendations simply because less data exists for their genres.
---

## 7. Evaluation

How I checked the system:

- Four profiles were tested against the full 18-song catalog: a minimal starter profile (genre, mood, energy only), high energy pop, chill lofi, and deep intense rock. For each, the top-5 results and scores were printed and checked against intuition
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
