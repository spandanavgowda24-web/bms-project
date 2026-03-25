import re

def detect_steps(text, language="en"):

    if not text:
        return []

    text = text.strip()

    # =============================
    # 🔥 SPLIT SENTENCES
    # =============================
    sentences = re.split(r'[.!?।]', text)

    steps = []

    # =============================
    # 🔥 ENGLISH LOGIC
    # =============================
    if language == "en":

        action_verbs = [
            "add","apply","take","use","mix","put","heat","wash","cut","boil",
            "start","pour","cook","dry","clean","press","open","close","insert"
        ]

        connectors = ["first", "then", "next", "after", "finally"]

        ignore_phrases = [
            "hi", "hello", "welcome", "good morning", "good evening",
            "today", "guys", "friends", "my name", "thanks"
        ]

        for s in sentences:

            line = s.strip().lower()

            if len(line) < 10:
                continue

            if any(p in line for p in ignore_phrases):
                continue

            if line.startswith("i "):
                continue

            if any(c in line for c in connectors):
                steps.append(line.capitalize())
                continue

            words = line.split()

            if words and words[0] in action_verbs:
                steps.append(line.capitalize())
                continue

            if any(v in line for v in action_verbs) and len(words) <= 15:
                steps.append(line.capitalize())

    # =============================
    # 🔥 HINDI / KANNADA (FIXED)
    # =============================
    else:

        for s in sentences:

            line = s.strip()

            if len(line) < 15:
                continue

            # ❌ remove useless talk
            if any(x in line.lower() for x in ["hello", "welcome"]):
                continue

            # 🔥 SIMPLE RULE: keep meaningful lines
            steps.append(line)

    # =============================
    # 🔥 REMOVE DUPLICATES
    # =============================
    final_steps = []
    for s in steps:
        if s not in final_steps:
            final_steps.append(s)

    # =============================
    # 🔥 FINAL FIX (IMPORTANT)
    # =============================
    if len(final_steps) < 2:
        return []   # will become summary

    return final_steps