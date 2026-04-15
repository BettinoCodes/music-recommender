# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Goal / Task

VibeFinder 1.0 predicts which songs from a fixed catalog will feel most compatible with a user's current taste. Given a preference profile (genre, mood, energy target, acoustic preference), it scores every song in the catalog and returns the top five matches ranked by score.

It does not learn, remember previous sessions, or improve over time. It is a rule-based scoring engine, not a trained machine-learning model.

---

## 3. Intended Use and Non-Intended Use

### Intended use

- **Classroom exploration** — Understanding how scoring, weighting, and ranking turn structured data into ranked suggestions
- **Concept demonstration** — Showing the difference between collaborative filtering (other users' behavior) and content-based filtering (song attributes) without needing real user data
- **Experimentation** — Adjusting weights and features to see how recommendations change, which builds intuition for how real platforms tune their systems
- **Prototyping** — Testing a feature idea or scoring formula before wiring it up to a larger dataset or ML pipeline

### Not intended for

- **Real-world music discovery** — The 18-song catalog is far too small to provide meaningful variety; results will repeat and miss obvious good matches
- **Personalization over time** — The system has no memory; running it twice with the same profile gives identical results regardless of what the user listened to in between
- **Demographic or cultural representation** — The catalog skews toward Western popular genres and does not reflect the diversity of global music traditions
- **Production deployment** — There are no safety checks, rate limits, input validation, or abuse protections

---

## 4. How the Model Works

Imagine you hand a DJ a sticky note that says "I want chill lofi music, not too energetic, and I prefer acoustic sounds." The DJ goes through every song in their crate, gives it a score based on how well it matches your note, and hands you the top five.

That is exactly what VibeFinder does. For each song it checks four things:

1. **Does the genre match?** A match earns the biggest bonus (2 points) because genre is the widest filter — a jazz fan will rarely enjoy metal, no matter the mood.
2. **Does the mood match?** A match earns 1 point. Mood is more flexible than genre (a "chill" user might also enjoy "relaxed"), but it is still a meaningful signal.
3. **How close is the energy level?** Energy is a number between 0 and 1. The closer a song's energy is to the user's target, the more points it earns (up to 1 point). A perfect energy match adds 1.0; a song that is 0.5 away adds only 0.5.
4. **Acoustic bonus (optional):** If the user prefers acoustic music and a song is mostly acoustic, it earns an extra 0.5 points.

The song with the highest total score is recommended first.

---

## 5. Data

Imagine you hand a DJ a sticky note that says "I want chill lofi music, not too energetic, and I prefer acoustic sounds." The DJ goes through every song in their crate, gives it a score based on how well it matches your note, and hands you the top five.

That is exactly what VibeFinder does. For each song it checks three things:

1. **Does the genre match?** A match earns the biggest bonus (2 points) because genre is the widest filter — a jazz fan will rarely enjoy metal, no matter the mood.
2. **Does the mood match?** A match earns 1 point. Mood is more flexible than genre (a "chill" user might also enjoy "relaxed"), but it is still a meaningful signal.
3. **How close is the energy level?** Energy is a number between 0 and 1. The closer a song's energy is to the user's target, the more points it earns (up to 1 point). A perfect energy match adds 1.0; a song that is 0.5 away adds only 0.5.
4. **Acoustic bonus (optional):** If the user prefers acoustic music and a song is mostly acoustic, it earns an extra 0.5 points.

The song with the highest total score is recommended first.

---

## 5. Data

The catalog contains **18 songs** across **15 genres** and **12 distinct moods**.

**Genres:** pop, lofi, rock, ambient, jazz, synthwave, indie pop, r&b, country, classical, edm, hip-hop, metal, reggae, folk

**Moods:** happy, chill, intense, relaxed, focused, moody, sad, nostalgic, peaceful, euphoric, confident, aggressive

The starter dataset (10 songs) was extended with 8 new songs to add underrepresented genres and moods. Despite this expansion, the catalog is tiny compared to any real streaming service (Spotify has over 100 million tracks). Most genres appear only once or twice, which means the system has almost no choice when a user requests a less common genre like reggae or classical. The dataset reflects a general Western popular music taste and does not represent global music traditions.

---

## 6. Strengths

- **Clear, well-supported profiles** — When a user's genre and mood are both present in the catalog, the top result is almost always the correct intuitive pick. For example, the "lofi / chill" profile correctly surfaced *Library Rain* and *Midnight Coding* as #1 and #2 — exactly the kind of low-energy, acoustic tracks that fit that vibe.
- **Transparent reasoning** — Every recommendation comes with a line-by-line explanation (e.g., "genre match 'rock' (+2.0); energy proximity 0.99 (+0.99)"), so a user can immediately understand why they got a result and adjust their profile if it feels wrong.
- **No cold-start problem** — Because the system does not need listening history, it works immediately for any user who can describe their preferences.
- **Energy proximity is nuanced** — Using `1 - |song.energy - target|` means a song with energy 0.82 scores higher than one with 0.95 for a user targeting 0.8, which is more accurate than simply rewarding "higher energy."

---

## 7. Observed Behavior and Bias

### Catalog sparsity creates false precision

With only 18 songs, most genres have a single representative. When a user asks for "classical / peaceful," the only classical song (*String Theory*) wins by default regardless of how well it actually fits. The system looks confident when it is really just making the only choice available.

### Genre weight creates a hard ceiling for cross-genre discoveries

A genre match (+2.0) is worth more than a perfect mood match + perfect energy match combined (max 1.0 + 1.0 = 2.0). This means a song in the wrong genre can never score as high as a genre match with a bad mood and average energy. In a richer catalog this is a reasonable design choice, but in an 18-song catalog it means the system can be "tricked" by the one song that matches genre even if its other attributes are far off.

### Conflicting preferences expose a catalog gap

The adversarial "High-Energy Sad" profile (genre: r&b, mood: sad, energy: 0.9) revealed a real structural weakness. The only sad song in the catalog (*Broken Glass Heart*) has energy 0.52, far from the user's target of 0.9. The system correctly recommends it first because the genre + mood bonus (3.0 points) outweighs the energy penalty, but the remaining four recommendations are high-energy songs with no sad or r&b connection whatsoever. A user who wants sad but high-energy music (a real listening mode — think intense breakup anthems) gets almost no meaningful help.

### Unknown genres receive no bonus, only energy fallback

When a requested genre does not exist in the catalog (e.g., "bossa nova"), the system silently falls back to mood and energy only, with no warning to the user. The top results look reasonable numerically but the user has no idea their genre preference was completely ignored.

### Energy is the only continuous feature scored

Tempo, valence, and danceability are in the dataset but unused in scoring. Two songs with identical genre, mood, and energy scores are treated as identical even if one is a slow, melancholic waltz and the other is an upbeat dance track.

---

## 8. Evaluation Process

### Profiles tested

Six profiles were run against the 18-song catalog: three standard and three adversarial.

| Profile | Genre | Mood | Energy | Notes |
|---|---|---|---|---|
| High-Energy Pop | pop | happy | 0.80 | Standard baseline |
| Chill Lofi (acoustic) | lofi | chill | 0.38 | Acoustic bonus enabled |
| Deep Intense Rock | rock | intense | 0.90 | Standard baseline |
| High-Energy Sad | r&b | sad | 0.90 | Adversarial: conflicting mood/energy |
| Unknown Genre | bossa nova | chill | 0.40 | Adversarial: genre not in catalog |
| Mid-Everything Jazz | jazz | relaxed | 0.50 | Adversarial: average preferences |

### What the results showed

**High-Energy Pop** behaved exactly as designed. *Sunrise City* (pop, happy, energy 0.82) scored 3.98 and was the clear winner. *Gym Hero* (pop, intense, energy 0.93) came second purely on genre, which felt slightly off — it is a workout track, not a happy pop song — but the math was correct given the weights.

**Chill Lofi** was the strongest profile. All top three results were genuinely good lofi matches. *Library Rain* narrowly beat *Midnight Coding* (4.47 vs 4.46) purely because its energy (0.35) was marginally closer to the target (0.38) than Midnight Coding's (0.42). This one-hundredth-of-a-point margin shows how sensitive the system is to small energy differences.

**Deep Intense Rock** correctly put *Storm Runner* at #1 with a near-perfect score (3.99). The drop to #2 (*Gym Hero* at 1.97) was large, confirming that genre + mood + energy alignment is essential for a high score. Songs 3–5 were pure energy matches with no genre or mood alignment.

**High-Energy Sad (adversarial)** exposed the biggest weakness. *Broken Glass Heart* scored 3.62 and was correctly recommended first, but its energy (0.52) is far from the user's target (0.90), which the explanation clearly shows. Songs 2–5 were all high-energy tracks in completely unrelated genres (rock, pop, edm, metal). A real user in this state gets the right #1 but useless #2–5.

**Unknown Genre (bossa nova)** silently degraded to a mood+energy recommender. The top three results were chill-mood lofi/ambient tracks — which is arguably reasonable — but the user gets no feedback that their genre preference was ignored entirely.

**Mid-Everything Jazz** showed that a single exact match on a rare genre+mood pair dominates the list. *Coffee Shop Stories* (the only jazz song) scored 3.87 while #2 scored only 0.98 — a gap of nearly 3 points. The system was very "sure" but its confidence came only from catalog sparsity.

### Weight-shift experiment

Halving the genre weight (2.0 to 1.0) and doubling the energy multiplier (×1.0 to ×2.0) produced two notable changes:

1. For the High-Energy Pop profile, *Rooftop Lights* (indie pop, **happy**, energy 0.76) swapped from #3 to #2, displacing *Gym Hero* (pop, **intense**, energy 0.93). With stronger energy weighting, the mood-matching but wrong-genre song beat the genre-matching but wrong-mood song. This arguably felt more accurate — *Rooftop Lights* is closer to a "happy" vibe — but it required weakening the genre boundary.

2. For the High-Energy Sad adversarial profile, the gap between #1 and #2 shrank dramatically. *Storm Runner* (rock, intense, energy 0.91) rose from 0.99 to 1.98, getting dangerously close to a mood-and-genre-matching but energy-mismatched result. This felt less accurate: a rock track about intensity should not nearly outscore the only actual r&b sad song.

**Conclusion:** The original weights (genre=2.0) create clearer genre boundaries and are safer for an 18-song catalog. A bigger catalog with multiple songs per genre could support a lower genre weight without the system collapsing onto a single representative.

---

## 9. Ideas for Improvement

- **Add valence and tempo to the score** — valence (musical positiveness) could distinguish "high-energy happy" from "high-energy angry," which the current system cannot do.
- **Soft genre matching** — Instead of exact string matching, use a genre similarity map (e.g., lofi ~ ambient, metal ~ rock) so that a user requesting folk still gets partial credit for acoustic indie matches.
- **Catalog gap detection** — Warn the user when their requested genre is absent from the catalog instead of silently falling back to energy-only ranking.
- **Diversity injection** — After ranking by score, ensure the top-5 span at least two different genres so the list does not become five nearly-identical songs.
- **User feedback loop** — Allow users to thumbs-up/thumbs-down results and adjust weights automatically, which is how real collaborative systems are seeded.

---

## 10. Personal Reflection

### What was the biggest learning moment?

The biggest learning moment was running the adversarial "High-Energy Sad" profile and watching the system fall apart after #1. *Broken Glass Heart* was the correct top result, but songs 2–5 were a rock track, a pop workout song, an EDM drop, and a metal track — none of which had anything to do with sadness or r&b. The system was not wrong by its own rules; it was faithfully doing its job. The problem was that the catalog had no song that combined sad mood with high energy, so the scoring logic had nothing meaningful left to rank after the first pick. That moment made it real: a recommender is only as good as the data behind it. Rules and weights are just the decision layer on top. If the inventory does not contain what the user needs, the algorithm cannot invent it.

### How did using AI tools help, and when did you need to double-check?

AI tools were genuinely useful for three things: generating the expanded song catalog with realistic feature values, drafting the plain-language explanations in this model card, and quickly suggesting the `1 - abs(song.energy - target)` proximity formula when I was thinking about how to reward closeness rather than raw magnitude.

Double-checking was important in two places. First, the generated songs needed to be verified manually — the AI produced plausible-looking numbers, but I had to confirm that the energy, acousticness, and valence values actually made sense for the genre and mood combination (a "classical / peaceful" song with 0.22 energy and 0.97 acousticness is believable; those numbers should not be randomly high). Second, the weight recommendations from AI tended toward balance (equal weights for everything), which sounds fair but would have made genre and mood effectively meaningless compared to a perfectly-matched energy score. The decision to weight genre at 2.0 came from reasoning about the problem, not from the AI's first suggestion.

### What was surprising about how simple algorithms can still "feel" like recommendations?

The most surprising thing was that just three signals — genre, mood, and energy — were enough to produce results that felt intuitive for well-defined profiles. For the Chill Lofi user, the top two results were exactly the songs a human curator would pick. There was no machine learning, no neural network, no years of listening history: just a sticky note and arithmetic.

What made it feel real was the **explanation** attached to each result. When the output said "genre match 'lofi' (+2.0); mood match 'chill' (+1.0); energy proximity 0.97 (+0.97); acoustic bonus," it read like a reason, not a calculation. That is probably a large part of why "Because you listened to X" captions on Spotify feel trustworthy — the explanation creates the impression of understanding even when the underlying logic is far simpler than it appears.

### What would you try next if you extended this project?

Three things, in order of impact:

1. **Add valence to the score.** Valence (musical positiveness) is already in the dataset and would immediately solve the "High-Energy Sad" problem. A user targeting sad + high energy would get songs with low valence and high energy rather than just energy-adjacent songs in unrelated genres.

2. **Soft genre matching via a similarity map.** Right now `"folk" == "country"` is `False` and earns zero points, but folk and country share acoustic instrumentation and song structure. A simple dictionary like `{"folk": ["country", "indie folk"], "metal": ["rock", "punk"]}` would let nearby genres earn partial credit (e.g., +1.0 instead of +2.0) and dramatically improve results for niche profiles.

3. **A feedback loop.** After showing results, ask the user one question: "Did this match your vibe? (yes / kind of / no)." Use the answer to nudge the weights up or down for the next run. That is the seed of collaborative filtering — user behavior shaping future recommendations — and it would be a natural bridge from this content-based system toward how real platforms actually work.
