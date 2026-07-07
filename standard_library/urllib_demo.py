"""
urllib module — REST API client patterns using the X (Twitter) API v2 as example.

Topic: how to call an authenticated paginated REST API using only the standard
library (urllib + json), with sensible handling of rate limits and time windows.

Concrete scenario: collect SNS posts ("過去5年分の発言") for sentiment / public-
opinion analysis. The X API v2 endpoints used here are:

    GET /2/tweets/search/recent       (last 7 days, Basic tier)
    GET /2/tweets/search/all          (full archive — Enterprise tier only)

⚠️  Retrieving five years of historical tweets is ONLY possible via the
    `search/all` endpoint, which requires the paid Enterprise tier. The
    free / Basic tier is capped at the last 7 days via `search/recent`.
    Academic Research access (which previously allowed full archive) was
    discontinued in 2023. This script wires up both endpoints, but the
    archive call will return 403 unless your Bearer Token has the right tier.

Set the bearer token via environment variable to run for real:

    export X_BEARER_TOKEN="AAAA..."
    python standard_library/urllib_demo.py "選挙 OR 世論調査" --days 7

Without the token, the script runs in dry-run mode and prints the request
that *would* be sent.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from typing import Iterator
from zoneinfo import ZoneInfo

JST = ZoneInfo("Asia/Tokyo")
UTC = ZoneInfo("UTC")

API_BASE = "https://api.twitter.com/2"
RECENT_ENDPOINT = f"{API_BASE}/tweets/search/recent"   # last 7 days
ARCHIVE_ENDPOINT = f"{API_BASE}/tweets/search/all"     # full archive (Enterprise)

# Default fields requested — see the X API v2 docs for the full set.
TWEET_FIELDS = "created_at,author_id,lang,public_metrics,conversation_id"
MAX_RESULTS_PER_PAGE = 100  # API hard cap


# ── Request helpers ────────────────────────────────────────────────────────
def _build_url(endpoint: str, params: dict[str, str | int]) -> str:
    """Build a fully-qualified URL with a urlencoded query string."""
    qs = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    return f"{endpoint}?{qs}"


def _bearer_request(url: str, token: str) -> urllib.request.Request:
    """Wrap a GET in a Request carrying the OAuth2 Bearer header."""
    req = urllib.request.Request(url, method="GET")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("User-Agent", "python-learning-repo/urllib_demo")
    return req


def _do_request(req: urllib.request.Request, max_retries: int = 5) -> dict:
    """
    Execute the request with retry on 429 (rate limited) and 5xx.
    Honors the `Retry-After` response header when present.
    """
    backoff = 2
    for attempt in range(1, max_retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429 or 500 <= e.code < 600:
                wait = int(e.headers.get("Retry-After", backoff))
                print(f"  HTTP {e.code} — retry {attempt}/{max_retries} in {wait}s",
                      file=sys.stderr)
                time.sleep(wait)
                backoff *= 2
                continue
            # 4xx other than 429 — not retryable
            body = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"X API {e.code}: {body}") from e
    raise RuntimeError(f"Gave up after {max_retries} retries")


# ── Public API ─────────────────────────────────────────────────────────────
def search_tweets(
    query: str,
    *,
    start_time: datetime,
    end_time: datetime,
    token: str,
    archive: bool = False,
    page_size: int = MAX_RESULTS_PER_PAGE,
) -> Iterator[dict]:
    """
    Yield individual tweet dicts matching `query` between start_time and end_time.

    The X API requires RFC3339 timestamps in UTC. Pagination is driven by the
    `next_token` field in the response `meta`.
    """
    endpoint = ARCHIVE_ENDPOINT if archive else RECENT_ENDPOINT
    next_token: str | None = None

    while True:
        params: dict[str, str | int] = {
            "query": query,
            "tweet.fields": TWEET_FIELDS,
            "max_results": page_size,
            "start_time": start_time.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end_time":   end_time.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        if next_token:
            params["next_token"] = next_token

        url = _build_url(endpoint, params)
        payload = _do_request(_bearer_request(url, token))

        for tweet in payload.get("data", []):
            yield tweet

        next_token = payload.get("meta", {}).get("next_token")
        if not next_token:
            break


def five_year_window(now: datetime | None = None) -> tuple[datetime, datetime]:
    """Return (start, end) covering ~5 years up to `now` (default: now in JST)."""
    end = now or datetime.now(tz=JST)
    start = end - timedelta(days=365 * 5)
    return start, end


# ── CLI ────────────────────────────────────────────────────────────────────
def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Collect tweets via X API v2.")
    p.add_argument("query", help='Search query, e.g. "選挙 OR 世論調査 lang:ja"')
    p.add_argument("--days", type=int, default=7,
                   help="Window size in days back from now (default: 7).")
    p.add_argument("--five-years", action="store_true",
                   help="Use a 5-year window. Requires --archive + Enterprise tier.")
    p.add_argument("--archive", action="store_true",
                   help="Hit search/all (full archive) instead of search/recent.")
    p.add_argument("--limit", type=int, default=10,
                   help="Stop after collecting this many tweets (default: 10).")
    p.add_argument("--out", help="Optional path to write results as JSON lines.")
    return p.parse_args(argv)


def _main(argv: list[str]) -> int:
    args = _parse_args(argv)

    if args.five_years:
        start, end = five_year_window()
        args.archive = True
    else:
        end = datetime.now(tz=JST)
        start = end - timedelta(days=args.days)

    print(f"Query : {args.query!r}")
    print(f"Window: {start:%Y-%m-%d %H:%M %Z} → {end:%Y-%m-%d %H:%M %Z}")
    print(f"Endpoint: {'search/all (archive)' if args.archive else 'search/recent'}")

    token = os.environ.get("X_BEARER_TOKEN")
    if not token:
        # Dry run — just show the URL that would be called.
        url = _build_url(
            ARCHIVE_ENDPOINT if args.archive else RECENT_ENDPOINT,
            {
                "query": args.query,
                "tweet.fields": TWEET_FIELDS,
                "max_results": MAX_RESULTS_PER_PAGE,
                "start_time": start.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "end_time":   end.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
        )
        print("\nNo X_BEARER_TOKEN set — dry run. Would GET:")
        print(f"  {url}")
        print("\nSet X_BEARER_TOKEN to call the API for real.")
        return 0

    collected: list[dict] = []
    for i, tweet in enumerate(
        search_tweets(args.query, start_time=start, end_time=end,
                      token=token, archive=args.archive),
        start=1,
    ):
        collected.append(tweet)
        ts = tweet.get("created_at", "")
        text = tweet.get("text", "").replace("\n", " ")[:80]
        print(f"{i:>4}. [{ts}] {text}")
        if i >= args.limit:
            break

    print(f"\nCollected {len(collected)} tweet(s).")

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            for t in collected:
                f.write(json.dumps(t, ensure_ascii=False) + "\n")
        print(f"Wrote {args.out}")

    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
