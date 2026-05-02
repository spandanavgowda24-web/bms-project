# services/step_detector.py - FIXED (Lower threshold)
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def detect_steps(text, language="en"):
    """
    Extract steps from transcript - LOWER THRESHOLD
    """
    if not text or len(text.strip()) < 20:
        logger.warning(f"Text too short: {len(text) if text else 0}")
        return []

    steps = []
    text_lower = text.lower()

    # Split into sentences
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 15]

    # Method 1: Numbered steps (1., 2., etc.)
    for s in sentences:
        if re.match(r'^\d+\.', s):
            step_text = re.sub(r'^\d+\.\s*', '', s)
            if len(step_text) > 10:
                steps.append(step_text)

    # Method 2: Step markers (first, then, next, etc.)
    if len(steps) < 2:
        step_markers = [
            'first', 'then', 'next', 'after', 'finally', 'step',
            'पहले', 'फिर', 'अगला', 'बाद', 'अंत में',
            'ಮೊದಲು', 'ನಂತರ', 'ಮುಂದೆ', 'ಕೊನೆಯಲ್ಲಿ'
        ]
        current_step = []
        for s in sentences:
            s_lower = s.lower()
            is_new_step = any(marker in s_lower for marker in step_markers)
            if is_new_step and current_step:
                steps.append(' '.join(current_step))
                current_step = [s]
            else:
                current_step.append(s)
        if current_step:
            steps.append(' '.join(current_step))

    # Method 3: Action verbs
    if len(steps) < 2:
        action_verbs = [
            'add', 'pour', 'mix', 'stir', 'boil', 'cook', 'heat', 'cut', 'chop',
            'open', 'click', 'go', 'select', 'press', 'type', 'save', 'put', 'take',
            'डालें', 'मिलाएं', 'पकाएं', 'काटें', 'खोलें',
            'ಸೇರಿಸಿ', 'ಬೆರೆಸಿ', 'ಬೇಯಿಸಿ', 'ಕತ್ತರಿಸಿ', 'ತೆರೆಯಿರಿ'
        ]
        for s in sentences:
            if any(verb in s.lower() for verb in action_verbs):
                if len(s) > 20:
                    steps.append(s)

    # Method 4: Split by common instructional transitions
    if len(steps) < 2:
        transitions = [' then ', ' next ', ' after that ', ' finally ', ' now ']
        for trans in transitions:
            if trans in text_lower:
                parts = text_lower.split(trans)
                for part in parts:
                    if len(part) > 20:
                        steps.append(part.strip().capitalize())
                break

    # Method 5: Take all meaningful sentences as steps
    if len(steps) < 2 and len(sentences) >= 2:
        for s in sentences:
            if len(s) > 25 and len(s.split()) >= 4:
                steps.append(s)

    # Clean steps
    cleaned = []
    for step in steps:
        step = step.strip()
        if step:
            step = step[0].upper() + step[1:] if len(step) > 1 else step
            if step and step[-1] not in '.!?':
                step += '.'
            cleaned.append(step)

    # Remove duplicates
    unique = []
    seen = set()
    for step in cleaned:
        key = step.lower()[:50]
        if key not in seen:
            seen.add(key)
            unique.append(step)

    # If still no steps, create from transcript (force as instructional)
    if len(unique) < 1 and len(text) > 50:
        # Split by periods and take first few as steps
        parts = re.split(r'\.\s+', text)
        for part in parts[:5]:
            if len(part) > 20:
                unique.append(part.strip().capitalize() + '.')

    logger.info(f"✅ Detected {len(unique)} steps")
    return unique[:10]


def generate_summary(text, steps=None):
    """Generate summary from text"""
    if not text:
        return "No content to summarize."

    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    if not sentences:
        return text[:200] if len(text) > 200 else text

    if steps and len(steps) > 0:
        return f"This video contains {len(steps)} steps.\n\n" + ". ".join(sentences[:2])

    return ". ".join(sentences[:2]) if len(sentences) >= 2 else sentences[0][:200]