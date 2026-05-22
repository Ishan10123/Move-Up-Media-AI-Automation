import time
import json
import hashlib
import threading

from collections import OrderedDict


DEFAULT_EXPIRY_SECONDS = 300

MAX_CACHE_ITEMS = 1000

CACHE = OrderedDict()

CACHE_LOCK = threading.RLock()


def current_timestamp():

    return time.time()


def normalize_identifier(identifier):

    try:

        normalized = json.dumps(
            identifier,
            sort_keys=True,
            default=str
        )

        return normalized.strip().lower()

    except Exception:

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

    hashed_identifier = hashlib.sha256(
        normalized_identifier.encode(
            "utf-8"
        )
    ).hexdigest()

    return (
        f"{prefix}:{hashed_identifier}"
    )


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

    try:

        elapsed_time = (
            current_timestamp()
            -
            item["timestamp"]
        )

        return elapsed_time > item["expiry"]

    except Exception:

        return True


def cleanup_expired_cache():

    deleted_keys = []

    with CACHE_LOCK:

        cache_keys = list(
            CACHE.keys()
        )

        for key in cache_keys:

            item = CACHE.get(key)

            if not item:

                continue

            if is_cache_expired(item):

                deleted_keys.append(
                    key
                )

        for key in deleted_keys:

            CACHE.pop(
                key,
                None
            )

    return len(
        deleted_keys
    )


def enforce_cache_limit():

    with CACHE_LOCK:

        while len(CACHE) > MAX_CACHE_ITEMS:

            CACHE.popitem(
                last=False
            )


def set_cache(
    key,
    value,
    expiry=DEFAULT_EXPIRY_SECONDS
):

    try:

        cleanup_expired_cache()

        cache_item = build_cache_item(
            value,
            expiry
        )

        with CACHE_LOCK:

            CACHE[key] = cache_item

            CACHE.move_to_end(
                key
            )

            enforce_cache_limit()

        return True

    except Exception as error:

        print(
            f"[CACHE SET ERROR] {str(error)}"
        )

        return False


def get_cache(key):

    try:

        with CACHE_LOCK:

            item = CACHE.get(key)

            if not item:

                return None

            if is_cache_expired(item):

                CACHE.pop(
                    key,
                    None
                )

                return None

            CACHE.move_to_end(
                key
            )

            return item.get(
                "value"
            )

    except Exception as error:

        print(
            f"[CACHE GET ERROR] {str(error)}"
        )

        return None


def delete_cache(key):

    try:

        with CACHE_LOCK:

            CACHE.pop(
                key,
                None
            )

        return True

    except Exception as error:

        print(
            f"[CACHE DELETE ERROR] {str(error)}"
        )

        return False


def clear_cache():

    try:

        with CACHE_LOCK:

            CACHE.clear()

        return True

    except Exception as error:

        print(
            f"[CACHE CLEAR ERROR] {str(error)}"
        )

        return False


def cache_exists(key):

    cached_value = get_cache(
        key
    )

    return cached_value is not None


def get_cache_size():

    cleanup_expired_cache()

    with CACHE_LOCK:

        return len(CACHE)


def get_cache_keys():

    cleanup_expired_cache()

    with CACHE_LOCK:

        return list(
            CACHE.keys()
        )


def get_cache_statistics():

    cleanup_expired_cache()

    with CACHE_LOCK:

        total_items = len(
            CACHE
        )

        total_expired = 0

        for item in CACHE.values():

            if is_cache_expired(item):

                total_expired += 1

        active_entries = (
            total_items
            -
            total_expired
        )

    return {

        "total_cache_items":
            total_items,

        "active_entries":
            active_entries,

        "expired_entries":
            total_expired,

        "default_expiry_seconds":
            DEFAULT_EXPIRY_SECONDS,

        "max_cache_items":
            MAX_CACHE_ITEMS
    }


def get_cache_item_metadata(key):

    try:

        with CACHE_LOCK:

            item = CACHE.get(key)

            if not item:

                return None

            created_timestamp = item.get(
                "timestamp",
                0
            )

            age_seconds = (
                current_timestamp()
                -
                created_timestamp
            )

            remaining_expiry_seconds = max(

                0,

                item.get(
                    "expiry",
                    0
                )
                -
                age_seconds
            )

            return {

                "created_timestamp":
                    created_timestamp,

                "age_seconds":
                    round(
                        age_seconds,
                        2
                    ),

                "remaining_expiry_seconds":
                    round(
                        remaining_expiry_seconds,
                        2
                    )
            }

    except Exception as error:

        print(
            f"[CACHE METADATA ERROR] {str(error)}"
        )

        return None


def refresh_cache_expiry(
    key,
    new_expiry=DEFAULT_EXPIRY_SECONDS
):

    try:

        with CACHE_LOCK:

            item = CACHE.get(key)

            if not item:

                return False

            item["timestamp"] = (
                current_timestamp()
            )

            item["expiry"] = (
                new_expiry
            )

            CACHE.move_to_end(
                key
            )

        return True

    except Exception as error:

        print(
            f"[CACHE REFRESH ERROR] {str(error)}"
        )

        return False


def invalidate_prefix(prefix):

    deleted_count = 0

    try:

        with CACHE_LOCK:

            matching_keys = [

                key

                for key in CACHE.keys()

                if key.startswith(prefix)
            ]

            for key in matching_keys:

                CACHE.pop(
                    key,
                    None
                )

                deleted_count += 1

        return deleted_count

    except Exception as error:

        print(
            f"[CACHE INVALIDATION ERROR] {str(error)}"
        )

        return 0


def get_or_set_cache(
    key,
    callback,
    expiry=DEFAULT_EXPIRY_SECONDS
):

    cached_value = get_cache(
        key
    )

    if cached_value is not None:

        return cached_value

    try:

        value = callback()

        set_cache(
            key,
            value,
            expiry
        )

        return value

    except Exception as error:

        print(
            f"[CACHE CALLBACK ERROR] {str(error)}"
        )

        return None


def cache_response(
    prefix,
    identifier,
    callback,
    expiry=DEFAULT_EXPIRY_SECONDS
):

    cache_key = generate_cache_key(
        prefix,
        identifier
    )

    return get_or_set_cache(
        cache_key,
        callback,
        expiry
    )


def warm_cache():

    cleanup_expired_cache()

    return {

        "status":
            "cache_ready",

        "active_cache_items":
            get_cache_size(),

        "cache_statistics":
            get_cache_statistics()
    }


def cache_health_check():

    try:

        cleanup_expired_cache()

        stats = get_cache_statistics()

        cache_usage_percent = round(

            (
                stats["total_cache_items"]
                /
                MAX_CACHE_ITEMS
            ) * 100,
            2
        )

        return {

            "healthy":
                cache_usage_percent < 90,

            "cache_usage_percent":
                cache_usage_percent,

            "statistics":
                stats
        }

    except Exception as error:

        return {

            "healthy":
                False,

            "error":
                str(error)
        }