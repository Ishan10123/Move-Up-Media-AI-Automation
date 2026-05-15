from datetime import datetime

from apscheduler.schedulers.blocking import (
    BlockingScheduler
)

from apscheduler.events import (
    EVENT_JOB_EXECUTED,
    EVENT_JOB_ERROR
)

from app.automation.report_pipeline import (
    run_full_pipeline
)


scheduler = BlockingScheduler()


def write_scheduler_log(message):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    formatted_message = (
        f"[SCHEDULER {timestamp}] {message}"
    )

    print(formatted_message)


def scheduled_weekly_reports():

    write_scheduler_log(
        "Starting scheduled autonomous AI pipeline"
    )

    try:

        result = run_full_pipeline()

        write_scheduler_log(
            f"Pipeline completed successfully | "
            f"Successful Channels: "
            f"{result['successful_channels']} | "
            f"Failed Channels: "
            f"{result['failed_channels']}"
        )

    except Exception as error:

        write_scheduler_log(
            f"Scheduler Pipeline Error: {str(error)}"
        )


def scheduler_listener(event):

    if event.exception:

        write_scheduler_log(
            "Scheduled job crashed unexpectedly"
        )

    else:

        write_scheduler_log(
            "Scheduled job executed successfully"
        )


scheduler.add_listener(
    scheduler_listener,
    EVENT_JOB_EXECUTED | EVENT_JOB_ERROR
)


scheduler.add_job(
    scheduled_weekly_reports,
    trigger="cron",
    day_of_week="mon",
    hour=9,
    minute=0,
    id="moveup_weekly_ai_reports",
    replace_existing=True
)


def start_scheduler():

    write_scheduler_log(
        "MoveUp Media Autonomous Scheduler Started"
    )

    write_scheduler_log(
        "Weekly reports scheduled every Monday at 09:00"
    )

    write_scheduler_log(
        "Scheduler is actively monitoring jobs"
    )

    scheduler.start()


if __name__ == "__main__":

    start_scheduler()