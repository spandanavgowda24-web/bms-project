def detect_command(text):

    if not text:
        return "unknown"

    text = text.lower()

    # -------------------------
    # START / BEGIN
    # -------------------------
    if any(p in text for p in [
        "start", "begin", "let's start", "go ahead"
    ]):
        return "start"

    # -------------------------
    # NEXT
    # -------------------------
    if any(p in text for p in [
        "next", "continue", "go ahead", "move on", "next step"
    ]):
        return "next"

    # -------------------------
    # PREVIOUS
    # -------------------------
    if any(p in text for p in [
        "previous", "go back", "last step", "back"
    ]):
        return "previous"

    # -------------------------
    # REPEAT
    # -------------------------
    if any(p in text for p in [
        "repeat", "again", "say again", "repeat that"
    ]):
        return "repeat"

    # -------------------------
    # RESTART
    # -------------------------
    if any(p in text for p in [
        "restart", "start again", "from beginning"
    ]):
        return "restart"

    # -------------------------
    # GO TO STEP NUMBER
    # -------------------------
    import re
    match = re.search(r'\b(\d+)\b', text)

    if match:
        return f"step_{match.group(1)}"

    # -------------------------
    # CONFIRMATION
    # -------------------------
    if any(p in text for p in [
        "yes", "okay", "ok", "sure"
    ]):
        return "start"

    return "unknown"