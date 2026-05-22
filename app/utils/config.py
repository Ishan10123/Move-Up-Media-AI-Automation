import os
import threading

from dotenv import load_dotenv


load_dotenv()


CONFIG_LOCK = threading.RLock()

CURRENT_GEMINI_KEY_INDEX = 0


SUPPORTED_MODELS = [

    "gemini-1.5-flash",

    "gemini-1.5-pro",

    "gemini-2.0-flash"
]


DEFAULT_PRIMARY_MODEL = (
    "gemini-1.5-flash"
)

DEFAULT_FALLBACK_MODEL = (
    "gemini-1.5-flash"
)


def safe_string(value):

    try:

        if value is None:

            return None

        cleaned_value = str(
            value
        ).strip()

        if not cleaned_value:

            return None

        return cleaned_value

    except Exception:

        return None


def get_streamlit_secret(name):

    try:

        import streamlit as st

        if name in st.secrets:

            return safe_string(
                st.secrets[name]
            )

    except Exception:

        pass

    return None


def get_environment_variable(name):

    try:

        value = os.getenv(name)

        return safe_string(
            value
        )

    except Exception:

        return None


def get_env_variable(name):

    streamlit_secret = get_streamlit_secret(
        name
    )

    if streamlit_secret:

        return streamlit_secret

    environment_variable = (
        get_environment_variable(
            name
        )
    )

    if environment_variable:

        return environment_variable

    raise ValueError(
        f"Missing required environment variable: {name}"
    )


def get_optional_env_variable(
    name,
    default_value=None
):

    try:

        return get_env_variable(
            name
        )

    except Exception:

        return default_value


def get_boolean_env_variable(
    name,
    default=False
):

    value = str(

        get_optional_env_variable(
            name,
            default
        )

    ).strip().lower()

    return value in [

        "true",
        "1",
        "yes",
        "enabled",
        "on"
    ]


def get_integer_env_variable(
    name,
    default=0
):

    try:

        return int(

            str(

                get_optional_env_variable(
                    name,
                    default
                )

            ).strip()
        )

    except Exception:

        return default


def get_float_env_variable(
    name,
    default=0.0
):

    try:

        return float(

            str(

                get_optional_env_variable(
                    name,
                    default
                )

            ).strip()
        )

    except Exception:

        return default


def validate_model_name(model_name):

    if model_name in SUPPORTED_MODELS:

        return model_name

    return DEFAULT_PRIMARY_MODEL


YOUTUBE_API_KEY = get_env_variable(
    "YOUTUBE_API_KEY"
)


def load_gemini_api_keys():

    keys = []

    for key_name in [

        "GEMINI_API_KEY_1",
        "GEMINI_API_KEY_2",
        "GEMINI_API_KEY_3",
        "GEMINI_API_KEY_4",
        "GEMINI_API_KEY_5"
    ]:

        key_value = (
            get_optional_env_variable(
                key_name
            )
        )

        if key_value:

            keys.append(
                key_value
            )

    legacy_key = (
        get_optional_env_variable(
            "GEMINI_API_KEY"
        )
    )

    if legacy_key:

        if legacy_key not in keys:

            keys.append(
                legacy_key
            )

    unique_keys = []

    for key in keys:

        if key not in unique_keys:

            unique_keys.append(
                key
            )

    return unique_keys


GEMINI_API_KEYS = (
    load_gemini_api_keys()
)


if not GEMINI_API_KEYS:

    raise ValueError(
        "No Gemini API keys configured."
    )


GEMINI_API_KEY = (
    GEMINI_API_KEYS[0]
)


APP_ENVIRONMENT = (
    get_optional_env_variable(
        "APP_ENVIRONMENT",
        "production"
    )
)


PRODUCTION_MODE = (
    APP_ENVIRONMENT.lower()
    ==
    "production"
)


ENABLE_CACHE = (
    get_boolean_env_variable(
        "ENABLE_CACHE",
        True
    )
)

ENABLE_AUTOMATION = (
    get_boolean_env_variable(
        "ENABLE_AUTOMATION",
        True
    )
)

ENABLE_BENCHMARKING = (
    get_boolean_env_variable(
        "ENABLE_BENCHMARKING",
        True
    )
)

ENABLE_FALLBACK_MODEL = (
    get_boolean_env_variable(
        "ENABLE_FALLBACK_MODEL",
        True
    )
)

ENABLE_AI_RETRY = (
    get_boolean_env_variable(
        "ENABLE_AI_RETRY",
        True
    )
)


REPORT_RETENTION_DAYS = (
    get_integer_env_variable(
        "REPORT_RETENTION_DAYS",
        30
    )
)

CACHE_EXPIRY_SECONDS = (
    get_integer_env_variable(
        "CACHE_EXPIRY_SECONDS",
        1800
    )
)

