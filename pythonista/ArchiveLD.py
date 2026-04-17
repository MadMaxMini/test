"""
ArchiveLD — One-tap LaunchDarkly calendar archive

Dumps ALL events from Jan 2019 – Dec 2024 that match LaunchDarkly
(zoom links, calendar name, titles) to a readable markdown + JSON.

Just tap Run in Pythonista. No arguments needed.
Output goes to console (Pythonista shortcut can save to Dropbox).
"""

import datetime as dt
import json
import time

try:
    from objc_util import ObjCClass  # type: ignore
except Exception:
    print("This script must be run in Pythonista on iOS.")
    raise

print("ROBOT_SIGNATURE_TOP: ArchiveLD.py is running.")

EKEventStore = ObjCClass("EKEventStore")
NSDate = ObjCClass("NSDate")

# ── Config (all baked in) ──────────────────────────────────

START_DATE = dt.datetime(2019, 1, 1)
END_DATE = dt.datetime(2025, 1, 1)  # exclusive — covers through Dec 31, 2024

# Match if ANY of these appear in title, calendar name, location, or URL
LD_MARKERS = [
    "launchdarkly",
    "launch darkly",
]

# Known LD phantom events that don't contain "launchdarkly" in metadata
LD_TITLE_EXACT = [
    "how are you *really* doing?",
    "weekly review",
    "strategic team forecast call",
    "west leadership call",
    "srat hoffman",
    "all revenue",
    "compensation 101",
    "pave training",
    "tola weekly team call",
]

# ── Helpers ────────────────────────────────────────────────

def ns_to_py(nsdate):
    return dt.datetime.fromtimestamp(nsdate.timeIntervalSince1970())

def py_to_ns(pydt):
    ts = time.mktime(pydt.timetuple())
    return NSDate.dateWithTimeIntervalSince1970_(ts)

def safe_str(value):
    if value is None:
        return None
    s = str(value).strip()
    return s or None

def fmt_time(t):
    return t.strftime("%I:%M %p").lstrip("0")

def fmt_time_range(start, end):
    if not end or end <= start:
        return fmt_time(start)
    return "{0}\u2013{1}".format(fmt_time(start), fmt_time(end))

# ── Event extraction ───────────────────────────────────────

def event_to_record(ev):
    title = safe_str(ev.title()) or "Untitled"
    is_all_day = bool(ev.isAllDay())
    start_dt = ns_to_py(ev.startDate())
    end_dt = ns_to_py(ev.endDate()) if ev.endDate() else None

    cal_title = None
    try:
        cal = ev.calendar()
        cal_title = safe_str(cal.title()) if cal else None
    except Exception:
        cal_title = None

    location = safe_str(ev.location())

    notes = None
    try:
        raw = safe_str(ev.notes())
        if raw and len(raw) > 300:
            raw = raw[:299] + "..."
        notes = raw
    except Exception:
        notes = None

    url = None
    try:
        url_obj = ev.URL()
        if url_obj:
            url = safe_str(url_obj.absoluteString()) or safe_str(url_obj)
    except Exception:
        url = None

    return {
        "title": title,
        "all_day": is_all_day,
        "start_dt": start_dt,
        "end_dt": end_dt,
        "calendar": cal_title,
        "location": location,
        "notes": notes,
        "url": url,
    }

def is_ld_event(rec):
    """Return True if this event looks like it belongs to LaunchDarkly."""
    # Build searchable text from all metadata
    haystack = " ".join([
        rec.get("title") or "",
        rec.get("calendar") or "",
        rec.get("location") or "",
        rec.get("url") or "",
        rec.get("notes") or "",
    ]).lower()

    # Check markers (substring match)
    for marker in LD_MARKERS:
        if marker in haystack:
            return True

    # Check known phantom titles (prefix match)
    title_lower = (rec.get("title") or "").lower()
    for t in LD_TITLE_EXACT:
        if title_lower.startswith(t):
            return True

    return False

# ── Fetch events in chunks (EventKit can choke on huge ranges) ─

