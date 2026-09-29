"""Calculates uptime percentage and other statistics from saved history."""

from contextlib import closing

from .database import get_connection

STATS_QUERY = """
SELECT
    c1.url                                                AS url,
    COUNT(*)                                              AS total,
    SUM(c1.is_up)                                         AS successful,
    AVG(CASE WHEN c1.is_up = 1 THEN c1.response_time_ms END) AS avg_response,
    (SELECT c2.is_up FROM checks c2
      WHERE c2.url = c1.url ORDER BY c2.id DESC LIMIT 1)  AS last_is_up
FROM checks c1
"""


def _row_to_stats(row):
    """Turn one database row into a friendly dictionary."""
    total = row["total"]
    successful = row["successful"] or 0
    return {
        "url": row["url"],
        "total": total,
        "successful": successful,
        "failed": total - successful,
        "uptime_percent": (successful / total * 100) if total else 0.0,
        "avg_response_ms": row["avg_response"],
        "last_is_up": row["last_is_up"],
    }


def get_uptime_stats(url):
    """Return stats for one website, or None if it has no records."""
    with closing(get_connection()) as conn:
        row = conn.execute(
            STATS_QUERY + " WHERE c1.url = ? GROUP BY c1.url", (url,)
        ).fetchone()
    return _row_to_stats(row) if row else None


def get_all_stats():
    """Return stats for every website in the database."""
    with closing(get_connection()) as conn:
        rows = conn.execute(
            STATS_QUERY + " GROUP BY c1.url ORDER BY c1.url"
        ).fetchall()
    return [_row_to_stats(row) for row in rows]


def format_stats(stats):
    """Turn the stats dictionary into a nicely aligned text block."""
    avg = stats["avg_response_ms"]
    avg_text = f"{avg:.0f}ms" if avg is not None else "N/A"

    return (
        f"Website: {stats['url']}\n\n"
        f"Uptime:       {stats['uptime_percent']:.2f}%\n"
        f"Checks:       {stats['total']:,}\n"
        f"Successful:   {stats['successful']:,}\n"
        f"Failed:       {stats['failed']:,}\n"
        f"Avg Response: {avg_text}"
    )
    