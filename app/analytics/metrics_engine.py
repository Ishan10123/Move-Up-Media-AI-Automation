import math

from datetime import datetime
from datetime import timezone

from statistics import mean


PROCESSING_ENGINE_VERSION = "2.0.0"


def safe_int(value):

    try:

        if value is None:

            return 0

        return int(float(value))

    except Exception:

        return 0


def safe_float(value):

    try:

        if value is None:

            return 0.0

        return float(value)

    except Exception:

        return 0.0


def safe_round(
    value,
    digits=2
):

    try:

        return round(
            safe_float(value),
            digits
        )

    except Exception:

        return 0.0


def calculate_engagement_rate(
    views,
    likes,
    comments
):

    views = safe_int(views)

    likes = safe_int(likes)

    comments = safe_int(comments)

    if views <= 0:

        return 0.0

    weighted_engagement = (
        (likes * 1)
        +
        (comments * 3)
    )

    engagement_rate = (
        weighted_engagement / views
    ) * 100

    return safe_round(
        engagement_rate
    )


def calculate_views_per_day(
    views,
    published_at
):

    views = safe_int(views)

    if views <= 0:

        return 0.0

    try:

        published_date = datetime.fromisoformat(
            str(published_at).replace(
                "Z",
                "+00:00"
            )
        )

    except Exception:

        return 0.0

    current_date = datetime.now(
        timezone.utc
    )

    total_seconds = (
        current_date - published_date
    ).total_seconds()

    days_live = max(
        total_seconds / 86400,
        1
    )

    views_per_day = (
        views / days_live
    )

    views_per_day = min(
        views_per_day,
        1000000
    )

    return safe_round(
        views_per_day
    )


def calculate_like_ratio(
    views,
    likes
):

    views = safe_int(views)

    likes = safe_int(likes)

    if views <= 0:

        return 0.0

    return safe_round(
        (likes / views) * 100
    )


def calculate_comment_ratio(
    views,
    comments
):

    views = safe_int(views)

    comments = safe_int(comments)

    if views <= 0:

        return 0.0

    return safe_round(
        (comments / views) * 100
    )


def calculate_engagement_quality(
    engagement_rate,
    comment_ratio
):

    quality_score = (
        (engagement_rate * 0.7)
        +
        (comment_ratio * 0.3)
    )

    if quality_score >= 12:

        return "Exceptional"

    if quality_score >= 7:

        return "Strong"

    if quality_score >= 4:

        return "Average"

    return "Weak"


def calculate_growth_velocity(
    views_per_day
):

    if views_per_day >= 50000:

        return "Explosive Growth"

    if views_per_day >= 10000:

        return "High Growth"

    if views_per_day >= 3000:

        return "Moderate Growth"

    return "Low Growth"


def calculate_estimated_ctr_signal(
    engagement_rate,
    views_per_day,
    like_ratio
):

    normalized_views = min(
        math.log10(
            views_per_day + 1
        ) * 2,
        10
    )

    ctr_score = (
        (engagement_rate * 0.5)
        +
        (normalized_views * 0.3)
        +
        (like_ratio * 0.2)
    )

    if ctr_score >= 8:

        return "High CTR Probability"

    if ctr_score >= 5:

        return "Moderate CTR Probability"

    return "Low CTR Probability"


def calculate_estimated_retention_signal(
    engagement_rate,
    comment_ratio,
    like_ratio
):

    retention_score = (
        (engagement_rate * 0.5)
        +
        (comment_ratio * 0.3)
        +
        (like_ratio * 0.2)
    )

    if retention_score >= 8:

        return "Strong Retention"

    if retention_score >= 5:

        return "Moderate Retention"

    return "Weak Retention"


def calculate_momentum_score(
    engagement_rate,
    views_per_day,
    like_ratio
):

    normalized_views = min(
        math.log10(
            views_per_day + 1
        ) * 2,
        10
    )

    momentum_score = (
        (engagement_rate * 0.4)
        +
        (normalized_views * 0.4)
        +
        (like_ratio * 0.2)
    )

    return safe_round(
        momentum_score
    )


