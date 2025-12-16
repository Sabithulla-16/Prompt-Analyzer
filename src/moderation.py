BANNED_KEYWORDS = [
    "hack", "crack", "piracy", "illegal",
    "porn", "nsfw", "sexual", "violence",
    "drugs", "weapon", "bomb"
]

def is_safe(prompt: str) -> bool:
    p = prompt.lower()
    return not any(word in p for word in BANNED_KEYWORDS)