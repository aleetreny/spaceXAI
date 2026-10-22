"""Import public Luma calendars into luma.js.

Reads each calendar's public iCal feed (the "subscribe" link Luma offers to
anyone). No API key and no Luma Plus. Only what the feed publishes is kept:
title, dates, the event link, the location text and GEO when Luma shows them,
and the organiser name. Descriptions, guests and contacts are not stored.

Run from the repo root:  python3 scripts/import-luma.py
"""
import datetime
import json
import re
import sys
import urllib.request
from pathlib import Path

FEED = "https://api.lu.ma/ics/get?entity=calendar&id={}"

# How each calendar was found. "linked" = linked from tonight's event page.
# "name" = luma.com/<slug> exists and its calendar name matches the community;
# a lead still has to confirm it is theirs.
CALENDARS = [
    {"id": "cal-QQGEIJl1K33N0zb", "community": None, "match": "linked",
     "found": "Calendar of tonight's event, luma.com/eveur09a"},
    {"id": "cal-61Cv6COs4g9GKw7", "community": None, "match": "linked",
     "found": "Linked from luma.com/eveur09a"},
    {"id": "cal-Qk1P4msjA8eRxCs", "community": "hack-collective", "match": "name",
     "found": "luma.com/thehackcollective"},
    {"id": "cal-pMjwAfN0msdzm8I", "community": "night-office", "match": "name",
     "found": "luma.com/nightoffice"},
    {"id": "cal-ObXRLmBUISp8LQh", "community": "ai-agents-lab", "match": "name",
     "found": "luma.com/aiagentslab, named UK AI Agents Lab"},
    {"id": "cal-UVqp4TtefuCg69F", "community": "ai-pilled", "match": "name",
     "found": "luma.com/ai-pilled"},
    {"id": "cal-kJ57qrBTX6wGZyo", "community": "outpost", "match": "name",
     "found": "luma.com/outpost"},
]

# Searched on luma.com and not found, so the page can say so.
NOT_FOUND = ["unicorn-mafia", "hackradar", "kickstart-global", "basedcollective",
             "corgi", "united-italian-societies"]


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "same-room-import/1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def unfold(text):
    # RFC 5545: a line starting with a space continues the previous one.
    return re.sub(r"\r?\n[ \t]", "", text).splitlines()


def unescape(value):
    return (value.replace("\\n", "\n").replace("\\N", "\n")
            .replace("\\,", ",").replace("\\;", ";").replace("\\\\", "\\"))


def parse_date(name, value):
    if "VALUE=DATE" in name:
        return datetime.date(int(value[:4]), int(value[4:6]), int(value[6:8])).isoformat(), True
    stamp = datetime.datetime.strptime(value.rstrip("Z"), "%Y%m%dT%H%M%S")
    return stamp.replace(tzinfo=datetime.timezone.utc).isoformat().replace("+00:00", "Z"), False


def parse(text):
    calendar = {"name": None, "events": []}
    event = None
    for line in unfold(text):
        if ":" not in line:
            continue
        name, value = line.split(":", 1)
        key = name.split(";", 1)[0]
        if key == "X-WR-CALNAME":
            calendar["name"] = unescape(value)
        elif line == "BEGIN:VEVENT":
            event = {"hosts": []}
        elif line == "END:VEVENT":
            calendar["events"].append(event)
            event = None
        elif event is None:
            continue
        elif key == "UID":
            event["id"] = value.split("@", 1)[0]
        elif key == "SUMMARY":
            event["title"] = unescape(value)
        elif key in ("DTSTART", "DTEND"):
            stamp, all_day = parse_date(name, value)
            event["startsAt" if key == "DTSTART" else "endsAt"] = stamp
            if key == "DTSTART":
                event["allDay"] = all_day
        elif key == "LOCATION":
            event["location"] = unescape(value)
        elif key == "GEO":
            lat, lng = value.split(";")
            event["geo"] = {"lat": round(float(lat), 6), "lng": round(float(lng), 6)}
        elif key == "ORGANIZER":
            host = re.search(r'CN="?([^";:]+)', name)
            if host:
                event["hosts"].append(host.group(1).strip())
        elif key == "DESCRIPTION":
            link = re.search(r"https://luma\.com/[A-Za-z0-9_-]+", unescape(value))
            if link:
                event["url"] = link.group(0)
    return calendar


def main():
    out = Path("luma.js")
    fetched_at = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    calendars = []
    events = {}
    for entry in CALENDARS:
        parsed = parse(fetch(FEED.format(entry["id"])))
        calendars.append({
            "id": entry["id"],
            "name": parsed["name"],
            "communityId": entry["community"],
            "match": entry["match"],
            "found": entry["found"],
            "feed": FEED.format(entry["id"]),
            "eventCount": len(parsed["events"]),
        })
        for event in parsed["events"]:
            if "id" not in event or "startsAt" not in event:
                continue
            location = event.pop("location", "") or ""
            # Luma puts the event link here when the address is hidden.
            hidden = not location or location.startswith("http")
            if hidden:
                # The organiser hid the address; do not keep the point either.
                event.pop("geo", None)
            merged = events.setdefault(event["id"], dict(event, calendarIds=[],
                location=None if hidden else location, addressHidden=hidden))
            merged["calendarIds"].append(entry["id"])
        print(f"{entry['id']}  {parsed['name']}: {len(parsed['events'])} events", file=sys.stderr)

    ordered = sorted(events.values(), key=lambda e: e["startsAt"])
    payload = {
        "fetchedAt": fetched_at,
        "source": "Public Luma iCal feeds. Regenerate with python3 scripts/import-luma.py",
        "calendars": calendars,
        "notFound": NOT_FOUND,
        "events": ordered,
    }
    out.write_text(
        "/* Generated by scripts/import-luma.py from public Luma iCal feeds. Do not edit by hand. */\n"
        "window.SAME_ROOM_LUMA = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n"
    )
    print(f"{len(ordered)} unique events from {len(calendars)} calendars -> {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