def classify_momentum(momentum_score):

    if momentum_score >= 8:

        return "Viral Momentum"

    if momentum_score >= 5:

        return "Growing Momentum"

    return "Low Momentum"


def calculate_audience_signal_strength(
    engagement_rate,
    comment_ratio,
    like_ratio
):

    audience_signal = (
        (engagement_rate * 0.5)
        +
        (comment_ratio * 0.3)
        +
        (like_ratio * 0.2)
    )

    if audience_signal >= 8:

        return "High Audience Resonance"

    if audience_signal >= 5:

        return "Moderate Audience Resonance"

    return "Weak Audience Resonance"


def calculate_content_efficiency(
    views_per_day,
    engagement_rate
):

    normalized_views = min(
        math.log10(
            views_per_day + 1
        ) * 2,
        10
    )

    efficiency_score = (
        (normalized_views * 0.6)
        +
        (engagement_rate * 0.4)
    )

    return safe_round(
        efficiency_score
    )


def calculate_performance_score(video):

    views = safe_int(
        video.get(
            "views",
            0
        )
    )

    likes = safe_int(
        video.get(
            "likes",
            0
        )
    )

    comments = safe_int(
        video.get(
            "comments",
            0
        )
    )

    published_at = video.get(
        "published_at",
        ""
    )

    engagement_rate = calculate_engagement_rate(
        views,
        likes,
        comments
    )

    views_per_day = calculate_views_per_day(
        views,
        published_at
    )

    like_ratio = calculate_like_ratio(
        views,
        likes
    )

    comment_ratio = calculate_comment_ratio(
        views,
        comments
    )

    normalized_views = min(
        math.log10(
            views_per_day + 1
        ) * 2,
        10
    )

    score = (
        (engagement_rate * 0.35)
        +
        (normalized_views * 0.35)
        +
        (like_ratio * 0.20)
        +
        (comment_ratio * 0.10)
    )

    return safe_round(
        score
    )


def classify_video(score):

    if score >= 7:

        return "Strong"

    if score >= 4:

        return "Average"

    return "Underperforming"


def generate_video_summary(video):

    return (

        f"{video.get('title', 'Unknown Video')} achieved "

        f"{video.get('views', 0)} views with "

        f"{video.get('engagement_rate', 0)}% engagement. "

        f"The content shows "

        f"{video.get('growth_velocity', 'Unknown Growth')} "

        f"with "

        f"{video.get('estimated_retention_signal', 'Unknown Retention')}."
    )


def calculate_channel_health_score(videos):

    if not videos:

        return 0.0

    performance_scores = [

        safe_float(
            video.get(
                "performance_score",
                0
            )
        )

        for video in videos
    ]

    return safe_round(
        mean(performance_scores)
    )


def classify_channel_health(score):

    if score >= 7:

        return "High Performing"

    if score >= 4:

        return "Stable"

    return "Needs Optimization"


def generate_channel_summary(videos):

    if not videos:

        return {

            "total_videos": 0,
            "total_views": 0,
            "average_engagement": 0,
            "average_performance_score": 0,
            "strong_videos": 0,
            "underperforming_videos": 0,
            "channel_health_score": 0,
            "channel_health": "No Data"
        }

    total_views = sum([

        safe_int(
            video.get(
                "views",
                0
            )
        )

        for video in videos
    ])

    average_engagement = safe_round(

        mean([

            safe_float(
                video.get(
                    "engagement_rate",
                    0
                )
            )

            for video in videos
        ])
    )

    average_score = safe_round(

        mean([

            safe_float(
                video.get(
                    "performance_score",
                    0
                )
            )

            for video in videos
        ])
    )

    strong_videos = len([

        video

        for video in videos

        if video.get(
            "classification"
        ) == "Strong"
    ])

    underperforming_videos = len([

        video

        for video in videos

        if video.get(
            "classification"
        ) == "Underperforming"
    ])

    health_score = calculate_channel_health_score(
        videos
    )

    return {

        "total_videos":
            len(videos),

        "total_views":
            total_views,

        "average_engagement":
            average_engagement,

        "average_performance_score":
            average_score,

        "strong_videos":
            strong_videos,

        "underperforming_videos":
            underperforming_videos,

        "channel_health_score":
            health_score,

        "channel_health":
            classify_channel_health(
                health_score
            )
    }


