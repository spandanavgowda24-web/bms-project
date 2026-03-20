import spacy
import re

# English NLP (unchanged)
nlp = spacy.load("en_core_web_sm")


def detect_steps(text):

    import re

    sentences = re.split(r'[.!?]', text)

    steps = []

    action_verbs = [
        "add","apply","take","use","mix","put","heat","wash","cut","boil",
        "start","pour","cook","dry","clean","press","open","close","insert"
    ]

    connectors = ["first", "then", "next", "after", "finally"]

    ignore_phrases = [
        "hi", "hello", "welcome", "good morning", "good evening",
        "today", "guys", "friends", "my name", "thanks",
        "i think", "i like", "i love", "i prefer"
    ]

    for s in sentences:

        line = s.strip().lower()

        if len(line) < 10:
            continue

        # ❌ remove useless talk
        if any(p in line for p in ignore_phrases):
            continue

        # ❌ remove personal talk
        if line.startswith("i "):
            continue

        # ✅ keep if sequence words
        if any(c in line for c in connectors):
            steps.append(line.capitalize())
            continue

        # ✅ keep if starts with action
        words = line.split()
        if words and words[0] in action_verbs:
            steps.append(line.capitalize())
            continue

        # ✅ keep if strong action sentence
        if any(v in line for v in action_verbs):
            if len(words) <= 15:
                steps.append(line.capitalize())

    # remove duplicates
    final_steps = []
    for s in steps:
        if s not in final_steps:
            final_steps.append(s)

    return final_steps

    # =============================
    # UNKNOWN LANGUAGE
    # =============================
    return [text]