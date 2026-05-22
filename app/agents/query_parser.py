import re


COMMON_TYPOS = {

    "engagment": "engagement",
    "perfromance": "performance",
    "comparision": "comparison",
    "analitics": "analytics",
    "stratergy": "strategy",
    "vedio": "video"
}


ORDINAL_PATTERNS = {

    "latest": 0,
    "newest": 0,
    "recent": 0,
    "most recent": 0,

    "first": 0,
    "1st": 0,

    "second": 1,
    "2nd": 1,

    "third": 2,
    "3rd": 2,

    "fourth": 3,
    "4th": 3,

    "fifth": 4,
    "5th": 4
}


INTENT_KEYWORDS = {

    "compare_channels": [

        "compare",
        "comparison",
        "versus",
        "vs",
        "better channel",
        "benchmark"
    ],

    "top_videos": [

        "best video",
        "top video",
        "highest performing",
        "strongest video",
        "viral video"
    ],

    "underperforming_videos": [

        "worst video",
        "weakest video",
        "underperforming",
        "poor performance",
        "low performance"
    ],

    "video_metrics": [

        "metrics",
        "views",
        "likes",
        "comments",
        "performance score",
        "engagement",
        "ctr",
        "retention"
    ],

    "engagement_analysis": [

        "engagement",
        "audience interaction",
        "retention",
        "watch time"
    ],

    "trend_analysis": [

        "trend",
        "trending",
        "momentum",
        "growth pattern"
    ],

    "audience_behavior": [

        "audience",
        "viewer behavior",
        "retention drop"
    ],

    "content_strategy": [

        "content strategy",
        "content themes",
        "what works best",
        "content type",
        "content direction"
    ],

    "upload_consistency": [

        "upload consistency",
        "posting schedule",
        "upload frequency",
        "consistency"
    ],

    "growth_opportunities": [

        "growth",
        "opportunity",
        "scaling",
        "expand"
    ],

    "recommendations": [

        "recommendation",
        "improve",
        "optimize",
        "strategy",
        "suggestion"
    ]
}


METRIC_KEYWORDS = {

    "views": [
        "views"
    ],

    "likes": [
        "likes"
    ],

    "comments": [
        "comments"
    ],

    "engagement_rate": [
        "engagement"
    ],

    "performance_score": [
        "performance",
        "score"
    ],

    "ctr": [
        "ctr"
    ],

    "retention": [
        "retention"
    ]
}


def normalize_question(question):

    question = str(question).lower().strip()

    for typo, correction in COMMON_TYPOS.items():

        question = question.replace(
            typo,
            correction
        )

    question = re.sub(
        r"\s+",
        " ",
        question
    )

    return question


def keyword_exists(
    keyword,
    question
):

    return bool(

        re.search(
            rf"\b{re.escape(keyword)}\b",
            question
        )
    )


def detect_intent(question):

    question = normalize_question(
        question
    )

    intent_scores = {}

    for intent, keywords in INTENT_KEYWORDS.items():

        score = 0

        for keyword in keywords:

            if keyword_exists(
                keyword,
                question
            ):

                score += 1

        if score > 0:

            intent_scores[intent] = score

    if not intent_scores:

        return "general_analysis"

    return max(
        intent_scores,
        key=intent_scores.get
    )


def extract_video_position(question):

    question = normalize_question(
        question
    )

    for pattern, index in ORDINAL_PATTERNS.items():

        if keyword_exists(
            pattern,
            question
        ):

            return index

    digit_match = re.search(
        r"(\d+)(st|nd|rd|th)",
        question
    )

    if digit_match:

        try:

            return (
                int(
                    digit_match.group(1)
                ) - 1
            )

        except Exception:

            return None

    return None


def detect_relative_direction(question):

    question = normalize_question(
        question
    )

    if any(

        keyword_exists(
            keyword,
            question
        )

        for keyword in [
            "last",
            "oldest",
            "earliest"
        ]
    ):

        return "last"

    return "latest"


def extract_metric_focus(question):

    question = normalize_question(
        question
    )

    metrics = []

    for metric, keywords in METRIC_KEYWORDS.items():

        for keyword in keywords:

            if keyword_exists(
                keyword,
                question
            ):

                metrics.append(metric)

                break

    return metrics


def requires_video_lookup(question):

    question = normalize_question(
        question
    )

    lookup_keywords = [

        "video",
        "uploaded",
        "latest",
        "last",
        "newest",
        "recent",
        "first",
        "second",
        "third",
        "4th",
        "5th"
    ]

    return any(

        keyword_exists(
            keyword,
            question
        )

        for keyword in lookup_keywords
    )


def detect_query_complexity(question):

    question = normalize_question(
        question
    )

    word_count = len(
        question.split()
    )

    if word_count >= 20:

        return "high"

    if word_count >= 10:

        return "medium"

    return "low"


def parse_user_query(question):

    normalized_question = normalize_question(
        question
    )

    parsed_data = {

        "intent":
            detect_intent(
                normalized_question
            ),

        "video_position":
            extract_video_position(
                normalized_question
            ),

        "direction":
            detect_relative_direction(
                normalized_question
            ),

        "metric_focus":
            extract_metric_focus(
                normalized_question
            ),

        "requires_video_lookup":
            requires_video_lookup(
                normalized_question
            ),

        "query_complexity":
            detect_query_complexity(
                normalized_question
            ),

        "normalized_question":
            normalized_question,

        "raw_question":
            question
    }

    return parsed_data