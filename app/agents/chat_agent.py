import time

from google import genai

from app.utils.config import (
    GEMINI_API_KEY,
    PRIMARY_MODEL,
    FALLBACK_MODEL,
    MAX_RETRIES,
    RETRY_DELAY_SECONDS,
    ENABLE_FALLBACK_MODEL,
    ENABLE_AI_RETRY
)

from app.utils.cache_manager import (
    generate_cache_key,
    get_cache,
    set_cache
)


client = genai.Client(
    api_key=GEMINI_API_KEY
)


def build_chat_prompt(
    question,
    context
):

    return f"""
You are an autonomous AI media strategist working for MoveUp Media.

Responsibilities:
- analyze YouTube operational analytics
- detect performance patterns
- identify audience behavior trends
- recommend optimization strategies
- provide concise executive intelligence

Rules:
- use only provided analytics
- avoid hallucinations
- be concise
- analytical
- actionable
- business-oriented
- operationally focused

Question:
{question}

Analytics Context:
{context}

Response Structure:

1. Direct Answer

2. Key Insight

3. Strategic Recommendation

Maximum 250 words.
"""


def extract_response_text(response):

    try:

        if hasattr(response, "text"):

            if response.text:

                return response.text.strip()

        return (
            "No AI response generated."
        )

    except Exception:

        return (
            "Unable to parse AI response."
        )


def is_retryable_error(error):

    error_text = str(error).lower()

    retry_keywords = [
        "429",
        "503",
        "resource_exhausted",
        "quota",
        "unavailable",
        "overloaded",
        "timeout"
    ]

    return any(
        keyword in error_text
        for keyword in retry_keywords
    )


def generate_with_model(
    model_name,
    prompt
):

    response = client.models.generate_content(
        model=model_name,
        contents=prompt
    )

    return extract_response_text(
        response
    )


def generate_ai_response(prompt):

    models_to_try = [
        PRIMARY_MODEL
    ]

    if ENABLE_FALLBACK_MODEL:

        if FALLBACK_MODEL not in models_to_try:

            models_to_try.append(
                FALLBACK_MODEL
            )

    last_error = None

    for model_name in models_to_try:

        retries = (
            MAX_RETRIES
            if ENABLE_AI_RETRY
            else 1
        )

        for attempt in range(retries):

            try:

                return generate_with_model(
                    model_name,
                    prompt
                )

            except Exception as error:

                last_error = error

                if not is_retryable_error(
                    error
                ):

                    break

                if attempt < retries - 1:

                    wait_time = (
                        RETRY_DELAY_SECONDS
                        * (attempt + 1)
                    )

                    time.sleep(
                        wait_time
                    )

    return handle_ai_error(
        last_error
    )


def handle_ai_error(error):

    error_text = str(error)

    if "429" in error_text:

        return (
            "AI quota limit temporarily exceeded due to high usage volume. "
            "Please retry in a few moments."
        )

    if "503" in error_text:

        return (
            "AI service is currently experiencing unusually high demand. "
            "Please retry shortly."
        )

    if "resource_exhausted" in error_text.lower():

        return (
            "AI resources are temporarily exhausted. "
            "Please retry after some time."
        )

    return (
        f"AI Assistant Error: {error_text}"
    )


def ask_ai(
    question,
    context
):

    try:

        cache_key = generate_cache_key(
            "chat",
            question
        )

        cached_response = get_cache(
            cache_key
        )

        if cached_response:

            return cached_response

        prompt = build_chat_prompt(
            question,
            context
        )

        final_response = generate_ai_response(
            prompt
        )

        set_cache(
            cache_key,
            final_response,
            expiry=1800
        )

        return final_response

    except Exception as error:

        return handle_ai_error(
            error
        )