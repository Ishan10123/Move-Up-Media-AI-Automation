from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.utils.config import (
    YOUTUBE_API_KEY
)

from app.utils.cache_manager import (
    generate_cache_key,
    get_cache,
    set_cache
)


youtube = build(
    "youtube",
    "v3",
    developerKey=YOUTUBE_API_KEY
)


CHANNELS = {
    "Netflu": "@Netflu",
    "ThePlayoffsTV": "@ThePlayoffsTV"
}


COMPETITOR_CHANNELS = {
    "ESPN Brasil": "@espnbrasil",
    "TNT Sports Brasil": "@TNTSportsBR",
    "NBA Brasil": "@NBABrasil"
}


def safe_int(value):

    try:

        return int(value)

    except:

        return 0


def safe_get(
    dictionary,
    keys,
    default=None
):

    try:

        current = dictionary

        for key in keys:

            current = current[key]

        return current

    except Exception:

        return default


def log_service_message(message):

    print(
        f"[YouTube Service] {message}"
    )


def build_youtube_client():

    return build(
        "youtube",
        "v3",
        developerKey=YOUTUBE_API_KEY
    )


def get_channel_id(handle):

    cache_key = generate_cache_key(
        "channel_id",
        handle
    )

    cached_channel_id = get_cache(
        cache_key
    )

    if cached_channel_id:

        return cached_channel_id

    try:

        response = youtube.search().list(
            part="snippet",
            q=handle,
            type="channel",
            maxResults=1
        ).execute()

        items = response.get(
            "items",
            []
        )

        if not items:

            log_service_message(
                f"No channel found for {handle}"
            )

            return None

        channel_id = safe_get(
            items[0],
            [
                "snippet",
                "channelId"
            ]
        )

        set_cache(
            cache_key,
            channel_id,
            expiry=3600
        )

        return channel_id

    except HttpError as error:

        log_service_message(
            f"YouTube API Error: {error}"
        )

        return None

    except Exception as error:

        log_service_message(
            f"Unexpected Channel ID Error: {error}"
        )

        return None


def get_channel_statistics(channel_id):

    cache_key = generate_cache_key(
        "channel_stats",
        channel_id
    )

    cached_data = get_cache(
        cache_key
    )

    if cached_data:

        return cached_data

    try:

        response = youtube.channels().list(
            part="statistics,snippet",
            id=channel_id
        ).execute()

        items = response.get(
            "items",
            []
        )

        if not items:

            return {}

        item = items[0]

        statistics = item.get(
            "statistics",
            {}
        )

        snippet = item.get(
            "snippet",
            {}
        )

        result = {
            "channel_title":
                snippet.get(
                    "title",
                    "Unknown Channel"
                ),

            "description":
                snippet.get(
                    "description",
                    ""
                ),

            "country":
                snippet.get(
                    "country",
                    "Unknown"
                ),

            "subscribers":
                safe_int(
                    statistics.get(
                        "subscriberCount",
                        0
                    )
                ),

            "total_views":
                safe_int(
                    statistics.get(
                        "viewCount",
                        0
                    )
                ),

            "total_videos":
                safe_int(
                    statistics.get(
                        "videoCount",
                        0
                    )
                )
        }

        set_cache(
            cache_key,
            result,
            expiry=1800
        )

        return result

    except Exception as error:

        log_service_message(
            f"Channel Statistics Error: {error}"
        )

        return {}


def get_video_statistics(video_id):

    cache_key = generate_cache_key(
        "video_stats",
        video_id
    )

    cached_data = get_cache(
        cache_key
    )

    if cached_data:

        return cached_data

    try:

        response = youtube.videos().list(
            part="statistics,contentDetails,snippet",
            id=video_id
        ).execute()

        items = response.get(
            "items",
            []
        )

        if not items:

            return {}

        item = items[0]

        set_cache(
            cache_key,
            item,
            expiry=1800
        )

        return item

    except Exception as error:

        log_service_message(
            f"Video Statistics Error: {error}"
        )

        return {}


def normalize_video_data(
    item,
    stats_item
):

    statistics = stats_item.get(
        "statistics",
        {}
    )

    content_details = stats_item.get(
        "contentDetails",
        {}
    )

    snippet = item.get(
        "snippet",
        {}
    )

    video_id = safe_get(
        item,
        [
            "id",
            "videoId"
        ]
    )

    return {
        "video_id":
            video_id,

        "title":
            snippet.get(
                "title",
                "Unknown Title"
            ),

        "description":
            snippet.get(
                "description",
                ""
            ),

        "published_at":
            snippet.get(
                "publishedAt",
                ""
            ),

        "thumbnail":
            safe_get(
                snippet,
                [
                    "thumbnails",
                    "high",
                    "url"
                ],
                ""
            ),

        "views":
            safe_int(
                statistics.get(
                    "viewCount",
                    0
                )
            ),

        "likes":
            safe_int(
                statistics.get(
                    "likeCount",
                    0
                )
            ),

        "comments":
            safe_int(
                statistics.get(
                    "commentCount",
                    0
                )
            ),

        "duration":
            content_details.get(
                "duration",
                "N/A"
            ),

        "video_url":
            f"https://youtube.com/watch?v={video_id}"
    }