def get_events_chunked(start, end, chunk_days=90):
    """Fetch events in chunks to avoid EventKit memory issues."""
    store = EKEventStore.new()
    all_events = []
    cursor = start

    while cursor < end:
        chunk_end = min(cursor + dt.timedelta(days=chunk_days), end)
        ns_start = py_to_ns(cursor)
        ns_end = py_to_ns(chunk_end)

        pred = store.predicateForEventsWithStartDate_endDate_calendars_(ns_start, ns_end, None)
        events = store.eventsMatchingPredicate_(pred)

        if events:
            for ev in list(events):
                all_events.append(ev)

        period = "{0} to {1}".format(
            cursor.strftime("%Y-%m-%d"),
            chunk_end.strftime("%Y-%m-%d"),
        )
        chunk_count = len(list(events)) if events else 0
        print("  ... fetched {0}: {1} events".format(period, chunk_count))
        cursor = chunk_end

    all_events.sort(key=lambda ev: ns_to_py(ev.startDate()).timestamp())
    return all_events

# ── Output formatting ──────────────────────────────────────

def format_markdown(records):
    """Pretty markdown grouped by month."""
    if not records:
        return "No LaunchDarkly events found."

    lines = []
    current_month = None

    for rec in records:
        month_key = rec["start_dt"].strftime("%Y-%m")
        if month_key != current_month:
            current_month = month_key
            month_label = rec["start_dt"].strftime("%B %Y")
            lines.append("")
            lines.append("## " + month_label)
            lines.append("")

        date_str = rec["start_dt"].strftime("%a %b %d")

        if rec["all_day"]:
            time_str = "all-day"
        else:
            time_str = fmt_time_range(rec["start_dt"], rec.get("end_dt"))

        title = rec["title"]
        cal = rec.get("calendar") or ""

        line = "- **{0}** {1} | {2}".format(date_str, time_str, title)
        if cal:
            line += " [{0}]".format(cal)
        if rec.get("location"):
            line += " @ {0}".format(rec["location"])
        if rec.get("url"):
            line += "\n  url: {0}".format(rec["url"])
        if rec.get("notes"):
            line += "\n  notes: {0}".format(rec["notes"])

        lines.append(line)

    return "\n".join(lines)

# ── Main ───────────────────────────────────────────────────

def main():
    print("")
    print("# LaunchDarkly Calendar Archive")
    print("# Period: 2019-01-01 to 2024-12-31")
    print("# Generated: {0}".format(dt.datetime.now().strftime("%Y-%m-%d %H:%M")))
    print("")
    print("Fetching events (this may take a minute)...")
    print("")

    raw_events = get_events_chunked(START_DATE, END_DATE)
    print("")
    print("Total calendar events in range: {0}".format(len(raw_events)))

    # Convert and filter to LD only
    records = [event_to_record(ev) for ev in raw_events]
    ld_records = [r for r in records if is_ld_event(r)]

    print("LaunchDarkly events found: {0}".format(len(ld_records)))
    print("")
    print("=" * 60)

    # Markdown output
    print(format_markdown(ld_records))

    # JSON block for machine processing
    print("")
    print("ROBOT_JSON_BEGIN")

    def rec_to_json(r):
        return {
            "title": r.get("title"),
            "all_day": bool(r.get("all_day")),
            "start": r["start_dt"].isoformat(),
            "end": r["end_dt"].isoformat() if r.get("end_dt") else None,
            "calendar": r.get("calendar"),
            "location": r.get("location"),
            "notes": r.get("notes"),
            "url": r.get("url"),
        }

    payload = {
        "archive": "launchdarkly",
        "range": {"start": "2019-01-01", "end": "2024-12-31"},
        "total_events": len(ld_records),
        "events": [rec_to_json(r) for r in ld_records],
    }
    print(json.dumps(payload, ensure_ascii=False))
    print("ROBOT_JSON_END")


if __name__ == "__main__":
    try:
        main()
    finally:
        print("ROBOT_SIGNATURE_BOTTOM: End of file reached.")