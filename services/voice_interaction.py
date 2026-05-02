import re

# =========================
# 🔥 NORMALIZE TEXT
# =========================
def normalize(text):
    text = text.lower().strip()

    # remove noise symbols
    text = re.sub(r'[^\w\s]', '', text)

    # normalize spaces
    text = re.sub(r'\s+', ' ', text)

    return text


# =========================
# 🔥 SMART MATCH (STRONG NLP)
# =========================
def match(text, patterns):
    return any(p in text for p in patterns)


# =========================
# 🔥 MAIN DETECTOR
# =========================
def detect_command(text):

    if not text:
        return "unknown"

    text = normalize(text)

    # =========================
    # 🔥 COMMAND GROUPS
    # =========================

    START = [
        "start", "begin", "lets start", "go ahead",
        "shuru", "prarambh", "start madi", "start maadi"
    ]

    NEXT = [
        "next", "next step", "continue", "move on", "go next",
        "agla", "aage", "munde", "mundhe", "ಮುಂದೆ"
    ]

    PREVIOUS = [
        "previous", "go back", "back", "one step back",
        "pichla", "peeche", "wapas",
        "hinde", "hindhe", "ಹಿಂದೆ"
    ]

    REPEAT = [
        "repeat", "again", "say again", "repeat that",
        "dobara", "phir se",
        "matte", "ಮತ್ತೆ"
    ]

    STOP = [
        "stop", "pause", "enough", "stop it",
        "ruk", "band karo",
        "nillisi", "ನಿಲ್ಲಿಸು"
    ]

    LAST = [
        "last", "final", "last step", "end",
        "akhri", "kone", "ಕೊನೆ"
    ]

    FIRST = [
        "first", "step one", "beginning",
        "pehla", "modala", "ಮೊದಲ"
    ]

    RESTART = [
        "restart", "start again", "from beginning",
        "phirse shuru", "modlinda", "ಮೊದಲಿನಿಂದ"
    ]

    # =========================
    # 🔥 PRIORITY DETECTION
    # =========================

    # 🔥 STOP FIRST (important)
    if match(text, STOP):
        return "stop"

    # 🔥 STEP NUMBER (SMART)
    match_step = re.search(r'(step\s*)?(\d+)', text)
    if match_step:
        num = int(match_step.group(2))
        return f"step_{num}"

    # 🔥 EXACT COMMANDS
    if match(text, START):
        return "start"

    if match(text, NEXT):
        return "next"

    if match(text, PREVIOUS):
        return "previous"

    if match(text, REPEAT):
        return "repeat"

    if match(text, RESTART):
        return "restart"

    if match(text, LAST):
        return "last"

    if match(text, FIRST):
        return "first"

    # =========================
    # 🔥 SMART SENTENCE UNDERSTANDING
    # =========================

    if "go" in text and "next" in text:
        return "next"

    if "go" in text and "back" in text:
        return "previous"

    if "say" in text and "again" in text:
        return "repeat"

    if "start" in text and "again" in text:
        return "restart"

    if "last step" in text:
        return "last"

    if "first step" in text:
        return "first"

    # =========================
    # 🔥 CONFIRMATION
    # =========================
    if any(p in text for p in ["yes", "ok", "okay", "haan", "haanji"]):
        return "start"

    return "unknown"