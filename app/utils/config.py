import os

from dotenv import load_dotenv


load_dotenv()


def get_streamlit_secret(name):

    try:

        import streamlit as st

        if name in st.secrets:

            value = st.secrets[name]

            if value:

                return str(value).strip()

    except Exception:

        pass

    return None


def get_environment_variable(name):

    value = os.getenv(name)

    if value:

        return str(value).strip()

    return None


def get_env_variable(name):

    streamlit_secret = get_streamlit_secret(
        name
    )

    if streamlit_secret:

        return streamlit_secret

    env_variable = get_environment_variable(
        name
    )

    if env_variable:

        return env_variable

    raise ValueError(
        f"Missing required environment variable: {name}"
    )


def get_optional_env_variable(
    name,
    default_value=None
):

    try:

        return get_env_variable(name)

    except Exception:

        return default_value


def get_boolean_env_variable(
    name,
    default=False
):

    value = str(
        get_optional_env_variable(
            name,
            str(default)
        )
    ).lower()

    return value in [
        "true",
        "1",
        "yes",
        "enabled"
    ]


def get_integer_env_variable(
    name,
    default=0
):

    try:

        return int(
            get_optional_env_variable(
                name,
                default
            )
        )

    except Exception:

        return default


YOUTUBE_API_KEY = get_env_variable(
    "YOUTUBE_API_KEY"
)

GEMINI_API_KEY = get_env_variable(
    "GEMINI_API_KEY"
)


APP_ENVIRONMENT = get_optional_env_variable(
    "APP_ENVIRONMENT",
    "development"
)


ENABLE_CACHE = get_boolean_env_variable(
    "ENABLE_CACHE",
    True
)

ENABLE_AUTOMATION = get_boolean_env_variable(
    "ENABLE_AUTOMATION",
    True
)

ENABLE_BENCHMARKING = get_boolean_env_variable(
    "ENABLE_BENCHMARKING",
    True
)

ENABLE_FALLBACK_MODEL = get_boolean_env_variable(
    "ENABLE_FALLBACK_MODEL",
    True
)

ENABLE_AI_RETRY = get_boolean_env_variable(
    "ENABLE_AI_RETRY",
    True
)


REPORT_RETENTION_DAYS = get_integer_env_variable(
    "REPORT_RETENTION_DAYS",
    30
)

CACHE_EXPIRY_SECONDS = get_integer_env_variable(
    "CACHE_EXPIRY_SECONDS",
    1800
)

AI_REQUEST_COOLDOWN = get_integer_env_variable(
    "AI_REQUEST_COOLDOWN",
    5
)

MAX_CHAT_HISTORY = get_integer_env_variable(
    "MAX_CHAT_HISTORY",
    20
)

MAX_RETRIES = get_integer_env_variable(
    "MAX_RETRIES",
    3
)

RETRY_DELAY_SECONDS = get_integer_env_variable(
    "RETRY_DELAY_SECONDS",
    3
)


PRIMARY_MODEL = get_optional_env_variable(
    "PRIMARY_MODEL",
    "gemini-1.5-flash"
)

FALLBACK_MODEL = get_optional_env_variable(
    "FALLBACK_MODEL",
    "gemini-1.5-flash"
)


DEFAULT_REPORT_FORMAT = get_optional_env_variable(
    "DEFAULT_REPORT_FORMAT",
    "pdf"
)

APP_TITLE = get_optional_env_variable(
    "APP_TITLE",
    "MoveUp Media AI Ops Platform"
)

COMPANY_NAME = get_optional_env_variable(
    "COMPANY_NAME",
    "MoveUp Media"
)