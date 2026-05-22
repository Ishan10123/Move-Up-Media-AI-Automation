from datetime import datetime

from apscheduler.schedulers.background import (
    BackgroundScheduler
)

from apscheduler.events import (
    EVENT_JOB_EXECUTED,
    EVENT_JOB_ERROR
)

from app.automation.report_pipeline import (
    run_full_pipeline
)

from app.utils.config import (
    ENABLE_AUTOMATION
)


scheduler = BackgroundScheduler(
    timezone="Asia/Kolkata"
)


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


def configure_scheduler():

    scheduler.add_job(

        scheduled_weekly_reports,

        trigger="cron",

        day_of_week="mon",

        hour=9,

        minute=0,

        id="moveup_weekly_ai_reports",

        replace_existing=True,

        max_instances=1,

        coalesce=True,

        misfire_grace_time=3600
    )


def start_scheduler():

    if not ENABLE_AUTOMATION:

        write_scheduler_log(
            "Automation disabled via configuration"
        )

        return

    if scheduler.running:

        write_scheduler_log(
            "Scheduler already running"
        )

        return

    configure_scheduler()

    write_scheduler_log(
        "MoveUp Media Autonomous Scheduler Started"
    )

    write_scheduler_log(
        "Weekly reports scheduled every Monday at 09:00 IST"
    )

    write_scheduler_log(
        "Scheduler is actively monitoring jobs"
    )

    scheduler.start()


def shutdown_scheduler():

    if scheduler.running:

        scheduler.shutdown()

        write_scheduler_log(
            "Scheduler shutdown completed"
        )


if __name__ == "__main__":

    start_scheduler()

    try:

        import time

        while True:

            time.sleep(60)

    except (
        KeyboardInterrupt,
        SystemExit
    ):

        shutdown_scheduler()