import requests
import re

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
PROMPT_CACHE = {}

# =========================================================
# 1️⃣ RULE-BASED NORMALIZATION (FIRST LINE OF DEFENSE)
# =========================================================

RULES = [
    # AUDIO / SPEECH → TEXT (English, Hindi, Hinglish)
    (
        r"(awaaz|voice|audio|speech|bol).*?(text|likh|likho|text mein|words)",
        "Convert my voice recording into text"
    ),

    # LETTER / EMAIL / WRITING
    (
        r"(letter|email|mail|application|resume|cv)",
        "Write a letter or email using AI"
    ),

    # IMAGE / LOGO / DESIGN
    (
        r"(logo|design|creative|poster|image|photo)",
        "Create a professional logo or image"
    ),

    # CODE
    (
        r"(code|coding|program|python|java|c\+\+)",
        "Write code using AI"
    ),

    # VIDEO / REELS
    (
        r"(video|reel|short|youtube|instagram)",
        "Create short videos or reels using AI"
    ),

    # SUMMARIZATION
    (
        r"(summarize|summary|research|paper|notes)",
        "Summarize a document or research paper"
    ),
]

def rule_based_rewrite(prompt: str) -> str | None:
    text = prompt.lower()
    for pattern, normalized in RULES:
        if re.search(pattern, text):
            return normalized
    return None


# =========================================================
# 2️⃣ STRICT LLM PROMPT (REWRITE ONLY, NOT CHAT)
# =========================================================

SYSTEM_MESSAGE = """
You are NOT a chat assistant.

You are a PROMPT NORMALIZER for an AI tool selection system.

Your ONLY task:
- Rewrite the user input into ONE short, clear AI task.

STRICT RULES:
- Do NOT answer the user
- Do NOT ask questions
- Do NOT explain anything
- Do NOT say "I will help you"
- Do NOT give steps or guidance
- Output ONLY ONE sentence

The output MUST:
- Start with a verb (Write, Create, Generate, Convert, Summarize)
- Be neutral and tool-agnostic
- Be suitable for selecting an AI tool

Examples:

Input: help me to write letter
Output: Write a letter using AI

Input: can you write email for me
Output: Write an email using AI

Input: logo
Output: Create a professional logo for a startup

Input: meri awaaz ko text mein badlo
Output: Convert my voice recording into text
"""

CHAT_PATTERNS = [
    "i will help",
    "please provide",
    "let me",
    "sure,",
    "i can help",
    "start by",
    "here is",
    "step",
    "first,"
]

# =========================================================
# 3️⃣ MAIN REWRITE FUNCTION
# =========================================================

def rewrite_prompt(user_prompt: str) -> str:
    if user_prompt in PROMPT_CACHE:
        return PROMPT_CACHE[user_prompt]

    # ---------- RULE-BASED FIRST ----------
    rule_result = rule_based_rewrite(user_prompt)
    if rule_result:
        PROMPT_CACHE[user_prompt] = rule_result
        return rule_result

    # ---------- LLM SECOND ----------
    try:
        response = requests.post(
            OLLAMA_CHAT_URL,
            json={
                "model": "qwen2:0.5b",
                "messages": [
                    {"role": "system", "content": SYSTEM_MESSAGE},
                    {"role": "user", "content": user_prompt}
                ],
                "stream": False
            },
            timeout=None
        )
        response.raise_for_status()

        rewritten = response.json()["message"]["content"].strip()

        # ---------- HARD REJECTION OF CHAT-LIKE OUTPUT ----------
        if (
            not rewritten
            or len(rewritten.split()) < 3
            or any(p in rewritten.lower() for p in CHAT_PATTERNS)
        ):
            rewritten = user_prompt

        PROMPT_CACHE[user_prompt] = rewritten
        return rewritten

    except Exception as e:
        print("⚠️ Rewrite failed:", e)
        PROMPT_CACHE[user_prompt] = user_prompt
        return user_prompt