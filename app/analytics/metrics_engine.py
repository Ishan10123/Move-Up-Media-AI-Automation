from datetime import datetime, timezone
from statistics import mean


def safe_int(value):

    try:

        return int(value)

    except:

        return 0


def safe_float(value):

    try:

        return float(value)

    except:

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

        return 0

    engagement_rate = (
        (likes + comments) / views
    ) * 100

    return round(
        engagement_rate,
        2
    )


def calculate_views_per_day(
    views,
    published_at
):

    views = safe_int(views)

    try:

        published_date = datetime.fromisoformat(
            published_at.replace(
                "Z",
                "+00:00"
            )
        )

    except:

        return 0

    current_date = datetime.now(
        timezone.utc
    )

    days_live = (
        current_date - published_date
    ).days

    if days_live <= 0:

        days_live = 1

    return round(
        views / days_live,
        2
    )


def calculate_like_ratio(
    views,
    likes
):

    views = safe_int(views)
    likes = safe_int(likes)

    if views <= 0:

        return 0

    return round(
        (likes / views) * 100,
        2
    )


def calculate_comment_ratio(
    views,
    comments
):

    views = safe_int(views)
    comments = safe_int(comments)

    if views <= 0:

        return 0

    return round(
        (comments / views) * 100,
        2
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

    if quality_score >= 10:

        return "Exceptional"

    elif quality_score >= 7:

        return "Strong"

    elif quality_score >= 4:

        return "Average"

    return "Weak"


def calculate_growth_velocity(
    views_per_day
):

    if views_per_day >= 10000:

        return "Explosive Growth"

    elif views_per_day >= 5000:

        return "High Growth"

    elif views_per_day >= 1000:

        return "Moderate Growth"

    return "Low Growth"


def calculate_estimated_ctr_signal(
    engagement_rate,
    views_per_day,
    like_ratio
):

    ctr_score = (
        (engagement_rate * 0.5)
        +
        (
            min(
                views_per_day / 1000,
                10
            ) * 0.3
        )
        +
        (like_ratio * 0.2)
    )

    if ctr_score >= 8:

        return "High CTR Probability"

    elif ctr_score >= 5:

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

    elif retention_score >= 5:

        return "Moderate Retention"

    return "Weak Retention"


def calculate_momentum_score(
    engagement_rate,
    views_per_day,
    like_ratio
):

    momentum_score = (
        (engagement_rate * 0.4)
        +
        (
            min(
                views_per_day / 1000,
                10
            ) * 0.4
        )
        +
        (like_ratio * 0.2)
    )

    return round(
        momentum_score,
        2
    )


def classify_momentum(momentum_score):

    if momentum_score >= 8:

        return "Viral Momentum"

    elif momentum_score >= 5:

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

    elif audience_signal >= 5:

        return "Moderate Audience Resonance"

    return "Weak Audience Resonance"


def calculate_content_efficiency(
    views_per_day,
    engagement_rate
):

    efficiency_score = (
        (
            min(
                views_per_day / 1000,
                10
            )
        ) * 0.6
        +
        (engagement_rate * 0.4)
    )

    return round(
        efficiency_score,
        2
    )


def calculate_performance_score(video):

    engagement_rate = calculate_engagement_rate(
        video["views"],
        video["likes"],
        video["comments"]
    )

    views_per_day = calculate_views_per_day(
        video["views"],
        video["published_at"]
    )

    like_ratio = calculate_like_ratio(
        video["views"],
        video["likes"]
    )

    comment_ratio = calculate_comment_ratio(
        video["views"],
        video["comments"]
    )

    normalized_views = min(
        views_per_day / 1000,
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

    return round(
        score,
        2
    )


def classify_video(score):

    if score >= 8:

        return "Strong"

    elif score >= 4:

        return "Average"

    return "Underperforming"


def generate_video_summary(video):

    return (
        f"{video['title']} achieved "
        f"{video['views']} views with "
        f"{video['engagement_rate']}% engagement. "
        f"The video is classified as "
        f"{video['classification']} with "
        f"{video['growth_velocity']} and "
        f"{video['estimated_retention_signal']}."
    )


def calculate_channel_health_score(videos):

    if not videos:

        return 0

    performance_scores = [
        safe_float(
            video.get(
                "performance_score",
                0
            )
        )
        for video in videos
    ]

    return round(
        mean(performance_scores),
        2
    )


def classify_channel_health(score):

    if score >= 8:

        return "High Performing"

    elif score >= 5:

        return "Stable"

    return "Needs Optimization"


def generate_channel_summary(videos):

    if not videos:

        return {}

    total_views = sum([
        safe_int(
            video.get(
                "views",
                0
            )
        )
        for video in videos
    ])

    average_engagement = round(
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
    )

    average_score = round(
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


def enrich_video_metrics(videos):

    enriched_videos = []

    for video in videos:

        engagement_rate = calculate_engagement_rate(
            video["views"],
            video["likes"],
            video["comments"]
        )

        views_per_day = calculate_views_per_day(
            video["views"],
            video["published_at"]
        )

        like_ratio = calculate_like_ratio(
            video["views"],
            video["likes"]
        )

        comment_ratio = calculate_comment_ratio(
            video["views"],
            video["comments"]
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
                content_efficiency
        }

        enriched_video[
            "summary"
        ] = generate_video_summary(
            enriched_video
        )

        enriched_videos.append(
            enriched_video
        )

    return enriched_videos