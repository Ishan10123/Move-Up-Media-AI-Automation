import os
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
    export_to_docx,
    export_to_pdf
)

from app.utils.cache_manager import (
    warm_cache,
    get_cache_statistics
)


def ensure_directories():

    directories = [
        "reports",
        "logs"
    ]

    for directory in directories:

        os.makedirs(
            directory,
            exist_ok=True
        )


def write_log(message):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    formatted_message = (
        f"[{timestamp}] {message}"
    )

    print(formatted_message)

    with open(
        "logs/main.log",
        "a",
        encoding="utf-8"
    ) as log_file:

        log_file.write(
            formatted_message + "\n"
        )


def print_section(title):

    print("\n")

    print("=" * 100)

    print(title)

    print("=" * 100)


def display_channel_statistics(stats):

    print("\nCHANNEL STATISTICS")

    print("-" * 100)

    print(
        f"Subscribers: "
        f"{stats.get('subscribers', 'N/A')}"
    )

    print(
        f"Total Views: "
        f"{stats.get('total_views', 'N/A')}"
    )

    print(
        f"Total Videos: "
        f"{stats.get('total_videos', 'N/A')}"
    )

    print(
        f"Country: "
        f"{stats.get('country', 'N/A')}"
    )


def display_channel_summary(summary):

    print("\nCHANNEL PERFORMANCE SUMMARY")

    print("-" * 100)

    print(
        f"Total Videos: "
        f"{summary.get('total_videos', 0)}"
    )

    print(
        f"Total Views: "
        f"{summary.get('total_views', 0)}"
    )

    print(
        f"Average Engagement: "
        f"{summary.get('average_engagement', 0)}%"
    )

    print(
        f"Average Performance Score: "
        f"{summary.get('average_performance_score', 0)}"
    )

    print(
        f"Strong Videos: "
        f"{summary.get('strong_videos', 0)}"
    )

    print(
        f"Underperforming Videos: "
        f"{summary.get('underperforming_videos', 0)}"
    )

    print(
        f"Channel Health Score: "
        f"{summary.get('channel_health_score', 0)}"
    )

    print(
        f"Channel Health Status: "
        f"{summary.get('channel_health', 'Unknown')}"
    )


def display_video_metrics(video):

    print("\n" + "-" * 100)

    print(
        f"Title: {video['title']}"
    )

    print(
        f"Published At: {video['published_at']}"
    )

    print(
        f"Views: {video['views']}"
    )

    print(
        f"Likes: {video['likes']}"
    )

    print(
        f"Comments: {video['comments']}"
    )

    print(
        f"Engagement Rate: "
        f"{video['engagement_rate']}%"
    )

    print(
        f"Views Per Day: "
        f"{video['views_per_day']}"
    )

    print(
        f"Performance Score: "
        f"{video['performance_score']}"
    )

    print(
        f"Classification: "
        f"{video['classification']}"
    )

    print(
        f"Growth Velocity: "
        f"{video['growth_velocity']}"
    )

    print(
        f"Momentum: "
        f"{video['momentum_classification']}"
    )

    print(
        f"Retention Signal: "
        f"{video['estimated_retention_signal']}"
    )

    print(
        f"Audience Signal: "
        f"{video['audience_signal_strength']}"
    )

    print(
        f"Video URL: "
        f"{video['video_url']}"
    )


def export_reports(
    report,
    channel_name
):

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    pdf_filename = (
        f"reports/{channel_name}_{timestamp}.pdf"
    )

    docx_filename = (
        f"reports/{channel_name}_{timestamp}.docx"
    )

    export_to_pdf(
        report,
        pdf_filename,
        channel_name
    )

    export_to_docx(
        report,
        docx_filename,
        channel_name
    )

    write_log(
        f"Reports exported for {channel_name}"
    )

    print(
        f"\nPDF Report Saved: "
        f"{pdf_filename}"
    )

    print(
        f"DOCX Report Saved: "
        f"{docx_filename}"
    )


def process_channel(
    channel_name,
    handle
):

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

            write_log(
                f"Failed to fetch channel ID for {channel_name}"
            )

            return

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

            write_log(
                f"No videos found for {channel_name}"
            )

            return

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

        export_reports(
            report,
            channel_name
        )

        write_log(
            f"Analysis completed successfully for {channel_name}"
        )

    except Exception as error:

        write_log(
            f"Main Pipeline Error for {channel_name}: {str(error)}"
        )

        write_log(
            traceback.format_exc()
        )


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

            print(
                f"Competitor: "
                f"{competitor['channel_name']}"
            )

            print(
                f"Subscribers: "
                f"{competitor['subscribers']}"
            )

            print(
                f"Total Views: "
                f"{competitor['total_views']}"
            )

            print(
                f"Total Videos: "
                f"{competitor['total_videos']}"
            )

            print(
                f"Latest Videos Analyzed: "
                f"{competitor['latest_videos_analyzed']}"
            )

    except Exception as error:

        write_log(
            f"Competitive Benchmark Error: {str(error)}"
        )


def display_runtime_summary(
    start_time
):

    execution_time = round(
        time.time() - start_time,
        2
    )

    cache_stats = (
        get_cache_statistics()
    )

    print_section(
        "SYSTEM EXECUTION SUMMARY"
    )

    print(
        f"Execution Time: "
        f"{execution_time} seconds"
    )

    print(
        f"Active Cache Entries: "
        f"{cache_stats['active_entries']}"
    )

    print(
        f"Cache Size: "
        f"{cache_stats['total_cache_items']}"
    )


def main():

    start_time = time.time()

    ensure_directories()

    warm_cache()

    print_section(
        "MOVEUP MEDIA AI CONTENT OPS PLATFORM"
    )

    print(
        "\nInitializing autonomous analytics pipeline...\n"
    )

    write_log(
        "Main execution started"
    )

    for channel_name, handle in CHANNELS.items():

        process_channel(
            channel_name,
            handle
        )

    run_competitive_benchmark()

    display_runtime_summary(
        start_time
    )

    print_section(
        "AUTONOMOUS ANALYSIS COMPLETED"
    )

    print(
        "\nAll reports generated successfully.\n"
    )

    write_log(
        "Main execution completed"
    )


if __name__ == "__main__":

    main()