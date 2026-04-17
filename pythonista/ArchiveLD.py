"""
ArchiveLD — One-tap calendar archive (one year at a time)

Dumps ALL events for ONE YEAR to keep output small enough for Shortcuts.
Change YEAR below to archive different years. Run once per year.

Just tap Run in Pythonista. No arguments needed.
Output goes to console (Pythonista shortcut can save to Dropbox).
"""

import datetime as dt
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

# ── CHANGE THIS to archive a different year ───────────────
YEAR = 2020
# ───────────────────────────────────────────────────────────

START_DATE = dt.datetime(YEAR, 1, 1)
END_DATE = dt.datetime(YEAR + 1, 1, 1)  # exclusive — covers through Dec 31


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

    attendees = []
    try:
        att_list = ev.attendees()
        if att_list:
            for att in list(att_list):
                name = safe_str(att.name()) if att.name() else None
                email = None
                try:
                    url_attr = att.URL()
                    if url_attr:
                        raw = safe_str(url_attr.absoluteString()) or ""
                        if raw.startswith("mailto:"):
                            email = raw[7:]
                        elif "@" in raw:
                            email = raw
                except Exception:
                    pass
                if name or email:
                    attendees.append({"name": name, "email": email})
    except Exception:
        attendees = []

    organizer = None
    try:
        org = ev.organizer()
        if org:
            org_name = safe_str(org.name()) if org.name() else None
            org_email = None
            try:
                org_url = org.URL()
                if org_url:
                    raw = safe_str(org_url.absoluteString()) or ""
                    if raw.startswith("mailto:"):
                        org_email = raw[7:]
                    elif "@" in raw:
                        org_email = raw
            except Exception:
                pass
            if org_name or org_email:
                organizer = {"name": org_name, "email": org_email}
    except Exception:
        organizer = None

    return {
        "title": title,
        "all_day": is_all_day,
        "start_dt": start_dt,
        "end_dt": end_dt,
        "calendar": cal_title,
        "location": location,
        "notes": notes,
        "url": url,
        "organizer": organizer,
        "attendees": attendees,
    }

# ── Fetch events in chunks (EventKit can choke on huge ranges) ─

def get_events_chunked(start, end, chunk_days=30):
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
        return "No events found."

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
        if rec.get("organizer"):
            org = rec["organizer"]
            org_str = org.get("name") or ""
            if org.get("email"):
                org_str = "{0} <{1}>".format(org_str, org["email"]).strip() if org_str else org["email"]
            line += "\n  organizer: {0}".format(org_str)
        if rec.get("attendees"):
            parts = []
            for a in rec["attendees"]:
                a_str = a.get("name") or ""
                if a.get("email"):
                    a_str = "{0} <{1}>".format(a_str, a["email"]).strip() if a_str else a["email"]
                if a_str:
                    parts.append(a_str)
            if parts:
                line += "\n  attendees: {0}".format("; ".join(parts))
        if rec.get("url"):
            line += "\n  url: {0}".format(rec["url"])
        if rec.get("notes"):
            line += "\n  notes: {0}".format(rec["notes"])

        lines.append(line)

    return "\n".join(lines)

# ── Main ───────────────────────────────────────────────────

def main():
    print("")
    print("# Calendar Archive — {0}".format(YEAR))
    print("# Generated: {0}".format(dt.datetime.now().strftime("%Y-%m-%d %H:%M")))
    print("")

    raw_events = get_events_chunked(START_DATE, END_DATE)
    records = [event_to_record(ev) for ev in raw_events]

    print("")
    print("Total events: {0}".format(len(records)))
    print("")
    print("=" * 60)
    print(format_markdown(records))


if __name__ == "__main__":
    try:
        main()
    finally:
        print("ROBOT_SIGNATURE_BOTTOM: End of file reached.")