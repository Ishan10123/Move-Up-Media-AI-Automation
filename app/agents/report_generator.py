import time

from statistics import mean

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


def safe_float(value):

    try:

        return float(value)

    except Exception:

        return 0.0


def calculate_channel_aggregates(videos):

    if not videos:

        return {}

    return {

        "total_videos":
            len(videos),

        "total_views":
            sum([
                int(
                    video.get(
                        "views",
                        0
                    )
                )
                for video in videos
            ]),

        "average_views":
            round(
                mean([
                    safe_float(
                        video.get(
                            "views",
                            0
                        )
                    )
                    for video in videos
                ]),
                2
            ),

        "average_engagement_rate":
            round(
                mean([
                    safe_float(
                        video.get(
                            "engagement_rate",
                            0
                        )
                    )
                    for video in videos
                ]),
                2
            ),

        "average_performance_score":
            round(
                mean([
                    safe_float(
                        video.get(
                            "performance_score",
                            0
                        )
                    )
                    for video in videos
                ]),
                2
            )
    }


def get_top_videos(
    videos,
    limit=3
):

    return sorted(
        videos,
        key=lambda x:
        x.get(
            "performance_score",
            0
        ),
        reverse=True
    )[:limit]


def get_bottom_videos(
    videos,
    limit=3
):

    return sorted(
        videos,
        key=lambda x:
        x.get(
            "performance_score",
            0
        )
    )[:limit]


def build_report_prompt(
    channel_name,
    videos
):

    aggregates = calculate_channel_aggregates(
        videos
    )

    top_videos = get_top_videos(
        videos
    )

    bottom_videos = get_bottom_videos(
        videos
    )

    return f"""
You are a senior AI media strategist and operational intelligence analyst at MoveUp Media.

Generate an executive YouTube operational intelligence report.

Channel Name:
{channel_name}

Aggregate Metrics:
{aggregates}

Top Performing Videos:
{top_videos}

Weakest Videos:
{bottom_videos}

Analytics Dataset:
{videos}

Requirements:
- concise
- operational
- business-focused
- analytical
- actionable
- avoid hallucinations
- avoid markdown symbols
- maximum 600 words

Required Sections:

1. Executive Summary

2. Strongest Performing Videos

3. Underperforming Videos

4. Engagement Analysis

5. Content Trends

6. Strategic Recommendations

7. Next Week Priority Actions
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
            "AI report generation returned an empty response."
        )

    except Exception:

        return (
            "Unable to parse AI report."
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


def generate_ai_report(prompt):

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
                        f"[AI REPORT ERROR] "
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
            "AI report generation quota temporarily exceeded across active API pools. "
            "Please retry shortly."
        )

    if (
        "503" in error_text
        or
        "unavailable" in error_text.lower()
    ):

        return (
            "AI reporting service is temporarily overloaded. "
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
        f"Report Generation Error: {error_text}"
    )


def generate_channel_report(
    channel_name,
    videos
):

    try:

        cache_key = generate_cache_key(
            "report",
            channel_name
        )

        cached_report = get_cache(
            cache_key
        )

        if cached_report:

            return cached_report

        prompt = build_report_prompt(
            channel_name,
            videos
        )

        final_response = generate_ai_report(
            prompt
        )

        set_cache(
            cache_key,
            final_response,
            expiry=3600
        )

        return final_response

    except Exception as error:

        print(
            f"[REPORT_GENERATOR_FATAL] {str(error)}"
        )

        return handle_ai_error(
            error
        )