def get_latest_videos(
    channel_id,
    max_results=10
):

    if not channel_id:

        return []

    cache_key = generate_cache_key(
        "latest_videos",
        f"{channel_id}_{max_results}"
    )

    cached_videos = get_cache(
        cache_key
    )

    if cached_videos:

        return cached_videos

    try:

        response = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            order="date",
            type="video",
            maxResults=max_results
        ).execute()

    except Exception as error:

        log_service_message(
            f"Video Fetch Error: {error}"
        )

        return []

    videos = []

    for item in response.get(
        "items",
        []
    ):

        try:

            video_id = safe_get(
                item,
                [
                    "id",
                    "videoId"
                ]
            )

            if not video_id:

                continue

            stats_item = get_video_statistics(
                video_id
            )

            normalized_video = (
                normalize_video_data(
                    item,
                    stats_item
                )
            )

            videos.append(
                normalized_video
            )

        except Exception as error:

            log_service_message(
                f"Video Processing Error: {error}"
            )

    set_cache(
        cache_key,
        videos,
        expiry=900
    )

    return videos


def get_video_by_position(
    videos,
    position=0
):

    if not videos:

        return None

    sorted_videos = sorted(
        videos,
        key=lambda x:
        x.get(
            "published_at",
            ""
        ),
        reverse=True
    )

    if (
        position < 0
        or position >= len(sorted_videos)
    ):

        return sorted_videos[0]

    return sorted_videos[position]


def get_top_performing_video(videos):

    if not videos:

        return None

    return max(
        videos,
        key=lambda x:
        x.get(
            "performance_score",
            0
        )
    )


def get_underperforming_video(videos):

    if not videos:

        return None

    return min(
        videos,
        key=lambda x:
        x.get(
            "performance_score",
            0
        )
    )


def get_channel_complete_data(
    channel_name,
    handle,
    max_results=10
):

    try:

        channel_id = get_channel_id(
            handle
        )

        if not channel_id:

            return None

        channel_statistics = (
            get_channel_statistics(
                channel_id
            )
        )

        latest_videos = get_latest_videos(
            channel_id,
            max_results=max_results
        )

        return {
            "channel_name":
                channel_name,

            "channel_handle":
                handle,

            "channel_id":
                channel_id,

            "channel_statistics":
                channel_statistics,

            "videos":
                latest_videos
        }

    except Exception as error:

        log_service_message(
            f"Channel Complete Data Error: {error}"
        )

        return None


def get_multiple_channels_data(
    channels_dict,
    max_results=10
):

    all_channels_data = {}

    for channel_name, handle in channels_dict.items():

        try:

            channel_data = (
                get_channel_complete_data(
                    channel_name,
                    handle,
                    max_results=max_results
                )
            )

            if channel_data:

                all_channels_data[
                    channel_name
                ] = channel_data

                log_service_message(
                    f"Successfully fetched data for {channel_name}"
                )

            else:

                log_service_message(
                    f"Failed to fetch data for {channel_name}"
                )

        except Exception as error:

            log_service_message(
                f"Multi-channel Fetch Error for {channel_name}: {error}"
            )

    return all_channels_data


def get_competitor_channels_data():

    return get_multiple_channels_data(
        COMPETITOR_CHANNELS
    )


def get_primary_channels_data():

    return get_multiple_channels_data(
        CHANNELS
    )


def build_competitive_summary(
    benchmark_data
):

    summary = []

    for channel_name, data in benchmark_data.items():

        try:

            stats = data.get(
                "channel_statistics",
                {}
            )

            summary.append({
                "channel_name":
                    channel_name,

                "subscribers":
                    stats.get(
                        "subscribers",
                        0
                    ),

                "total_views":
                    stats.get(
                        "total_views",
                        0
                    ),

                "total_videos":
                    stats.get(
                        "total_videos",
                        0
                    ),

                "latest_videos_analyzed":
                    len(
                        data.get(
                            "videos",
                            []
                        )
                    )
            })

        except Exception as error:

            log_service_message(
                f"Competitive Summary Error: {error}"
            )

    return summary