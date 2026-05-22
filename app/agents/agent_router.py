import json

from statistics import mean
from datetime import datetime

from app.agents.chat_agent import (
    ask_ai
)

from app.agents.query_parser import (
    parse_user_query
)

from app.utils.cache_manager import (
    generate_cache_key,
    get_cache,
    set_cache
)


def safe_float(value):

    try:

        return float(value)

    except Exception:

        return 0.0


def safe_int(value):

    try:

        return int(value)

    except Exception:

        return 0


def calculate_channel_summary(videos):

    if not videos:

        return {

            "total_views": 0,
            "average_views": 0,
            "average_engagement": 0,
            "average_performance_score": 0,
            "strong_videos": 0,
            "underperforming_videos": 0
        }

    total_views = sum(

        safe_int(
            video.get(
                "views",
                0
            )
        )

        for video in videos
    )

    average_views = round(

        mean([

            safe_int(
                video.get(
                    "views",
                    0
                )
            )

            for video in videos
        ]),
        2
    )

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

    average_performance = round(

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

    return {

        "total_views":
            total_views,

        "average_views":
            average_views,

        "average_engagement":
            average_engagement,

        "average_performance_score":
            average_performance,

        "strong_videos":
            strong_videos,

        "underperforming_videos":
            underperforming_videos
    }


def get_top_videos(
    videos,
    limit=3
):

    if not videos:

        return []

    return sorted(

        videos,

        key=lambda x:

        safe_float(
            x.get(
                "performance_score",
                0
            )
        ),

        reverse=True

    )[:limit]


def get_underperforming_videos(
    videos,
    limit=3
):

    if not videos:

        return []

    return sorted(

        videos,

        key=lambda x:

        safe_float(
            x.get(
                "performance_score",
                0
            )
        )

    )[:limit]


def parse_datetime(value):

    try:

        return datetime.fromisoformat(
            value.replace(
                "Z",
                "+00:00"
            )
        )

    except Exception:

        return datetime.min


def get_video_by_position(
    videos,
    position,
    direction="latest"
):

    if not videos:

        return None

    sorted_videos = sorted(

        videos,

        key=lambda x:

        parse_datetime(
            x.get(
                "published_at",
                ""
            )
        ),

        reverse=True
    )

    if direction == "last":

        sorted_videos = list(
            reversed(sorted_videos)
        )

    if (

        position is not None
        and
        0 <= position < len(sorted_videos)

    ):

        return sorted_videos[position]

    return sorted_videos[0]


def compress_video_data(
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


def build_compare_context(
    all_channel_data
):

    comparison_data = {}

    for channel_name, videos in all_channel_data.items():

        comparison_data[channel_name] = {

            "summary":
                calculate_channel_summary(
                    videos
                ),

            "top_videos":
                compress_video_data(
                    get_top_videos(videos)
                )
        }

    return comparison_data


def build_video_lookup_context(
    parsed_query,
    videos
):

    selected_video = get_video_by_position(

        videos,

        parsed_query.get(
            "video_position"
        ),

        parsed_query.get(
            "direction"
        )
    )

    return {

        "selected_video":
            selected_video,

        "metric_focus":
            parsed_query.get(
                "metric_focus",
                []
            )
    }


def build_top_videos_context(videos):

    return {

        "top_videos":
            compress_video_data(
                get_top_videos(videos)
            )
    }


def build_underperforming_context(videos):

    return {

        "underperforming_videos":
            compress_video_data(
                get_underperforming_videos(videos)
            )
    }


def build_engagement_context(videos):

    if not videos:

        return {}

    sorted_videos = sorted(

        videos,

        key=lambda x:

        safe_float(
            x.get(
                "engagement_rate",
                0
            )
        ),

        reverse=True
    )

    return {

        "highest_engagement":
            compress_video_data(
                sorted_videos[:3]
            ),

        "lowest_engagement":
            compress_video_data(
                sorted_videos[-3:]
            ),

        "average_engagement":
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
            )
    }


def build_content_strategy_context(videos):

    top_videos = get_top_videos(
        videos,
        limit=5
    )

    return {

        "top_titles": [

            video.get(
                "title",
                ""
            )

            for video in top_videos
        ],

        "top_video_data":
            compress_video_data(
                top_videos
            )
    }


def build_recommendation_context(videos):

    return {

        "strong_patterns":
            compress_video_data(
                get_top_videos(videos)
            ),

        "weak_patterns":
            compress_video_data(
                get_underperforming_videos(videos)
            )
    }


def build_summary_context(videos):

    return {

        "channel_summary":
            calculate_channel_summary(
                videos
            ),

        "top_videos":
            compress_video_data(
                get_top_videos(videos)
            )
    }


def build_upload_consistency_context(videos):

    return {

        "publish_dates": [

            video.get(
                "published_at",
                ""
            )

            for video in videos[:10]
        ],

        "total_uploads":
            len(videos)
    }


def generate_dynamic_context(
    parsed_query,
    selected_channel,
    selected_channel_data,
    all_channel_data
):

    try:

        intent = parsed_query.get(
            "intent"
        )

        if intent == "compare_channels":

            context = build_compare_context(
                all_channel_data
            )

        elif parsed_query.get(
            "requires_video_lookup"
        ):

            context = build_video_lookup_context(
                parsed_query,
                selected_channel_data
            )

        elif intent == "top_videos":

            context = build_top_videos_context(
                selected_channel_data
            )

        elif intent == "underperforming_videos":

            context = build_underperforming_context(
                selected_channel_data
            )

        elif intent == "engagement_analysis":

            context = build_engagement_context(
                selected_channel_data
            )

        elif intent == "content_strategy":

            context = build_content_strategy_context(
                selected_channel_data
            )

        elif intent == "recommendations":

            context = build_recommendation_context(
                selected_channel_data
            )

        elif intent == "upload_consistency":

            context = build_upload_consistency_context(
                selected_channel_data
            )

        else:

            context = build_summary_context(
                selected_channel_data
            )

        return {

            "channel_name":
                selected_channel,

            "analysis_type":
                intent,

            "generated_at":
                str(datetime.utcnow()),

            "context":
                context
        }

    except Exception as error:

        return {

            "channel_name":
                selected_channel,

            "analysis_type":
                "fallback_summary",

            "error":
                str(error),

            "context":
                build_summary_context(
                    selected_channel_data
                )
        }


def route_user_query(
    question,
    selected_channel,
    selected_channel_data,
    all_channel_data
):

    cache_key = generate_cache_key(

        "agent",

        f"{selected_channel}:{question}"
    )

    cached_response = get_cache(
        cache_key
    )

    if cached_response:

        return cached_response

    parsed_query = parse_user_query(
        question
    )

    dynamic_context = (

        generate_dynamic_context(

            parsed_query,
            selected_channel,
            selected_channel_data,
            all_channel_data
        )
    )

    context_payload = json.dumps(

        dynamic_context,

        indent=2,

        default=str
    )

    response = ask_ai(
        question,
        context_payload
    )

    final_response = {

        "intent":
            parsed_query.get(
                "intent"
            ),

        "parsed_query":
            parsed_query,

        "response":
            response
    }

    set_cache(

        cache_key,

        final_response,

        expiry=600
    )

    return final_response