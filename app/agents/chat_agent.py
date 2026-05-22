import time

from google import genai

from app.utils.config import (
    GEMINI_API_KEYS,
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


def create_client(api_key):

    return genai.Client(
        api_key=api_key
    )


def build_chat_prompt(
    question,
    context
):

    return f"""
You are an autonomous AI media strategist working for MoveUp Media.

Responsibilities:
- analyze YouTube operational analytics
- identify audience behavior patterns
- detect content momentum
- recommend operational improvements
- provide executive intelligence

Rules:
- use only provided analytics
- avoid hallucinations
- concise responses only
- business-oriented
- analytical
- actionable

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

        if hasattr(response, "candidates"):

            candidates = response.candidates

            if candidates:

                content = (
                    candidates[0]
                    .content
                    .parts[0]
                    .text
                )

                if content:

                    return content.strip()

        return (
            "AI assistant could not generate a response."
        )

    except Exception:

        return (
            "Unable to parse AI response."
        )


def is_retryable_error(error):

    error_text = str(error).lower()

    retryable_keywords = [
        "429",
        "503",
        "quota",
        "resource_exhausted",
        "unavailable",
        "overloaded",
        "timeout",
        "internal"
    ]

    return any(
        keyword in error_text
        for keyword in retryable_keywords
    )


def generate_with_client(
    client,
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

    for api_key in GEMINI_API_KEYS:

        client = create_client(
            api_key
        )

        for model_name in models_to_try:

            retries = (
                MAX_RETRIES
                if ENABLE_AI_RETRY
                else 1
            )

            for attempt in range(retries):

                try:

                    response = generate_with_client(
                        client,
                        model_name,
                        prompt
                    )

                    if response:

                        return response

                except Exception as error:

                    last_error = error

                    print(
                        f"[AI CHAT ERROR] "
                        f"Model={model_name} "
                        f"Attempt={attempt + 1} "
                        f"Error={str(error)}"
                    )

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

                    continue

    return handle_ai_error(
        last_error
    )


def handle_ai_error(error):

    error_text = str(error)

    if (
        "429" in error_text
        or
        "quota" in error_text.lower()
    ):

        return (
            "AI quota limit temporarily exceeded across active API pools. "
            "Please retry shortly."
        )

    if (
        "503" in error_text
        or
        "unavailable" in error_text.lower()
    ):

        return (
            "AI assistant service is temporarily overloaded. "
            "Please retry in a few moments."
        )

    if (
        "resource_exhausted"
        in error_text.lower()
    ):

        return (
            "AI infrastructure resources are temporarily exhausted. "
            "Please retry shortly."
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

        print(
            f"[CHAT_AGENT_FATAL] {str(error)}"
        )

        return handle_ai_error(
            error
        )