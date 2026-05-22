import os
import sys
import time
import traceback

from datetime import datetime

from app.services.youtube_service import (

    CHANNELS,

    get_channel_id,

    get_latest_videos,

    get_channel_statistics,

    get_competitor_channels_data,

    build_competitive_summary
)

from app.analytics.metrics_engine import (

    enrich_video_metrics,

    generate_channel_summary,

    calculate_channel_health_score,

    classify_channel_health
)

from app.agents.report_generator import (
    generate_channel_report
)

from app.utils.report_exporter import (
    export_reports
)

from app.utils.cache_manager import (

    warm_cache,

    get_cache_statistics,

    cache_health_check
)

from app.utils.config import (

    CONFIG_SUMMARY,

    validate_configuration,

    APP_TITLE
)


LOG_FILE = "logs/main.log"


def ensure_directories():

    directories = [

        "logs",

        "reports"
    ]

    for directory in directories:

        os.makedirs(
            directory,
            exist_ok=True
        )


def write_log(
    message,
    level="INFO"
):

    ensure_directories()

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    formatted_message = (

        f"[{level}] "

        f"[{timestamp}] "

        f"{message}"
    )

    print(
        formatted_message
    )

    try:

        with open(

            LOG_FILE,

            "a",

            encoding="utf-8"
        ) as log_file:

            log_file.write(
                formatted_message + "\n"
            )

    except Exception as error:

        print(
            f"[LOGGING ERROR] {str(error)}"
        )


def print_section(title):

    print("\n")

    print("=" * 100)

    print(title)

    print("=" * 100)


def startup_validation():

    print_section(
        "SYSTEM STARTUP VALIDATION"
    )

    validation = validate_configuration()

    if not validation["valid"]:

        for error in validation["errors"]:

            write_log(
                error,
                level="ERROR"
            )

        raise Exception(
            "Configuration validation failed."
        )

    if validation["warnings"]:

        for warning in validation["warnings"]:

            write_log(
                warning,
                level="WARNING"
            )

    write_log(
        "Configuration validation completed successfully"
    )


def display_configuration_summary():

    print_section(
        "PLATFORM CONFIGURATION"
    )

    for key, value in CONFIG_SUMMARY.items():

        print(
            f"{key}: {value}"
        )


def display_channel_statistics(stats):

    print("\nCHANNEL STATISTICS")

    print("-" * 100)

    metrics = {

        "Subscribers":
            stats.get(
                "subscribers",
                "N/A"
            ),

        "Total Views":
            stats.get(
                "total_views",
                "N/A"
            ),

        "Total Videos":
            stats.get(
                "total_videos",
                "N/A"
            ),

        "Country":
            stats.get(
                "country",
                "N/A"
            )
    }

    for key, value in metrics.items():

        print(
            f"{key}: {value}"
        )


def display_channel_summary(summary):

    print("\nCHANNEL PERFORMANCE SUMMARY")

    print("-" * 100)

    metrics = {

        "Total Videos":
            summary.get(
                "total_videos",
                0
            ),

        "Total Views":
            summary.get(
                "total_views",
                0
            ),

        "Average Engagement":
            f"{summary.get('average_engagement', 0)}%",

        "Average Performance Score":
            summary.get(
                "average_performance_score",
                0
            ),

        "Strong Videos":
            summary.get(
                "strong_videos",
                0
            ),

        "Underperforming Videos":
            summary.get(
                "underperforming_videos",
                0
            ),

        "Channel Health Score":
            summary.get(
                "channel_health_score",
                0
            ),

        "Channel Health":
            summary.get(
                "channel_health",
                "Unknown"
            )
    }

    for key, value in metrics.items():

        print(
            f"{key}: {value}"
        )


def display_video_metrics(video):

    print("\n" + "-" * 100)

    metrics = {

        "Title":
            video.get(
                "title",
                "Unknown"
            ),

        "Published At":
            video.get(
                "published_at",
                "N/A"
            ),

        "Views":
            video.get(
                "views",
                0
            ),

        "Likes":
            video.get(
                "likes",
                0
            ),

        "Comments":
            video.get(
                "comments",
                0
            ),

        "Engagement Rate":
            f"{video.get('engagement_rate', 0)}%",

        "Views Per Day":
            video.get(
                "views_per_day",
                0
            ),

        "Performance Score":
            video.get(
                "performance_score",
                0
            ),

        "Classification":
            video.get(
                "classification",
                "Unknown"
            ),

        "Growth Velocity":
            video.get(
                "growth_velocity",
                "Unknown"
            ),

        "Momentum":
            video.get(
                "momentum_classification",
                "Unknown"
            ),

        "Retention Signal":
            video.get(
                "estimated_retention_signal",
                "Unknown"
            ),

        "Audience Signal":
            video.get(
                "audience_signal_strength",
                "Unknown"
            ),

        "Video URL":
            video.get(
                "video_url",
                "Unavailable"
            )
    }

    for key, value in metrics.items():

        print(
            f"{key}: {value}"
        )


def validate_report(report):

    if not report:

        return False

    invalid_patterns = [

        "quota",

        "resource_exhausted",

        "report generation error",

        "temporarily unavailable",

        "429",

        "503"
    ]

    report_text = str(
        report
    ).lower()

    return not any(

        pattern in report_text

        for pattern in invalid_patterns
    )


