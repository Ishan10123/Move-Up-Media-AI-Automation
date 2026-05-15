import time
import hashlib
import threading


CACHE = {}

CACHE_LOCK = threading.Lock()

DEFAULT_EXPIRY_SECONDS = 300


def normalize_identifier(identifier):

    return str(identifier).strip().lower()


def generate_cache_key(
    prefix,
    identifier
):

    normalized_identifier = (
        normalize_identifier(
            identifier
        )
    )

    hashed_identifier = hashlib.md5(
        normalized_identifier.encode()
    ).hexdigest()

    return (
        f"{prefix}:{hashed_identifier}"
    )


def current_timestamp():

    return time.time()


def build_cache_item(
    value,
    expiry
):

    return {
        "value":
            value,

        "timestamp":
            current_timestamp(),

        "expiry":
            expiry
    }


def is_cache_expired(item):

    elapsed_time = (
        current_timestamp()
        -
        item["timestamp"]
    )

    return elapsed_time > item["expiry"]


def set_cache(
    key,
    value,
    expiry=DEFAULT_EXPIRY_SECONDS
):

    with CACHE_LOCK:

        CACHE[key] = build_cache_item(
            value,
            expiry
        )


def get_cache(key):

    with CACHE_LOCK:

        item = CACHE.get(key)

        if not item:

            return None

        if is_cache_expired(item):

            delete_cache(key)

            return None

        return item["value"]


def delete_cache(key):

    with CACHE_LOCK:

        if key in CACHE:

            del CACHE[key]


def clear_cache():

    with CACHE_LOCK:

        CACHE.clear()


def cache_exists(key):

    return get_cache(key) is not None


def cleanup_expired_cache():

    expired_keys = []

    with CACHE_LOCK:

        for key, item in CACHE.items():

            if is_cache_expired(item):

                expired_keys.append(key)

        for key in expired_keys:

            del CACHE[key]

    return len(expired_keys)


def get_cache_size():

    cleanup_expired_cache()

    with CACHE_LOCK:

        return len(CACHE)


def get_cache_keys():

    cleanup_expired_cache()

    with CACHE_LOCK:

        return list(CACHE.keys())


def get_cache_statistics():

    cleanup_expired_cache()

    with CACHE_LOCK:

        total_items = len(CACHE)

        total_memory_entries = sum([
            1
            for _
            in CACHE.values()
        ])

    return {
        "total_cache_items":
            total_items,

        "active_entries":
            total_memory_entries,

        "default_expiry_seconds":
            DEFAULT_EXPIRY_SECONDS
    }


def get_or_set_cache(
    key,
    callback,
    expiry=DEFAULT_EXPIRY_SECONDS
):

    cached_value = get_cache(key)

    if cached_value is not None:

        return cached_value

    value = callback()

    set_cache(
        key,
        value,
        expiry
    )

    return value


def cache_response(
    prefix,
    identifier,
    callback,
    expiry=DEFAULT_EXPIRY_SECONDS
):

    key = generate_cache_key(
        prefix,
        identifier
    )

    return get_or_set_cache(
        key,
        callback,
        expiry
    )


def warm_cache():

    cleanup_expired_cache()

    return {
        "status":
            "cache_ready",

        "active_cache_items":
            get_cache_size()
    }


def invalidate_prefix(prefix):

    deleted_count = 0

    with CACHE_LOCK:

        matching_keys = [
            key
            for key in CACHE.keys()
            if key.startswith(prefix)
        ]

        for key in matching_keys:

            del CACHE[key]

            deleted_count += 1

    return deleted_count


def get_cache_item_metadata(key):

    with CACHE_LOCK:

        item = CACHE.get(key)

        if not item:

            return None

        age_seconds = (
            current_timestamp()
            -
            item["timestamp"]
        )

        remaining_seconds = max(
            0,
            item["expiry"] - age_seconds
        )

        return {
            "created_timestamp":
                item["timestamp"],

            "age_seconds":
                round(age_seconds, 2),

            "remaining_expiry_seconds":
                round(remaining_seconds, 2)
        }


def refresh_cache_expiry(
    key,
    new_expiry=DEFAULT_EXPIRY_SECONDS
):

    with CACHE_LOCK:

        item = CACHE.get(key)

        if not item:

            return False

        item["timestamp"] = (
            current_timestamp()
        )

        item["expiry"] = new_expiry

        return True