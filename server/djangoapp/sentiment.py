"""Small deterministic sentiment baseline, not an external AI prediction.

Words carry a +/-1 weight. A negation in the previous two words inverts
that weight. The score sign maps to positive, negative, or neutral.
"""

import re

POSITIVE = {
    "amazing",
    "awesome",
    "best",
    "excellent",
    "fantastic",
    "friendly",
    "good",
    "great",
    "helpful",
    "honest",
    "love",
    "loved",
    "perfect",
    "recommend",
    "satisfied",
    "wonderful",
}
NEGATIVE = {
    "awful",
    "bad",
    "broken",
    "disappointed",
    "dishonest",
    "hate",
    "horrible",
    "poor",
    "rude",
    "terrible",
    "unhappy",
    "unhelpful",
    "worst",
}
NEGATIONS = {"not", "never", "no", "hardly", "isn't", "wasn't", "don't", "didn't"}


def analyze(text):
    words = re.findall(r"[a-z]+(?:'[a-z]+)?", text.lower())
    score = 0
    for index, word in enumerate(words):
        weight = int(word in POSITIVE) - int(word in NEGATIVE)
        if any(previous in NEGATIONS for previous in words[max(0, index - 2) : index]):
            weight = -weight
        score += weight
    return "positive" if score > 0 else "negative" if score < 0 else "neutral"
