"""Checks a single website and returns the result as a dictionary."""

import time
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests

TIMEOUT_SECONDS = 10
HEADERS = {"User-Agent": "UptimeMonitor/1.0"}


def is_valid_url(url):
    """Return True if the URL looks like http(s)://something."""
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def check_website(url):
    """Check one website and return a dictionary describing the result."""
    result = {
        "url": url,
        "is_up": False,
        "status_code": None,
        "response_time_ms": None,
        "error": None,
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }

    if not is_valid_url(url):
        result["error"] = "Invalid URL (needs http:// or https://)"
        return result

    try:
        start = time.perf_counter()
        response = requests.get(url, timeout=TIMEOUT_SECONDS, headers=HEADERS)
        elapsed = time.perf_counter() - start

        result["status_code"] = response.status_code
        result["response_time_ms"] = round(elapsed * 1000)

        if 200 <= response.status_code < 400:
            result["is_up"] = True
        else:
            result["error"] = f"HTTP {response.status_code} {response.reason}"

    except requests.exceptions.Timeout:
        result["error"] = f"Timed out after {TIMEOUT_SECONDS}s"
    except requests.exceptions.SSLError:
        result["error"] = "SSL certificate error"
    except requests.exceptions.ConnectionError:
        result["error"] = "Can't connect (site not found or offline)"
    except requests.exceptions.TooManyRedirects:
        result["error"] = "Too many redirects"
    except requests.exceptions.RequestException as e:
        result["error"] = f"Request failed: {e}"

    return result


if __name__ == "__main__":
    test_sites = [
        "https://google.com",
        "https://this-site-does-not-exist-12345.com",
        "not-a-valid-url",
    ]
    for site in test_sites:
        print(check_website(site)) 