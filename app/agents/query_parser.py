import re


ORDINAL_PATTERNS = {
    "latest": 0,
    "newest": 0,
    "recent": 0,
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
        "better channel"
    ],

    "top_videos": [
        "best video",
        "top video",
        "highest performing",
        "strongest video"
    ],

    "underperforming_videos": [
        "worst video",
        "weakest video",
        "underperforming",
        "poor performance"
    ],

    "video_metrics": [
        "metrics",
        "views",
        "likes",
        "comments",
        "performance score",
        "engagement"
    ],

    "content_strategy": [
        "content strategy",
        "content themes",
        "what works best",
        "content type"
    ],

    "upload_consistency": [
        "upload consistency",
        "posting schedule",
        "upload frequency"
    ],

    "recommendations": [
        "recommendation",
        "improve",
        "optimize",
        "growth"
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

    return question.lower().strip()


def detect_intent(question):

    question = normalize_question(question)

    for intent, keywords in INTENT_KEYWORDS.items():

        for keyword in keywords:

            if keyword in question:

                return intent

    return "general_analysis"


def extract_video_position(question):

    question = normalize_question(question)

    for pattern, index in ORDINAL_PATTERNS.items():

        if pattern in question:

            return index

    digit_match = re.search(
        r"(\d+)(st|nd|rd|th)",
        question
    )

    if digit_match:

        return int(
            digit_match.group(1)
        ) - 1

    return None


def detect_relative_direction(question):

    question = normalize_question(question)

    if "last" in question:
        return "last"

    return "latest"


def extract_metric_focus(question):

    question = normalize_question(question)

    metrics = []

    for metric, keywords in METRIC_KEYWORDS.items():

        for keyword in keywords:

            if keyword in question:

                metrics.append(metric)

                break

    return metrics


def requires_video_lookup(question):

    question = normalize_question(question)

    lookup_keywords = [
        "video",
        "uploaded",
        "latest",
        "last",
        "3rd",
        "second",
        "first"
    ]

    return any(
        keyword in question
        for keyword in lookup_keywords
    )


def parse_user_query(question):

    return {
        "intent":
            detect_intent(question),

        "video_position":
            extract_video_position(question),

        "direction":
            detect_relative_direction(question),

        "metric_focus":
            extract_metric_focus(question),

        "requires_video_lookup":
            requires_video_lookup(question),

        "raw_question":
            question
    }