AI_REQUEST_COOLDOWN = (
    get_integer_env_variable(
        "AI_REQUEST_COOLDOWN",
        10
    )
)

MAX_CHAT_HISTORY = (
    get_integer_env_variable(
        "MAX_CHAT_HISTORY",
        10
    )
)

MAX_RETRIES = (
    get_integer_env_variable(
        "MAX_RETRIES",
        2
    )
)

RETRY_DELAY_SECONDS = (
    get_integer_env_variable(
        "RETRY_DELAY_SECONDS",
        5
    )
)

AI_REQUEST_TIMEOUT_SECONDS = (
    get_integer_env_variable(
        "AI_REQUEST_TIMEOUT_SECONDS",
        60
    )
)


PRIMARY_MODEL = validate_model_name(

    get_optional_env_variable(
        "PRIMARY_MODEL",
        DEFAULT_PRIMARY_MODEL
    )
)

FALLBACK_MODEL = validate_model_name(

    get_optional_env_variable(
        "FALLBACK_MODEL",
        DEFAULT_FALLBACK_MODEL
    )
)


DEFAULT_REPORT_FORMAT = (
    get_optional_env_variable(
        "DEFAULT_REPORT_FORMAT",
        "pdf"
    )
)

APP_TITLE = (
    get_optional_env_variable(
        "APP_TITLE",
        "MoveUp Media AI Ops Platform"
    )
)

COMPANY_NAME = (
    get_optional_env_variable(
        "COMPANY_NAME",
        "MoveUp Media"
    )
)


def get_total_available_keys():

    return len(
        GEMINI_API_KEYS
    )


def get_current_key_index():

    global CURRENT_GEMINI_KEY_INDEX

    with CONFIG_LOCK:

        return CURRENT_GEMINI_KEY_INDEX


def get_current_gemini_api_key():

    global CURRENT_GEMINI_KEY_INDEX

    with CONFIG_LOCK:

        return GEMINI_API_KEYS[
            CURRENT_GEMINI_KEY_INDEX
        ]


def rotate_gemini_api_key():

    global CURRENT_GEMINI_KEY_INDEX

    with CONFIG_LOCK:

        CURRENT_GEMINI_KEY_INDEX = (

            CURRENT_GEMINI_KEY_INDEX + 1

        ) % len(
            GEMINI_API_KEYS
        )

        return GEMINI_API_KEYS[
            CURRENT_GEMINI_KEY_INDEX
        ]


def get_next_gemini_api_key():

    return rotate_gemini_api_key()


def mask_secret(secret):

    if not secret:

        return "Unavailable"

    if len(secret) <= 8:

        return "********"

    return (
        secret[:4]
        +
        "********"
        +
        secret[-4:]
    )


def validate_configuration():

    validation_results = {

        "valid":
            True,

        "errors":
            [],

        "warnings":
            []
    }

    if not YOUTUBE_API_KEY:

        validation_results[
            "valid"
        ] = False

        validation_results[
            "errors"
        ].append(
            "Missing YouTube API key"
        )

    if not GEMINI_API_KEYS:

        validation_results[
            "valid"
        ] = False

        validation_results[
            "errors"
        ].append(
            "No Gemini API keys configured"
        )

    if PRIMARY_MODEL not in SUPPORTED_MODELS:

        validation_results[
            "warnings"
        ].append(
            "Unsupported primary model detected"
        )

    if FALLBACK_MODEL not in SUPPORTED_MODELS:

        validation_results[
            "warnings"
        ].append(
            "Unsupported fallback model detected"
        )

    return validation_results


CONFIG_SUMMARY = {

    "environment":
        APP_ENVIRONMENT,

    "production_mode":
        PRODUCTION_MODE,

    "cache_enabled":
        ENABLE_CACHE,

    "automation_enabled":
        ENABLE_AUTOMATION,

    "benchmarking_enabled":
        ENABLE_BENCHMARKING,

    "fallback_enabled":
        ENABLE_FALLBACK_MODEL,

    "retry_enabled":
        ENABLE_AI_RETRY,

    "primary_model":
        PRIMARY_MODEL,

    "fallback_model":
        FALLBACK_MODEL,

    "available_gemini_keys":
        len(GEMINI_API_KEYS),

    "youtube_key":
        mask_secret(
            YOUTUBE_API_KEY
        ),

    "active_gemini_key":
        mask_secret(
            get_current_gemini_api_key()
        )
}


def print_configuration_summary():

    print("\n")

    print("=" * 70)

    print(
        "MOVEUP MEDIA CONFIGURATION SUMMARY"
    )

    print("=" * 70)

    for key, value in CONFIG_SUMMARY.items():

        print(
            f"{key}: {value}"
        )

    print("=" * 70)

    print("\n")