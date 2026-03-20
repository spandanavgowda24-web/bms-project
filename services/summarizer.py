from transformers import pipeline

# Load summarization model
summarizer_model = pipeline(
    "text-generation",
    model="google/flan-t5-small"
)

def generate_summary(text):

    try:

        if not text or len(text.strip()) == 0:
            return "No speech detected in the media."

        # Create summarization prompt
        prompt = "Summarize the following tutorial clearly:\n" + text

        result = summarizer_model(
            prompt,
            max_length=512,   # allow large summary
            do_sample=False
        )

        summary = result[0]["generated_text"]

        return summary.strip()

    except Exception as e:

        print("Summary generation error:", e)

        # fallback → return full text if model fails
        return text