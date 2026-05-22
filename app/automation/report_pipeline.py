import os
import traceback

from datetime import datetime
from datetime import timedelta

from app.services.youtube_service import (
    CHANNELS,
    get_channel_id,
    get_latest_videos
)

from app.analytics.metrics_engine import (
    enrich_video_metrics,
    calculate_channel_health_score,
    classify_channel_health,
    generate_channel_summary
)

from app.agents.report_generator import (
    generate_channel_report
)

from app.utils.report_exporter import (
    export_to_pdf,
    export_to_docx
)

from app.utils.config import (
    REPORT_RETENTION_DAYS
)


LOG_FILE_PATH = "logs/automation.log"


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

    ensure_directories()

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    formatted_message = (
        f"[{timestamp}] {message}"
    )

    print(formatted_message)

    try:

        with open(
            LOG_FILE_PATH,
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


def cleanup_old_reports():

    ensure_directories()

    reports_directory = "reports"

    cutoff_time = (
        datetime.now()
        -
        timedelta(
            days=REPORT_RETENTION_DAYS
        )
    )

    deleted_files = 0

    try:

        for filename in os.listdir(
            reports_directory
        ):

            file_path = os.path.join(
                reports_directory,
                filename
            )

            if not os.path.isfile(
                file_path
            ):

                continue

            file_modified_time = datetime.fromtimestamp(
                os.path.getmtime(
                    file_path
                )
            )

            if file_modified_time < cutoff_time:

                os.remove(
                    file_path
                )

                deleted_files += 1

        write_log(
            f"Old report cleanup completed | Deleted Files: {deleted_files}"
        )

    except Exception as error:

        write_log(
            f"Report cleanup error: {str(error)}"
        )


def generate_report_filenames(
    channel_name
):

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    return {

        "pdf":
            f"reports/{channel_name}_{timestamp}.pdf",

        "docx":
            f"reports/{channel_name}_{timestamp}.docx"
    }


def build_pipeline_summary(
    channel_name,
    enriched_videos
):

    channel_summary = generate_channel_summary(
        enriched_videos
    )

    health_score = calculate_channel_health_score(
        enriched_videos
    )

    return {

        "channel_name":
            channel_name,

        "health_score":
            round(
                health_score,
                2
            ),

        "health_status":
            classify_channel_health(
                health_score
            ),

        "analytics":
            channel_summary
    }


def validate_report_content(report):

    if not report:

        return False

    invalid_patterns = [

        "quota",
        "resource_exhausted",
        "temporarily unavailable",
        "ai assistant error",
        "report generation error",
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


def generate_fallback_report(
    channel_name,
    enriched_videos
):

    summary = generate_channel_summary(
        enriched_videos
    )

    top_video = None

    if enriched_videos:

        top_video = max(

            enriched_videos,

            key=lambda x:

            x.get(
                "performance_score",
                0
            )
        )

    fallback_report = f"""
MOVEUP MEDIA OPERATIONAL REPORT

Channel:
{channel_name}

Executive Summary:
The AI reporting engine is currently unavailable. A lightweight operational analytics summary has been generated automatically.

Performance Overview:
- Total Videos: {summary.get("total_videos")}
- Total Views: {summary.get("total_views")}
- Average Engagement: {summary.get("average_engagement")}%
- Average Performance Score: {summary.get("average_performance_score")}

Top Performing Video:
{top_video.get("title") if top_video else "Unavailable"}

Operational Status:
{summary.get("channel_health")}

Recommendation:
Continue monitoring engagement trends and publishing consistency while the AI reporting engine recovers.
"""

    return fallback_report.strip()


def fetch_and_analyze_channel(
    channel_name,
    handle
):

    write_log(
        f"Starting analysis for {channel_name}"
    )

    channel_id = get_channel_id(
        handle
    )

    if not channel_id:

        raise Exception(
            f"Unable to fetch channel ID for {channel_name}"
        )

    write_log(
        f"Channel ID fetched for {channel_name}"
    )

    videos = get_latest_videos(
        channel_id
    )

    if not videos:

        raise Exception(
            f"No videos found for {channel_name}"
        )

    write_log(
        f"{len(videos)} videos fetched for {channel_name}"
    )

    enriched_videos = enrich_video_metrics(
        videos
    )

    write_log(
        f"Metrics enrichment completed for {channel_name}"
    )

    return enriched_videos


def generate_and_export_reports(
    channel_name,
    enriched_videos
):

    report = generate_channel_report(
        channel_name,
        enriched_videos
    )

    if not validate_report_content(
        report
    ):

        write_log(
            f"AI report validation failed for {channel_name}. Generating fallback report."
        )

        report = generate_fallback_report(
            channel_name,
            enriched_videos
        )

    filenames = generate_report_filenames(
        channel_name
    )

    export_to_pdf(
        report,
        filenames["pdf"],
        channel_name
    )

    write_log(
        f"PDF report exported for {channel_name}"
    )

    export_to_docx(
        report,
        filenames["docx"],
        channel_name
    )

    write_log(
        f"DOCX report exported for {channel_name}"
    )

    return {

        "report":
            report,

        "pdf":
            filenames["pdf"],

        "docx":
            filenames["docx"]
    }


def process_channel(
    channel_name,
    handle
):

    try:

        enriched_videos = fetch_and_analyze_channel(
            channel_name,
            handle
        )

        exported_reports = generate_and_export_reports(
            channel_name,
            enriched_videos
        )

        summary = build_pipeline_summary(
            channel_name,
            enriched_videos
        )

        write_log(
            f"Pipeline completed successfully for {channel_name}"
        )

        return {

            "success":
                True,

            "channel_name":
                channel_name,

            "summary":
                summary,

            "pdf_report":
                exported_reports["pdf"],

            "docx_report":
                exported_reports["docx"]
        }

    except Exception as error:

        write_log(
            f"Pipeline Error for {channel_name}: {str(error)}"
        )

        write_log(
            traceback.format_exc()
        )

        return {

            "success":
                False,

            "channel_name":
                channel_name,

            "error":
                str(error)
        }


def run_full_pipeline():

    ensure_directories()

    cleanup_old_reports()

    pipeline_start = datetime.now()

    write_log("=" * 70)

    write_log(
        "MOVEUP MEDIA AUTONOMOUS AI PIPELINE STARTED"
    )

    write_log("=" * 70)

    pipeline_results = []

    successful_channels = 0

    failed_channels = 0

    for channel_name, handle in CHANNELS.items():

        result = process_channel(
            channel_name,
            handle
        )

        pipeline_results.append(
            result
        )

        if result["success"]:

            successful_channels += 1

        else:

            failed_channels += 1

    execution_time = round(

        (
            datetime.now()
            -
            pipeline_start
        ).total_seconds(),
        2
    )

    write_log("=" * 70)

    write_log(
        "PIPELINE EXECUTION COMPLETED"
    )

    write_log(
        f"Successful Channels: {successful_channels}"
    )

    write_log(
        f"Failed Channels: {failed_channels}"
    )

    write_log(
        f"Execution Time: {execution_time} seconds"
    )

    write_log("=" * 70)

    return {

        "status":
            "completed",

        "successful_channels":
            successful_channels,

        "failed_channels":
            failed_channels,

        "execution_time_seconds":
            execution_time,

        "results":
            pipeline_results
    }


if __name__ == "__main__":

    final_result = run_full_pipeline()

    print("\n")

    print("=" * 70)

    print(
        "MOVEUP MEDIA AI AUTOMATION COMPLETED"
    )

    print("=" * 70)

    print(final_result)

    print("=" * 70)

    print("\n")