def compress_ai_context(
    videos,
    limit=5
):

    compressed = []

    for video in videos[:limit]:

        compressed.append({

            "title":
                video.get(
                    "title"
                ),

            "views":
                video.get(
                    "views"
                ),

            "engagement_rate":
                video.get(
                    "engagement_rate"
                ),

            "performance_score":
                video.get(
                    "performance_score"
                ),

            "classification":
                video.get(
                    "classification"
                )
        })

    return compressed


def enrich_video_metrics(videos):

    enriched_videos = []

    if not videos:

        return enriched_videos

    for video in videos:

        try:

            views = safe_int(
                video.get(
                    "views",
                    0
                )
            )

            likes = safe_int(
                video.get(
                    "likes",
                    0
                )
            )

            comments = safe_int(
                video.get(
                    "comments",
                    0
                )
            )

            published_at = video.get(
                "published_at",
                ""
            )

            engagement_rate = calculate_engagement_rate(
                views,
                likes,
                comments
            )

            views_per_day = calculate_views_per_day(
                views,
                published_at
            )

            like_ratio = calculate_like_ratio(
                views,
                likes
            )

            comment_ratio = calculate_comment_ratio(
                views,
                comments
            )

            performance_score = calculate_performance_score(
                video
            )

            classification = classify_video(
                performance_score
            )

            estimated_ctr_signal = (
                calculate_estimated_ctr_signal(
                    engagement_rate,
                    views_per_day,
                    like_ratio
                )
            )

            estimated_retention_signal = (
                calculate_estimated_retention_signal(
                    engagement_rate,
                    comment_ratio,
                    like_ratio
                )
            )

            engagement_quality = (
                calculate_engagement_quality(
                    engagement_rate,
                    comment_ratio
                )
            )

            growth_velocity = (
                calculate_growth_velocity(
                    views_per_day
                )
            )

            momentum_score = (
                calculate_momentum_score(
                    engagement_rate,
                    views_per_day,
                    like_ratio
                )
            )

            momentum_classification = (
                classify_momentum(
                    momentum_score
                )
            )

            audience_signal_strength = (
                calculate_audience_signal_strength(
                    engagement_rate,
                    comment_ratio,
                    like_ratio
                )
            )

            content_efficiency = (
                calculate_content_efficiency(
                    views_per_day,
                    engagement_rate
                )
            )

            enriched_video = {

                **video,

                "engagement_rate":
                    engagement_rate,

                "views_per_day":
                    views_per_day,

                "like_ratio":
                    like_ratio,

                "comment_ratio":
                    comment_ratio,

                "performance_score":
                    performance_score,

                "classification":
                    classification,

                "estimated_ctr_signal":
                    estimated_ctr_signal,

                "estimated_retention_signal":
                    estimated_retention_signal,

                "engagement_quality":
                    engagement_quality,

                "growth_velocity":
                    growth_velocity,

                "momentum_score":
                    momentum_score,

                "momentum_classification":
                    momentum_classification,

                "audience_signal_strength":
                    audience_signal_strength,

                "content_efficiency":
                    content_efficiency,

                "processing_version":
                    PROCESSING_ENGINE_VERSION,

                "analysis_timestamp":
                    str(
                        datetime.now(
                            timezone.utc
                        )
                    )
            }

            enriched_video[
                "summary"
            ] = generate_video_summary(
                enriched_video
            )

            enriched_videos.append(
                enriched_video
            )

        except Exception as error:

            print(
                f"[Metrics Engine Error] {str(error)}"
            )

            continue

    return enriched_videos