def process_channel(
    channel_name,
    handle
):

    channel_start_time = time.time()

    try:

        print_section(
            f"CHANNEL ANALYSIS: {channel_name}"
        )

        write_log(
            f"Starting analysis for {channel_name}"
        )

        channel_id = get_channel_id(
            handle
        )

        if not channel_id:

            raise Exception(
                "Unable to fetch channel ID."
            )

        print(
            f"\nChannel ID: {channel_id}"
        )

        channel_statistics = (
            get_channel_statistics(
                channel_id
            )
        )

        display_channel_statistics(
            channel_statistics
        )

        videos = get_latest_videos(

            channel_id,

            max_results=10
        )

        if not videos:

            raise Exception(
                "No videos found."
            )

        enriched_videos = (
            enrich_video_metrics(
                videos
            )
        )

        channel_summary = (
            generate_channel_summary(
                enriched_videos
            )
        )

        display_channel_summary(
            channel_summary
        )

        print_section(
            "VIDEO PERFORMANCE METRICS"
        )

        for video in enriched_videos:

            display_video_metrics(
                video
            )

        print_section(
            "AI PERFORMANCE REPORT"
        )

        report = generate_channel_report(

            channel_name,

            enriched_videos
        )

        print(report)

        exported_files = {}

        if validate_report(report):

            exported_files = export_reports(

                report,

                channel_name
            )

            write_log(
                f"Reports exported successfully for {channel_name}"
            )

        else:

            write_log(
                f"Report validation failed for {channel_name}",
                level="WARNING"
            )

        execution_time = round(

            time.time()
            -
            channel_start_time,

            2
        )

        write_log(
            f"Analysis completed for {channel_name} | Execution Time={execution_time}s"
        )

        return {

            "success":
                True,

            "channel":
                channel_name,

            "summary":
                channel_summary,

            "report_exports":
                exported_files,

            "execution_time":
                execution_time
        }

    except Exception as error:

        write_log(
            f"Channel Processing Error for {channel_name}: {str(error)}",
            level="ERROR"
        )

        write_log(
            traceback.format_exc(),
            level="ERROR"
        )

        return {

            "success":
                False,

            "channel":
                channel_name,

            "error":
                str(error)
        }


def run_competitive_benchmark():

    try:

        print_section(
            "COMPETITIVE BENCHMARK ANALYSIS"
        )

        benchmark_data = (
            get_competitor_channels_data()
        )

        benchmark_summary = (
            build_competitive_summary(
                benchmark_data
            )
        )

        for competitor in benchmark_summary:

            print("\n" + "-" * 100)

            metrics = {

                "Competitor":
                    competitor.get(
                        "channel_name",
                        "Unknown"
                    ),

                "Subscribers":
                    competitor.get(
                        "subscribers",
                        0
                    ),

                "Total Views":
                    competitor.get(
                        "total_views",
                        0
                    ),

                "Total Videos":
                    competitor.get(
                        "total_videos",
                        0
                    ),

                "Latest Videos Analyzed":
                    competitor.get(
                        "latest_videos_analyzed",
                        0
                    )
            }

            for key, value in metrics.items():

                print(
                    f"{key}: {value}"
                )

        return benchmark_summary

    except Exception as error:

        write_log(
            f"Competitive Benchmark Error: {str(error)}",
            level="ERROR"
        )

        return []


def display_runtime_summary(
    start_time,
    pipeline_results
):

    execution_time = round(

        time.time()
        -
        start_time,

        2
    )

    cache_stats = (
        get_cache_statistics()
    )

    cache_health = (
        cache_health_check()
    )

    successful_channels = len([

        result

        for result in pipeline_results

        if result.get(
            "success"
        )
    ])

    failed_channels = len([

        result

        for result in pipeline_results

        if not result.get(
            "success"
        )
    ])

    print_section(
        "SYSTEM EXECUTION SUMMARY"
    )

    metrics = {

        "Execution Time":
            f"{execution_time} seconds",

        "Successful Channels":
            successful_channels,

        "Failed Channels":
            failed_channels,

        "Active Cache Entries":
            cache_stats.get(
                "active_entries",
                0
            ),

        "Cache Size":
            cache_stats.get(
                "total_cache_items",
                0
            ),

        "Cache Healthy":
            cache_health.get(
                "healthy",
                False
            )
    }

    for key, value in metrics.items():

        print(
            f"{key}: {value}"
        )


def initialize_runtime():

    ensure_directories()

    warm_cache()

    startup_validation()

    display_configuration_summary()

    write_log(
        "Runtime initialized successfully"
    )


def main():

    start_time = time.time()

    pipeline_results = []

    try:

        initialize_runtime()

        print_section(
            APP_TITLE
        )

        print(
            "\nInitializing autonomous analytics pipeline...\n"
        )

        write_log(
            "Main execution started"
        )

        for channel_name, handle in CHANNELS.items():

            result = process_channel(

                channel_name,

                handle
            )

            pipeline_results.append(
                result
            )

        run_competitive_benchmark()

        display_runtime_summary(

            start_time,

            pipeline_results
        )

        print_section(
            "AUTONOMOUS ANALYSIS COMPLETED"
        )

        print(
            "\nAll operational workflows completed.\n"
        )

        write_log(
            "Main execution completed successfully"
        )

    except KeyboardInterrupt:

        write_log(
            "Execution interrupted by user",
            level="WARNING"
        )

        sys.exit(0)

    except Exception as error:

        write_log(
            f"Critical Main Execution Error: {str(error)}",
            level="CRITICAL"
        )

        write_log(
            traceback.format_exc(),
            level="CRITICAL"
        )

        sys.exit(1)


if __name__ == "__main__":

    main()